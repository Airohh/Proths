# 📊 Métriques Prometheus Disponibles

## 🎯 Métriques Exposées par l'API

L'API FastAPI expose plusieurs métriques Prometheus via l'endpoint `/metrics` :

### 1. `api_requests_total` (Counter)
**Description** : Nombre total de requêtes API

**Labels** :
- `method` : Méthode HTTP (GET, POST, etc.)
- `endpoint` : Chemin de l'endpoint (/predict, /health, etc.)
- `status` : Code de statut HTTP (200, 404, 500, etc.)

**Exemple** :
```
api_requests_total{endpoint="/predict", method="POST", status="200"} 23
```

**Utilisation dans Prometheus** :
```
# Toutes les requêtes
api_requests_total

# Requêtes par endpoint
sum(api_requests_total) by (endpoint)

# Taux de requêtes par seconde
rate(api_requests_total[5m])
```

---

### 2. `api_request_latency_seconds` (Histogram)
**Description** : Latence des requêtes API en secondes

**Labels** :
- `method` : Méthode HTTP
- `endpoint` : Chemin de l'endpoint

**Buckets** : 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10

**Exemple** :
```
api_request_latency_seconds_bucket{endpoint="/predict", method="POST", le="0.1"} 20
api_request_latency_seconds_sum{endpoint="/predict", method="POST"} 0.5
api_request_latency_seconds_count{endpoint="/predict", method="POST"} 23
```

**Utilisation dans Prometheus** :
```
# Latence moyenne
rate(api_request_latency_seconds_sum[5m]) / rate(api_request_latency_seconds_count[5m])

# P95 (95ème percentile)
histogram_quantile(0.95, rate(api_request_latency_seconds_bucket[5m]))

# P99 (99ème percentile)
histogram_quantile(0.99, rate(api_request_latency_seconds_bucket[5m]))
```

---

### 3. `predictions_total` (Counter)
**Description** : Nombre total de prédictions effectuées

**Labels** :
- `model_type` : Type de modèle (random_forest, lightgbm, etc.)

**Exemple** :
```
predictions_total{model_type="random_forest"} 23
```

**Utilisation dans Prometheus** :
```
# Toutes les prédictions
predictions_total

# Taux de prédictions par seconde
rate(predictions_total[5m])
```

---

### 4. `prediction_errors_total` (Counter)
**Description** : Nombre total d'erreurs de prédiction

**Labels** :
- `error_type` : Type d'erreur (model_not_loaded, validation_error, prediction_error, etc.)

**Exemple** :
```
prediction_errors_total{error_type="model_not_loaded"} 0
prediction_errors_total{error_type="validation_error"} 0
```

**Utilisation dans Prometheus** :
```
# Toutes les erreurs
sum(prediction_errors_total)

# Erreurs par type
sum(prediction_errors_total) by (error_type)

# Taux d'erreur
rate(prediction_errors_total[5m])
```

---

### 5. `model_loaded` (Gauge)
**Description** : État du modèle (1 = chargé, 0 = non chargé)

**Exemple** :
```
model_loaded 1
```

**Utilisation dans Prometheus** :
```
# État du modèle
model_loaded

# Alerte si modèle non chargé
model_loaded == 0
```

---

## 🔍 Requêtes Prometheus Utiles

### Taux de Requêtes par Seconde
```promql
rate(api_requests_total[5m])
```

### Latence P95
```promql
histogram_quantile(0.95, rate(api_request_latency_seconds_bucket[5m]))
```

### Taux d'Erreur
```promql
sum(rate(prediction_errors_total[5m])) / sum(rate(api_requests_total[5m]))
```

### Requêtes par Endpoint
```promql
sum(api_requests_total) by (endpoint)
```

### Prédictions par Seconde
```promql
rate(predictions_total[5m])
```

---

## 📊 Vérifier les Métriques dans Prometheus

1. **Ouvrir Prometheus** : http://localhost:9090

2. **Chercher une métrique** :
   - Dans la barre de recherche, taper : `api_requests_total`
   - Cliquer sur **Execute**
   - Vous devriez voir les résultats

3. **Voir toutes les métriques disponibles** :
   - Aller dans **Status → Targets**
   - Cliquer sur le target `mlops-api`
   - Cliquer sur **Show more** pour voir toutes les métriques

4. **Tester les requêtes** :
   - Copier-coller les requêtes PromQL ci-dessus
   - Voir les résultats en graphique ou en tableau

---

## 🎨 Visualiser dans Grafana

1. **Ouvrir Grafana** : http://localhost:3000

2. **Aller dans le Dashboard** :
   - **Dashboards** → **"MLOps Pipeline - Monitoring"**

3. **Les panneaux affichent** :
   - **API Requests** : `sum(rate(api_requests_total[5m]))`
   - **Latency (P95)** : `histogram_quantile(0.95, rate(api_request_latency_seconds_bucket[5m]))`
   - **Predictions** : `sum(rate(predictions_total[5m]))`
   - **Errors** : `sum(rate(prediction_errors_total[5m]))`
   - **Model Status** : `model_loaded`

4. **Si le dashboard est vide** :
   - Vérifier que Prometheus collecte des données
   - Vérifier la datasource Prometheus (Configuration → Data sources)
   - Rafraîchir le dashboard

---

## 🐛 Problèmes Courants

### Problème : Seulement `api_requests_total` visible

**Cause** : Pas assez de trafic ou métriques non incrémentées.

**Solution** :
1. Générer plus de trafic : `python scripts/generate_traffic.py --requests 50`
2. Vérifier que le modèle est chargé : `curl http://localhost:8000/model/info`
3. Vérifier l'endpoint `/metrics` : `curl http://localhost:8000/metrics`

### Problème : `predictions_total` est à 0

**Cause** : Le modèle n'est pas chargé ou les prédictions échouent.

**Solution** :
1. Entraîner un modèle : `python src/training/train.py`
2. Redémarrer l'API pour charger le modèle
3. Vérifier : `curl http://localhost:8000/model/info`

### Problème : `api_request_latency_seconds` n'apparaît pas

**Cause** : Les métriques d'histogramme ont un format différent.

**Solution** :
- Chercher : `api_request_latency_seconds_bucket`
- Ou : `api_request_latency_seconds_sum`
- Ou : `api_request_latency_seconds_count`

---

## ✅ Checklist

- [ ] API lancée : `uvicorn src.inference.api:app --reload`
- [ ] Endpoint `/metrics` accessible : http://localhost:8000/metrics
- [ ] Prometheus scrape l'API : Status → Targets → `mlops-api` est UP
- [ ] Trafic généré : `python scripts/generate_traffic.py`
- [ ] Métriques visibles dans Prometheus : Chercher `api_requests_total`
- [ ] Dashboard Grafana configuré et rafraîchi

---

**Une fois toutes les métriques visibles, le monitoring est complet !** 🎉

