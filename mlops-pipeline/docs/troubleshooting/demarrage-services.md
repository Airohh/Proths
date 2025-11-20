# 🚀 Démarrage des Services

## Services Disponibles

### 1. MLflow UI (Port 5000)

**Lancer** :
```powershell
cd mlops-pipeline
mlflow ui --port 5000
```

**Accéder** : http://localhost:5000

### 2. API FastAPI (Port 8000)

**Lancer** :
```powershell
cd mlops-pipeline
uvicorn src.inference.api:app --reload --port 8000
```

**Accéder** : 
- API : http://localhost:8000
- Docs : http://localhost:8000/docs

### 3. Services Docker

**Lancer** :
```powershell
cd mlops-pipeline
docker-compose up -d
```

**Services** :
- Prometheus : http://localhost:9090
- Grafana : http://localhost:3000 (admin/admin)
- MLflow : http://localhost:5000
- TimescaleDB : localhost:5432

## Vérifier que les Services Tournent

```powershell
# Vérifier les ports
netstat -an | findstr "5000 8000 9090 3000"

# Vérifier Docker
docker-compose ps
```

## Problèmes Courants

### Port déjà utilisé

```powershell
# Trouver le processus
netstat -ano | findstr :8000

# Tuer le processus
taskkill /PID <PID> /F
```

### Service ne démarre pas

1. Vérifier les logs
2. Vérifier les dépendances
3. Vérifier la configuration

