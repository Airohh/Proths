# 📊 Dashboard Grafana - Guide d'Accès

## 🎯 Problème

Vous ne trouvez pas le dashboard dans Grafana.

## ✅ Solution : Accéder au Dashboard

### Méthode 1 : Via le Menu Dashboards (Recommandé)

1. **Ouvrir Grafana** : http://localhost:3000
   - Login : `admin`
   - Password : `admin`

2. **Aller dans Dashboards** :
   - Cliquer sur l'icône **Dashboards** (4 carrés) dans le menu de gauche
   - Ou : Menu → **Dashboards** → **Browse**

3. **Chercher le dashboard** :
   - Le dashboard s'appelle : **"MLOps Pipeline - Monitoring"**
   - Il devrait apparaître dans la liste
   - Si vous ne le voyez pas, cherchez dans la barre de recherche : `MLOps`

4. **Ouvrir le dashboard** :
   - Cliquer sur **"MLOps Pipeline - Monitoring"**
   - Le dashboard devrait s'ouvrir avec tous les graphiques

---

### Méthode 2 : Import Manuel (Si le dashboard n'apparaît pas)

1. **Ouvrir Grafana** : http://localhost:3000

2. **Importer le dashboard** :
   - Menu → **Dashboards** → **Import**
   - Cliquer sur **Upload JSON file**
   - Sélectionner : `docker/grafana/dashboards/mlops-dashboard.json`
   - Cliquer sur **Load**

3. **Configurer la datasource** :
   - Dans **Prometheus**, sélectionner **Prometheus** (ou créer la datasource si nécessaire)
   - Cliquer sur **Import**

---

### Méthode 3 : Créer la Datasource Prometheus (Si nécessaire)

1. **Ouvrir Grafana** : http://localhost:3000

2. **Aller dans Configuration** :
   - Menu → **Configuration** (icône engrenage) → **Data sources**

3. **Ajouter Prometheus** :
   - Cliquer sur **Add data source**
   - Sélectionner **Prometheus**

4. **Configurer** :
   - **URL** : `http://prometheus:9090` (depuis Docker) ou `http://localhost:9090` (si Grafana est hors Docker)
   - Cliquer sur **Save & Test**
   - Vous devriez voir : "Data source is working"

---

## 🔍 Vérifier que le Dashboard est Provisionné

### Vérifier les Logs Grafana

```powershell
docker-compose logs grafana | Select-String -Pattern "dashboard"
```

Vous devriez voir des messages indiquant que le dashboard est chargé.

### Redémarrer Grafana

Si le dashboard n'apparaît pas après l'import automatique :

```powershell
cd "C:\Users\Utilisateur\Desktop\4 mois\Prometheus - LLM\mlops-pipeline"
docker-compose restart grafana
```

Attendre 10-15 secondes, puis rafraîchir Grafana.

---

## 📋 Contenu du Dashboard

Le dashboard **"MLOps Pipeline - Monitoring"** contient :

1. **API Requests Rate** : Taux de requêtes par seconde
2. **API Request Latency** : Latence des requêtes (P95)
3. **Predictions** : Nombre de prédictions
4. **Errors** : Nombre d'erreurs
5. **Model Status** : État du modèle (chargé/non chargé)
6. **Request Status Codes** : Codes de statut HTTP

---

## 🐛 Problèmes Courants

### Problème 1 : Dashboard vide après ouverture

**Cause** : Pas de données dans Prometheus ou datasource mal configurée.

**Solution** :
1. Vérifier que Prometheus collecte des données : http://localhost:9090
2. Vérifier la datasource Prometheus dans Grafana
3. Générer du trafic : `python scripts/generate_traffic.py`
4. Rafraîchir le dashboard (icône en haut à droite)

### Problème 2 : "No data" sur tous les panneaux

**Cause** : La datasource Prometheus n'est pas configurée ou pointe vers le mauvais endpoint.

**Solution** :
1. Configuration → Data sources → Prometheus
2. URL : `http://prometheus:9090` (depuis Docker)
3. Tester la connexion : **Save & Test**

### Problème 3 : Dashboard n'apparaît pas dans la liste

**Cause** : Le provisioning automatique n'a pas fonctionné.

**Solution** :
1. Vérifier que `docker/grafana/dashboards/mlops-dashboard.json` existe
2. Vérifier que `docker/grafana/provisioning/dashboards/dashboard.yml` existe
3. Redémarrer Grafana : `docker-compose restart grafana`
4. Ou importer manuellement (Méthode 2)

---

## ✅ Checklist

- [ ] Grafana accessible : http://localhost:3000
- [ ] Connecté avec admin/admin
- [ ] Datasource Prometheus configurée et testée
- [ ] Dashboard "MLOps Pipeline - Monitoring" visible dans Browse
- [ ] Dashboard ouvert et affichant des données
- [ ] Prometheus collecte des données (http://localhost:9090)

---

## 🚀 Accès Rapide

**URL directe** (si le dashboard existe) :
```
http://localhost:3000/d/mlops-pipeline-monitoring/mlops-pipeline-monitoring
```

**Ou** :
1. http://localhost:3000
2. Dashboards → Browse
3. Chercher "MLOps Pipeline - Monitoring"
4. Cliquer pour ouvrir

---

**Une fois le dashboard ouvert, vous devriez voir tous les graphiques avec les métriques !** 🎉

