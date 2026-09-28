# Architecture

## Services (docker-compose.yml)

| Service | Image | Rôle | Port |
|---|---|---|---|
| `mlflow` | `docker/Dockerfile.mlflow` | Tracking et registry. Métadonnées SQLite, artefacts servis en HTTP (`--serve-artifacts`) | 5000 |
| `trainer` | `docker/Dockerfile` (profil `setup`) | Tâche ponctuelle : télécharge AG News, entraîne le premier champion | – |
| `api` | `docker/Dockerfile` | Prédictions, feedback, rechargement du champion | 8000 |
| `monitor` | `docker/Dockerfile` | Drift, précision live, retrain, `/metrics` | 8001 (interne) |
| `prometheus` | `prom/prometheus:v2.53.0` | Collecte les métriques de `api` et `monitor`, évalue les alertes | 9090 |
| `grafana` | `grafana/grafana:11.1.0` | Dashboard provisionné `Proths · boucle MLOps` | 3000 |

`api` et `monitor` partagent le volume `app-data` : données préparées et journal
`predictions.db`. Seul MLflow connaît les modèles.

## Cycle de vie d'une prédiction

1. `POST /predict` : le `Pipeline` du champion calcule `predict_proba` sur le texte brut.
2. La ligne est écrite dans `predictions` (id, texte, classe, confiance, version du modèle).
3. L'appelant reçoit un `prediction_id`.
4. Plus tard, `POST /feedback {prediction_id, label}` complète la ligne (`true_label`).

## Un passage du monitor (toutes les 20 s dans Compose)

1. Il récupère le champion depuis l'alias et le met en cache par version.
2. Il lit les 500 dernières prédictions **de cette version**. Après une promotion, la
   fenêtre repart donc de zéro : pas de verdict tant qu'elle compte moins de 200
   prédictions (exporté comme NaN, affiché « en attente » dans Grafana).
3. Il calcule le rapport de drift contre `reference_profile.json`, embarqué avec la version.
4. Il calcule la précision live sur les prédictions labellisées de cette version.
5. Il cherche un déclencheur : drift, ou précision live inférieure à l'accuracy holdout
   moins 0,05.
6. Il réentraîne si les trois conditions suivantes sont réunies :
   - un déclencheur est présent ;
   - au moins 200 nouveaux labels sont arrivés depuis le dernier entraînement (lu dans
     MLflow) ;
   - le cooldown est écoulé.

   Le retrain appelle `train_and_register`, qui entraîne le candidat, puis évalue
   candidat **et** champion sur le holdout dans le même run MLflow. Il pose l'alias
   `@champion` si le gain atteint le seuil ; sinon, il tague la version avec la raison
   du rejet.
7. Après une promotion : `POST /model/reload` sur l'API. Si l'appel échoue, l'API voit
   quand même l'alias changer au prochain poll.

## Ce qui est loggé dans MLflow à chaque entraînement

- **Tags** : `kind=training`, `trigger` (manual / drift / performance), `decision`
  (promoted / rejected).
- **Paramètres** : type de modèle, taille du train, nombre de labels de feedback, version
  du champion au moment du duel.
- **Métriques** :
  - `holdout_*` pour le candidat ;
  - `champion_holdout_*` pour le champion ;
  - `delta_f1_macro` ;
  - `fit_seconds`.
- **Artefacts** : le `Pipeline` complet et `reference_profile.json`.
- **Tag de version** : `decision`, qui donne la raison lisible de la promotion ou du rejet.

## Métriques Prometheus

| Source | Métrique | Sens |
|---|---|---|
| api | `predictions_total{label}` | Prédictions servies par classe |
| api | `prediction_confidence` | Histogramme de la confiance max |
| api | `feedback_total{correct}` | Labels reçus, justes ou non |
| api | `model_version`, `model_loaded` | Version réellement servie |
| monitor | `drift_psi`, `drift_ks_stat`, `drift_chi2_pvalue`, `drift_detected` | Rapport de drift |
| monitor | `prediction_class_share{label}` | Mix de la fenêtre |
| monitor | `live_accuracy`, `live_labeled` | Performance avec labels |
| monitor | `champion_version`, `champion_holdout_f1` | État du registry |
| monitor | `retrain_total{trigger,decision}` | Historique des retrains |

Alertes (`docker/prometheus/alerts.yml`) : `DataDrift`, `LiveAccuracyDrop`,
`CandidateRejected`, `ModelNotLoaded`, `HighLatency`, `PredictionErrors`.
