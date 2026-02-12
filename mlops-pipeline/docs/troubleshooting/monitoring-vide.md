# 🔍 Monitoring Vide - Guide de Résolution

## Problème

Vous pouvez accéder à Prometheus (http://localhost:9090) et Grafana (http://localhost:3000) mais **ils n'affichent aucune donnée**.

## Solution : 3 Étapes

### Étape 1 : Lancer l'API FastAPI

**L'API doit être lancée** pour que Prometheus puisse collecter les métriques.

**Dans un terminal PowerShell** :

```powershell
cd "C:\Users\Utilisateur\Desktop\4 mois\Prometheus - LLM\mlops-pipeline"
uvicorn src.inference.api:app --reload --port 8000
```

**Laisser ce terminal ouvert** - l'API doit tourner en continu.

**Vérifier** : Ouvrir http://localhost:8000/docs dans votre navigateur. Vous devriez voir la documentation Swagger.

---

### Étape 2 : Vérifier que Prometheus Scrape l'API

1. **Ouvrir Prometheus** : http://localhost:9090

2. **Vérifier les Targets** :
   - Aller dans **Status → Targets**
   - Chercher le target `mlops-api`
   - Il doit être **UP**

3. **Si le target est DOWN** :
   - Vérifier que l'API est bien lancée (étape 1)
   - Vérifier que l'endpoint `/metrics` fonctionne : http://localhost:8000/metrics
   - Vous devriez voir des métriques au format Prometheus

4. **Tester manuellement** :
   ```powershell
   # Test de l'endpoint /metrics
   curl http://localhost:8000/metrics
   ```

---

### Étape 3 : Générer du Trafic

**Prometheus ne peut collecter que des métriques qui existent**. Si aucune requête n'a été faite à l'API, il n'y a pas de métriques.

**Option A : Script Python (Recommandé)**

```powershell
cd "C:\Users\Utilisateur\Desktop\4 mois\Prometheus - LLM\mlops-pipeline"
python scripts/generate_traffic.py
```

**Option B : Requêtes Manuelles**

```powershell
# Faire 10 requêtes
for ($i=1; $i -le 10; $i++) {
    Invoke-RestMethod -Uri "http://localhost:8000/predict" `
        -Method POST `
        -ContentType "application/json" `
        -Body '{"text": "artificial intelligence machine learning"}'
    Start-Sleep -Seconds 1
}
```

**Option C : Via Swagger UI**

1. Ouvrir http://localhost:8000/docs
2. Cliquer sur `/predict` → **Try it out**
3. Entrer un texte : `"artificial intelligence machine learning"`
4. Cliquer sur **Execute**
5. Répéter plusieurs fois

---

## 🔍 Vérification dans Prometheus

Après avoir généré du trafic :

1. **Ouvrir Prometheus** : http://localhost:9090

2. **Chercher des métriques** :
   - Dans la barre de recherche, taper : `api_requests_total`
   - Cliquer sur **Execute**
   - Vous devriez voir des résultats

3. **Autres métriques à vérifier** :
   - `predictions_total` - Nombre de prédictions
   - `api_request_latency_seconds` - Latence des requêtes
   - `model_loaded` - État du modèle (1 = chargé, 0 = non chargé)

---

## Vérification dans Grafana

1. **Ouvrir Grafana** : http://localhost:3000
   - Login : `admin`
   - Password : `admin`

2. **Aller dans Dashboards** :
   - Cliquer sur **Dashboards** (icône carrés) dans le menu de gauche
   - Ouvrir **"MLOps Pipeline - Monitoring"**

3. **Si le dashboard est vide** :
   - Vérifier que Prometheus collecte des données (étape précédente)
   - Vérifier la datasource Prometheus :
     - **Configuration** (icône engrenage) → **Data sources**
     - Cliquer sur **Prometheus**
     - Tester la connexion avec **Test**

4. **Rafraîchir le dashboard** :
   - Cliquer sur l'icône de rafraîchissement en haut à droite
   - Choisir **"Last 5 minutes"** ou **"Last 1 hour"**

---

## 🐛 Problèmes Courants

### Problème 1 : Target "mlops-api" est DOWN dans Prometheus

**Cause** : L'API n'est pas accessible depuis le conteneur Docker.

**Solution** :
- Vérifier que l'API est lancée sur `localhost:8000`
- Vérifier la configuration Prometheus : `docker/prometheus/prometheus.yml`
- Le target doit être : `host.docker.internal:8000` (pour Windows/Mac avec Docker Desktop)

### Problème 2 : L'endpoint /metrics retourne 404

**Cause** : L'endpoint `/metrics` n'est pas configuré dans l'API.

**Vérification** :
```powershell
curl http://localhost:8000/metrics
```

**Solution** : L'endpoint est déjà configuré dans `src/inference/api.py`. Si vous obtenez 404, vérifiez que vous utilisez la bonne version de l'API.

### Problème 3 : Prometheus collecte mais Grafana est vide

**Cause** : La datasource Prometheus n'est pas configurée correctement.

**Solution** :
1. Dans Grafana : **Configuration** → **Data sources**
2. Cliquer sur **Prometheus**
3. URL : `http://prometheus:9090` (depuis Docker) ou `http://localhost:9090` (si Grafana est hors Docker)
4. Cliquer sur **Save & Test**

### Problème 4 : Pas de métriques même après des requêtes

**Cause** : Le modèle n'est pas chargé ou les métriques ne sont pas incrémentées.

**Vérification** :
```powershell
# Vérifier l'état du modèle
curl http://localhost:8000/model/info

# Vérifier les métriques
curl http://localhost:8000/metrics | Select-String "model_loaded"
```

**Solution** :
- Entraîner un modèle : `python src/training/train.py`
- Redémarrer l'API pour charger le modèle

---

## Checklist

- [ ] Docker Desktop est lancé
- [ ] Services Docker sont lancés : `docker-compose ps` (Prometheus, Grafana doivent être UP)
- [ ] API FastAPI est lancée : `uvicorn src.inference.api:app --reload`
- [ ] Endpoint `/metrics` accessible : http://localhost:8000/metrics
- [ ] Target `mlops-api` est UP dans Prometheus (Status → Targets)
- [ ] Du trafic a été généré (requêtes à l'API)
- [ ] Métriques visibles dans Prometheus (chercher `api_requests_total`)
- [ ] Datasource Prometheus configurée dans Grafana
- [ ] Dashboard Grafana rafraîchi

---

## Script de Vérification

Créer un fichier `check_monitoring.ps1` :

```powershell
Write-Host "Verification du monitoring..." -ForegroundColor Cyan

# 1. API
Write-Host "`n1. API (port 8000):" -ForegroundColor Yellow
$api = Test-NetConnection -ComputerName localhost -Port 8000 -InformationLevel Quiet
if ($api) {
    Write-Host "   [OK] API accessible" -ForegroundColor Green
    try {
        $metrics = Invoke-WebRequest -Uri "http://localhost:8000/metrics" -UseBasicParsing
        Write-Host "   [OK] Endpoint /metrics accessible" -ForegroundColor Green
    } catch {
        Write-Host "   [ERROR] /metrics non accessible" -ForegroundColor Red
    }
} else {
    Write-Host "   [ERROR] API non accessible" -ForegroundColor Red
    Write-Host "   Lancer: uvicorn src.inference.api:app --reload" -ForegroundColor Yellow
}

# 2. Prometheus
Write-Host "`n2. Prometheus (port 9090):" -ForegroundColor Yellow
$prom = Test-NetConnection -ComputerName localhost -Port 9090 -InformationLevel Quiet
if ($prom) {
    Write-Host "   [OK] Prometheus accessible" -ForegroundColor Green
    Write-Host "   URL: http://localhost:9090" -ForegroundColor Cyan
} else {
    Write-Host "   [ERROR] Prometheus non accessible" -ForegroundColor Red
    Write-Host "   Lancer: docker-compose up -d" -ForegroundColor Yellow
}

# 3. Grafana
Write-Host "`n3. Grafana (port 3000):" -ForegroundColor Yellow
$graf = Test-NetConnection -ComputerName localhost -Port 3000 -InformationLevel Quiet
if ($graf) {
    Write-Host "   [OK] Grafana accessible" -ForegroundColor Green
    Write-Host "   URL: http://localhost:3000 (admin/admin)" -ForegroundColor Cyan
} else {
    Write-Host "   [ERROR] Grafana non accessible" -ForegroundColor Red
    Write-Host "   Lancer: docker-compose up -d" -ForegroundColor Yellow
}

Write-Host "`n[INFO] Pour generer du trafic:" -ForegroundColor Cyan
Write-Host "   python scripts/generate_traffic.py" -ForegroundColor White
```

Exécuter :
```powershell
.\check_monitoring.ps1
```

---

## Résumé

**Causes** : API non lancée, aucune requête faite, ou modèle non chargé.

**Solution** :
1. Lancer l'API : `uvicorn src.inference.api:app --reload`
2. Générer du trafic : `python scripts/generate_traffic.py`
3. Vérifier Prometheus (localhost:9090) et Grafana (localhost:3000)

