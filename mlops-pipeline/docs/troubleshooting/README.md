# 🔧 Guide de Dépannage

## Problèmes Courants et Solutions

### 1. ERR_CONNECTION_REFUSED

**Symptôme** : Impossible d'accéder à http://localhost:XXXX

**Solutions** :
- Vérifier que le service est lancé
- Voir [Démarrage des Services](demarrage-services.md)

### 2. Docker Non Installé

**Symptôme** : `docker : Le terme 'docker' n'est pas reconnu`

**Solutions** :
- Voir [Installation Docker](installation-docker.md)

### 3. Services Vides

**Symptôme** : Grafana/Prometheus/MLflow sont vides

**Solutions** :
- Voir [Remplir les Services](remplir-services.md)

### 4. Monitoring Vide

**Symptôme** : Prometheus/Grafana accessibles mais n'affichent rien

**Solutions** :
- Voir [Monitoring Vide](monitoring-vide.md)

---

## Guides de Dépannage

- **[Démarrage des Services](demarrage-services.md)** : Comment lancer tous les services
- **[Installation Docker](installation-docker.md)** : Installer et configurer Docker
- **[Remplir les Services](remplir-services.md)** : Générer des données pour les services
- **[Monitoring Vide](monitoring-vide.md)** : Résoudre les problèmes de monitoring (Prometheus/Grafana vides)

