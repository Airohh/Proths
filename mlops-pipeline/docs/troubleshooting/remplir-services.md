# 📊 Remplir les Services avec des Données

## 🎯 Problème

Les services (Grafana, Prometheus, MLflow) sont vides car **aucune donnée n'a été générée**.

## ✅ Solution : Générer des Données

### Étape 1 : Entraîner un Modèle (Pour MLflow)

Cela va créer des expériences et modèles dans MLflow :

```powershell
cd "C:\Users\Utilisateur\Desktop\4 mois\Prometheus - LLM\mlops-pipeline"
python src/training/train.py --model-type random_forest
```

**Résultat** :
- ✅ Expérience créée dans MLflow
- ✅ Modèle enregistré
- ✅ Métriques trackées

**Vérifier** : http://localhost:5000 → Vous devriez voir l'expérience "document-classification"

---

### Étape 2 : Lancer l'API (Pour Prometheus)

L'API expose les métriques que Prometheus collecte :

**Dans un NOUVEAU terminal PowerShell** :

```powershell
cd "C:\Users\Utilisateur\Desktop\4 mois\Prometheus - LLM\mlops-pipeline"
uvicorn src.inference.api:app --reload --port 8000
```

**Laisser le terminal ouvert**, puis :

1. **Tester l'API** :
   ```powershell
   # Test health check
   curl http://localhost:8000/health
   
   # Test prédiction
   curl -X POST "http://localhost:8000/predict" `
     -H "Content-Type: application/json" `
     -d '{\"text\": \"artificial intelligence machine learning\"}'
   ```

2. **Vérifier Prometheus** :
   - Aller sur http://localhost:9090
   - Dans la barre de recherche, taper : `api_requests_total`
   - Vous devriez voir des métriques

3. **Vérifier Grafana** :
   - Aller sur http://localhost:3000
   - Le dashboard devrait maintenant afficher des données

---

### Étape 3 : Générer du Trafic (Pour voir les Métriques)

**Option A : Script Python**

Créer un fichier `test_api.py` :

```python
import requests
import time

api_url = "http://localhost:8000"

# Générer 10 requêtes
for i in range(10):
    response = requests.post(
        f"{api_url}/predict",
        json={"text": f"test request {i}"}
    )
    print(f"Request {i+1}: {response.status_code}")
    time.sleep(1)
```

Exécuter :
```powershell
python test_api.py
```

**Option B : Boucle PowerShell**

```powershell
for ($i=1; $i -le 10; $i++) {
    Invoke-RestMethod -Uri "http://localhost:8000/predict" `
        -Method POST `
        -ContentType "application/json" `
        -Body '{"text": "artificial intelligence machine learning"}'
    Start-Sleep -Seconds 1
}
```

---

## 📋 Checklist Complète

### MLflow (Port 5000)

- [ ] Modèle entraîné : `python src/training/train.py`
- [ ] Accéder à http://localhost:5000
- [ ] Voir l'expérience "document-classification"
- [ ] Voir les runs avec métriques

### Prometheus (Port 9090)

- [ ] API lancée : `uvicorn src.inference.api:app --reload`
- [ ] Faire quelques requêtes à l'API
- [ ] Accéder à http://localhost:9090
- [ ] Vérifier Status → Targets → "mlops-api" est UP
- [ ] Chercher `api_requests_total` dans la barre de recherche

### Grafana (Port 3000)

- [ ] API lancée et générant du trafic
- [ ] Prometheus collecte des métriques
- [ ] Accéder à http://localhost:3000
- [ ] Se connecter (admin/admin)
- [ ] Aller dans Dashboards
- [ ] Ouvrir "MLOps Pipeline - Monitoring"
- [ ] Voir les graphiques avec données

---

## 🚀 Script Automatique

Pour tout faire d'un coup :

```powershell
# Terminal 1 - Entraîner modèle
cd "C:\Users\Utilisateur\Desktop\4 mois\Prometheus - LLM\mlops-pipeline"
python src/training/train.py --model-type random_forest

# Terminal 2 - Lancer API
cd "C:\Users\Utilisateur\Desktop\4 mois\Prometheus - LLM\mlops-pipeline"
uvicorn src.inference.api:app --reload --port 8000

# Terminal 3 - Générer du trafic
for ($i=1; $i -le 20; $i++) {
    Invoke-RestMethod -Uri "http://localhost:8000/predict" `
        -Method POST `
        -ContentType "application/json" `
        -Body '{"text": "artificial intelligence machine learning"}'
    Start-Sleep -Seconds 2
}
```

---

## 🎯 Ordre Recommandé

1. **Entraîner un modèle** → Remplit MLflow
2. **Lancer l'API** → Expose les métriques
3. **Faire des requêtes** → Génère des données pour Prometheus
4. **Vérifier Grafana** → Visualise les métriques

---

## 💡 Astuce

**Pour voir les données en temps réel dans Grafana** :
- Rafraîchir automatiquement : Cliquer sur l'icône de rafraîchissement en haut à droite
- Choisir "Last 5 minutes" ou "Last 1 hour"
- Les graphiques se mettront à jour automatiquement

---

**Une fois ces étapes faites, tous les services auront des données !** 🎉

