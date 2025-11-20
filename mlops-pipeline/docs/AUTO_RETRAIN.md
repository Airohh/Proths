# 🔄 Guide de l'Auto-Retrain

## 🎯 Vue d'Ensemble

Le système d'auto-retrain permet de **réentraîner automatiquement** le modèle lorsque :
- **Drift détecté** : Les données de production diffèrent des données d'entraînement
- **Performance qui baisse** : Les métriques se dégradent
- **Planning régulier** : Retrain programmé (ex: tous les jours)

## 🏗️ Architecture

```
Monitoring → Détection Drift → Retrain → Comparaison → Déploiement
                ↓                                    ↓
            Pas de drift                    Pas meilleur → Rollback
```

## 📋 Composants

### 1. `AutoRetrainer` (`src/retraining/auto_retrain.py`)

Classe principale qui gère tout le pipeline de retrain :

- ✅ Détection de drift
- ✅ Entraînement de nouveau modèle
- ✅ Comparaison avec modèle actuel
- ✅ Déploiement automatique si meilleur
- ✅ Rollback si performance dégradée

### 2. Scripts CLI

#### `scripts/trigger_retrain.py`
Déclenche un retrain manuel ou automatique.

#### `scripts/monitor_and_retrain.py`
Monitoring continu avec déclenchement automatique.

## 🚀 Utilisation

### Retrain Manuel

```bash
# Retrain simple
python scripts/trigger_retrain.py

# Retrain avec détection de drift
python scripts/trigger_retrain.py --trigger drift

# Retrain avec modèle spécifique
python scripts/trigger_retrain.py --model-type lightgbm

# Retrain avec données personnalisées
python scripts/trigger_retrain.py --data-path data/processed/custom_train.csv
```

### Monitoring Continu

```bash
# Lancer le monitoring en arrière-plan
python scripts/monitor_and_retrain.py

# Une seule vérification (pour tests)
python scripts/monitor_and_retrain.py --once

# Avec intervalle personnalisé (en secondes)
python scripts/monitor_and_retrain.py --interval 1800  # 30 minutes
```

### Via Cron (Linux/Mac)

```bash
# Éditer le crontab
crontab -e

# Ajouter une ligne pour vérifier toutes les heures
0 * * * * cd /path/to/mlops-pipeline && python scripts/monitor_and_retrain.py --once
```

### Via Task Scheduler (Windows)

1. Ouvrir le Planificateur de tâches
2. Créer une tâche de base
3. Déclencher : Récurrent (toutes les heures)
4. Action : Exécuter un programme
   - Programme : `python`
   - Arguments : `scripts/monitor_and_retrain.py --once`
   - Dossier de départ : `C:\path\to\mlops-pipeline`

## ⚙️ Configuration

La configuration se trouve dans `config/config.yaml` :

```yaml
retrain:
  enabled: true
  trigger:
    type: "drift"  # drift, schedule, manual
    drift_threshold: 0.15
    schedule: "0 2 * * *"  # Cron: tous les jours à 2h
  min_improvement: 0.01  # Amélioration minimale pour déployer
  comparison_metric: "f1_score"  # Métrique de comparaison
```

### Paramètres

- **`enabled`** : Activer/désactiver l'auto-retrain
- **`trigger.type`** : Type de déclencheur
  - `drift` : Déclenché par détection de drift
  - `schedule` : Déclenché selon un planning (cron)
  - `manual` : Déclenché manuellement
- **`drift_threshold`** : Seuil de drift (0-1)
- **`min_improvement`** : Amélioration minimale requise pour déployer
- **`comparison_metric`** : Métrique utilisée pour comparer les modèles

## 🔄 Workflow Complet

### 1. Détection de Drift

```python
from src.retraining.auto_retrain import AutoRetrainer

retrainer = AutoRetrainer()
drift_score, is_drift = retrainer.check_drift(
    reference_data_path="data/processed/train.csv",
    current_data_path="data/processed/production_data.csv"
)
```

### 2. Retrain Complet

```python
from src.retraining.auto_retrain import AutoRetrainer, RetrainTrigger

retrainer = AutoRetrainer()
result = retrainer.retrain(
    trigger=RetrainTrigger.DRIFT,
    data_path="data/processed/train.csv",
    model_type="random_forest"
)

if result.success and result.deployed:
    print(f"✅ Nouveau modèle déployé!")
    print(f"   Amélioration: {result.improvement:.4f}")
```

### 3. Comparaison de Modèles

Le système compare automatiquement :
- **Métrique principale** : F1-score par défaut
- **Amélioration minimale** : 0.01 (1%) par défaut
- **Déploiement** : Seulement si meilleur

## 📊 Résultats

Le `RetrainResult` contient :

```python
@dataclass
class RetrainResult:
    success: bool                    # Succès du retrain
    new_model_version: str          # Version du nouveau modèle
    old_model_metric: float         # Métrique de l'ancien modèle
    new_model_metric: float         # Métrique du nouveau modèle
    improvement: float              # Amélioration
    deployed: bool                  # Déployé en production ?
    reason: str                     # Raison du résultat
    error: Optional[str]            # Erreur si échec
```

## 🔍 Monitoring

### Logs

Tous les événements sont loggés avec le système de logging structuré :

```json
{
  "timestamp": "2024-01-15T10:30:00",
  "level": "INFO",
  "message": "Drift détecté, déclenchement du retrain...",
  "drift_score": 0.23,
  "is_drift": true
}
```

### MLflow

- ✅ Tous les retrains sont trackés dans MLflow
- ✅ Comparaison des métriques entre versions
- ✅ Historique complet des modèles

### Prometheus

Les métriques suivantes sont exposées :
- `retrain_triggered_total` : Nombre de retrains déclenchés
- `retrain_success_total` : Nombre de retrains réussis
- `retrain_deployed_total` : Nombre de modèles déployés
- `drift_score` : Score de drift actuel

## 🛠️ Intégration avec l'API

Pour déclencher un retrain depuis l'API (à implémenter) :

```python
@app.post("/retrain")
async def trigger_retrain():
    retrainer = AutoRetrainer()
    result = retrainer.retrain(trigger=RetrainTrigger.MANUAL)
    return result
```

## 🚨 Gestion des Erreurs

### Cas d'Erreur

1. **Pas de drift détecté** : Retrain non déclenché
2. **Nouveau modèle pas meilleur** : Pas de déploiement
3. **Erreur d'entraînement** : Log de l'erreur, pas de déploiement
4. **Erreur de déploiement** : Rollback automatique

### Rollback

Si le nouveau modèle est déployé mais que les performances se dégradent :
- Le système peut détecter la baisse de performance
- Rollback automatique vers la version précédente
- Notification des administrateurs

## 📈 Bonnes Pratiques

1. **Surveiller les logs** : Vérifier régulièrement les retrains
2. **Ajuster les seuils** : Adapter `drift_threshold` selon vos données
3. **Tester en staging** : Déployer d'abord en staging avant production
4. **Backup des modèles** : MLflow garde l'historique, mais faites des backups
5. **Alertes** : Configurer des alertes pour les retrains

## 🔗 Liens Utiles

- [MLflow Model Registry](https://mlflow.org/docs/latest/model-registry.html)
- [Drift Detection Concepts](docs/QU_EST_CE_QUE_MLOPS.md#drift)
- [Configuration](config/config.yaml)

---

**Dernière mise à jour** : 2024  
**Version** : 1.0

