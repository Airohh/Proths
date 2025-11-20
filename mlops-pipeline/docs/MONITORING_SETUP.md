# 📊 Guide de Configuration du Monitoring

## Vue d'Ensemble

Ce guide explique comment configurer et utiliser le monitoring complet avec Prometheus et Grafana.

## 🏗️ Architecture

```
API FastAPI → Métriques Prometheus → Prometheus → Grafana
     ↓              ↓                    ↓           ↓
  /metrics    Expose métriques    Collecte      Visualisation
```

## 📋 Composants

### 1. Prometheus

**Rôle** : Collecte et stocke les métriques

**Configuration** : `docker/prometheus/prometheus.yml`

**Métriques collectées** :
- `api_requests_total` : Nombre total de requêtes
- `api_request_latency_seconds` : Latence des requêtes
- `predictions_total` : Nombre de prédictions
- `prediction_errors_total` : Erreurs de prédiction
- `model_loaded` : État du modèle (1 = chargé, 0 = non chargé)

### 2. Grafana

**Rôle** : Visualisation des métriques

**Dashboards** :
- Dashboard principal : `MLOps Pipeline - Monitoring`
- Panneaux :
  - API Requests Rate
  - API Request Latency (p50, p95)
  - Predictions Total
  - Prediction Errors
  - Model Status
  - Error Rate
  - Request Status Codes

### 3. Alertes Prometheus

**Fichier** : `docker/prometheus/alerts.yml`

**Alertes configurées** :

1. **HighErrorRate** : Taux d'erreur > 5%
2. **ModelNotLoaded** : Modèle non chargé
3. **HighLatency** : Latence P95 > 1s
4. **NoPredictions** : Aucune prédiction depuis 10 minutes

## 🚀 Installation

### 1. Lancer les services

```bash
docker-compose up -d
```

### 2. Vérifier que tout fonctionne

```bash
# Prometheus
curl http://localhost:9090/-/healthy

# Grafana
curl http://localhost:3000/api/health
```

### 3. Accéder aux interfaces

- **Prometheus** : http://localhost:9090
- **Grafana** : http://localhost:3000
  - Login : `admin`
  - Password : `admin` (changé au premier login)

## 📊 Utilisation

### Prometheus

#### Requêtes utiles

```promql
# Taux de requêtes par seconde
rate(api_requests_total[5m])

# Latence P95
histogram_quantile(0.95, rate(api_request_latency_seconds_bucket[5m]))

# Taux d'erreur
rate(prediction_errors_total[5m]) / rate(predictions_total[5m]) * 100

# État du modèle
model_loaded
```

#### Vérifier les alertes

1. Aller sur http://localhost:9090/alerts
2. Voir l'état des alertes (pending, firing)

### Grafana

#### Accéder au dashboard

1. Se connecter à Grafana
2. Aller dans "Dashboards"
3. Le dashboard "MLOps Pipeline - Monitoring" devrait être disponible

#### Personnaliser le dashboard

1. Cliquer sur "Edit" sur le dashboard
2. Modifier les panneaux selon vos besoins
3. Sauvegarder

## 🔔 Alertes

### Configuration

Les alertes sont définies dans `docker/prometheus/alerts.yml`.

### Recevoir des alertes

Pour recevoir des alertes, vous devez configurer un Alertmanager :

1. **Email** : Envoyer des emails
2. **Slack** : Notifications Slack
3. **PagerDuty** : Alertes critiques
4. **Webhook** : Appel API personnalisé

### Exemple : Configuration Alertmanager

```yaml
# docker/alertmanager/config.yml
route:
  receiver: 'default'
  routes:
    - match:
        severity: critical
      receiver: 'critical-alerts'

receivers:
  - name: 'default'
    email_configs:
      - to: 'team@example.com'
        from: 'alerts@example.com'
        smarthost: 'smtp.example.com:587'
  
  - name: 'critical-alerts'
    slack_configs:
      - api_url: 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL'
        channel: '#alerts'
```

## 🛠️ Dépannage

### Prometheus ne collecte pas les métriques

1. Vérifier que l'API expose `/metrics` :
   ```bash
   curl http://localhost:8000/metrics
   ```

2. Vérifier la configuration dans Prometheus :
   - Aller sur http://localhost:9090/targets
   - Vérifier que le target "mlops-api" est "UP"

### Grafana ne montre pas de données

1. Vérifier la datasource Prometheus :
   - Settings → Data Sources
   - Vérifier que Prometheus est configuré et testé

2. Vérifier que Prometheus collecte des données :
   - Aller sur http://localhost:9090
   - Taper une requête : `api_requests_total`

### Alertes ne se déclenchent pas

1. Vérifier la syntaxe des règles :
   ```bash
   promtool check rules docker/prometheus/alerts.yml
   ```

2. Vérifier dans Prometheus :
   - Aller sur http://localhost:9090/alerts
   - Voir l'état des alertes

## 📈 Métriques Personnalisées

### Ajouter une nouvelle métrique

Dans `src/inference/api.py` :

```python
from prometheus_client import Counter, Histogram, Gauge

# Nouvelle métrique
CUSTOM_METRIC = Counter('custom_metric_total', 'Description')

# Incrémenter
CUSTOM_METRIC.inc()
```

### Visualiser dans Grafana

1. Créer un nouveau panneau
2. Utiliser la requête PromQL : `rate(custom_metric_total[5m])`

## 🎯 Bonnes Pratiques

1. **Surveiller les métriques clés** :
   - Taux d'erreur
   - Latence
   - Throughput

2. **Configurer des alertes pertinentes** :
   - Pas trop d'alertes (fatigue d'alerte)
   - Seuils réalistes
   - Actions claires

3. **Retention des données** :
   - Configurer la rétention Prometheus
   - Utiliser TimescaleDB pour long terme

4. **Dashboards** :
   - Un dashboard par équipe/service
   - Métriques business + techniques

## 📚 Ressources

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [PromQL Guide](https://prometheus.io/docs/prometheus/latest/querying/basics/)

---

**Dernière mise à jour** : 2024-11-18

