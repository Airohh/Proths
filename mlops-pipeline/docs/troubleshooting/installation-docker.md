# 🐳 Problème Docker - Guide de Résolution

## Problème

L'erreur `docker : Le terme 'docker' n'est pas reconnu` signifie que :
- Docker n'est **pas installé** sur votre machine, OU
- Docker est installé mais **pas dans le PATH** Windows

## 🔍 Diagnostic

### Vérifier si Docker est installé

**Méthode 1 : Commande PowerShell**
```powershell
docker --version
```

**Si vous voyez** : `docker : Le terme 'docker' n'est pas reconnu`
→ Docker n'est pas installé ou pas dans le PATH

**Si vous voyez** : `Docker version 20.10.x` ou similaire
→ Docker est installé

### Vérifier si Docker Desktop est installé

1. Ouvrir le **Menu Démarrer**
2. Chercher "Docker Desktop"
3. Si trouvé → Docker est installé mais peut-être pas démarré
4. Si non trouvé → Docker n'est pas installé

## Solutions

### Solution 1 : Installer Docker Desktop (Recommandé)

#### Étape 1 : Télécharger Docker Desktop

1. Aller sur : https://www.docker.com/products/docker-desktop
2. Cliquer sur "Download for Windows"
3. Télécharger `Docker Desktop Installer.exe`

#### Étape 2 : Installer Docker Desktop

1. **Exécuter** le fichier `Docker Desktop Installer.exe`
2. **Cocher** "Use WSL 2 instead of Hyper-V" (recommandé)
3. Suivre l'assistant d'installation
4. **Redémarrer** l'ordinateur si demandé

#### Étape 3 : Démarrer Docker Desktop

1. Ouvrir **Docker Desktop** depuis le menu Démarrer
2. Attendre que Docker démarre (icône dans la barre des tâches)
3. Vérifier que l'icône Docker est **verte** (pas rouge)

#### Étape 4 : Vérifier l'installation

Ouvrir PowerShell et tester :
```powershell
docker --version
docker-compose --version
docker ps
```

**Si ça fonctionne** → Docker est prêt

---

### Solution 2 : Ajouter Docker au PATH (Si déjà installé)

Si Docker est installé mais pas reconnu :

#### Étape 1 : Trouver où Docker est installé

Généralement dans :
- `C:\Program Files\Docker\Docker\resources\bin\`
- `C:\Program Files\Docker\Docker\resources\cli-plugins\`

#### Étape 2 : Ajouter au PATH

1. Ouvrir **Paramètres Windows**
2. Chercher "Variables d'environnement"
3. Cliquer sur "Variables d'environnement"
4. Dans "Variables système", trouver `Path`
5. Cliquer sur "Modifier"
6. Cliquer sur "Nouveau"
7. Ajouter : `C:\Program Files\Docker\Docker\resources\bin`
8. Cliquer sur "OK" partout
9. **Redémarrer PowerShell** (important !)

#### Étape 3 : Vérifier

```powershell
docker --version
```

---

### Solution 3 : Utiliser les Services Sans Docker

**Bonne nouvelle** : Docker n'est **pas obligatoire** pour utiliser le projet !

Vous pouvez utiliser :
- **MLflow UI** : Sans Docker
- **API FastAPI** : Sans Docker
- **Prometheus** : Optionnel (monitoring avancé)
- **Grafana** : Optionnel (visualisation avancée)

#### Services Essentiels (Sans Docker)

```powershell
# Terminal 1 - MLflow UI
cd "C:\Users\Utilisateur\Desktop\4 mois\Prometheus - LLM\mlops-pipeline"
mlflow ui --port 5000

# Terminal 2 - API
cd "C:\Users\Utilisateur\Desktop\4 mois\Prometheus - LLM\mlops-pipeline"
uvicorn src.inference.api:app --reload --port 8000
```


---

## Recommandation

### Pour Développement Local

**Option A : Sans Docker** (Plus simple)
- Utiliser MLflow UI et API directement
- Pas besoin de Docker
- Plus rapide à démarrer

**Option B : Avec Docker** (Plus complet)
- Monitoring complet (Prometheus + Grafana)
- Environnement isolé
- Plus proche de la production

### Pour Production

Docker est **recommandé** pour :
- Isolation des services
- Déploiement facile
- Scalabilité
- Monitoring complet

---

## 🐛 Problèmes Courants

### 1. Docker Desktop ne démarre pas

**Symptôme** : L'icône Docker reste rouge

**Solutions** :
1. Vérifier que WSL 2 est installé :
   ```powershell
   wsl --status
   ```
2. Si WSL 2 n'est pas installé :
   ```powershell
   wsl --install
   ```
3. Redémarrer l'ordinateur
4. Relancer Docker Desktop

### 2. "Docker daemon is not running"

**Solution** :
1. Ouvrir Docker Desktop
2. Attendre que l'icône soit verte
3. Vérifier : `docker ps`

### 3. Ports déjà utilisés

**Erreur** : `port is already allocated`

**Solution** :
```powershell
# Trouver le processus
netstat -ano | findstr :9090

# Tuer le processus (remplacer <PID>)
taskkill /PID <PID> /F
```

---

## 📋 Checklist d'Installation Docker

- [ ] Docker Desktop téléchargé
- [ ] Docker Desktop installé
- [ ] Ordinateur redémarré (si demandé)
- [ ] Docker Desktop lancé
- [ ] Icône Docker verte dans la barre des tâches
- [ ] `docker --version` fonctionne
- [ ] `docker-compose --version` fonctionne
- [ ] `docker ps` fonctionne

---

## Après Installation

Une fois Docker installé, vous pouvez lancer :

```powershell
cd "C:\Users\Utilisateur\Desktop\4 mois\Prometheus - LLM\mlops-pipeline"
docker-compose up -d
```

Cela lancera :
- Prometheus (port 9090)
- Grafana (port 3000)
- MLflow (port 5000)
- TimescaleDB (port 5432)

---

## 💡 Alternative : Docker via WSL 2

Si vous avez des problèmes avec Docker Desktop, vous pouvez utiliser Docker dans WSL 2 :

```bash
# Dans WSL 2
sudo apt update
sudo apt install docker.io docker-compose
sudo service docker start
```

---

## Ressources

- **Docker Desktop** : https://www.docker.com/products/docker-desktop
- **Documentation Docker** : https://docs.docker.com/
- **WSL 2** : https://docs.microsoft.com/en-us/windows/wsl/install

---

## Résumé

**Problème** : Docker non installé ou pas dans PATH

**Solutions** :
1. **Installer Docker Desktop** (recommandé pour Windows)
2. **Ajouter Docker au PATH** (si déjà installé)
3. **Utiliser sans Docker** (services essentiels fonctionnent)

**Pour le projet** : Docker est **optionnel** pour les fonctionnalités de base !

---

**Dernière mise à jour** : 2024-11-18

