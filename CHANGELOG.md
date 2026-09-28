# Changelog

## 2.0.0 (septembre 2026)

Refonte de la boucle : corrections de fond et observabilité ML.

**Corrigé**
- *Train/serve skew* : l'API vectorisait le texte brut alors que l'entraînement le
  nettoyait. Nettoyage, TF-IDF et modèle forment désormais un seul `Pipeline`.
- *Vectorizer orphelin* : un retrain réécrivait `vectorizer.pkl` même quand le candidat
  était rejeté. Le champion pouvait donc être servi avec le vocabulaire d'un autre modèle,
  sans aucune erreur. Le vocabulaire est maintenant versionné avec le modèle.
- *Comparaison biaisée* : le F1 du champion venait de son propre run, celui du candidat
  d'un split contenant ses pseudo-labels. Les deux sont désormais évalués sur le même
  holdout, dans le même run.
- *Pseudo-labels* : le retrain utilisait les prédictions du modèle comme labels. Il
  utilise maintenant les vrais labels reçus par `POST /feedback`.
- Registry MLflow perdu à chaque redémarrage (SQLite hors volume) ; stages dépréciés
  remplacés par l'alias `@champion`.

**Ajouté**
- Endpoint `POST /feedback` et journal SQLite des prédictions.
- Drift statistique : PSI, KS et chi², avec un profil de référence par version de modèle.
- Service `monitor` : précision live, retrain automatique (cooldown, labels minimum) et
  métriques Prometheus.
- Dashboard Grafana orienté ML et alertes (`DataDrift`, `LiveAccuracyDrop`…).
- `make demo` (scénario complet, graphique), `make compare` (choix du modèle).
- CI : ruff, tests avec couverture, quality gate sur de vraies données, build Docker.

**Modifié**
- Modèle : régression logistique (F1 0,923) au lieu du Random Forest (F1 0,73).
- Repo aplati (`mlops-pipeline/` → racine), dépendances runtime et dev séparées, scripts
  et docs inutilisés retirés.

## 1.x

- AG News par défaut, `/predict` journalisé, drift sur moyennes TF-IDF, promotion par
  stage MLflow.
