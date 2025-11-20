"""
Script de test end-to-end du pipeline MLOps
Teste le cycle complet : Train -> Deploy -> Monitor -> Retrain
"""
import sys
import time
from pathlib import Path
import requests

# Ajouter le répertoire parent au path
sys.path.append(str(Path(__file__).parent.parent))

from src.retraining.auto_retrain import AutoRetrainer, RetrainTrigger
from src.utils.logger import get_logger

logger = get_logger(__name__)


def test_training():
    """Test 1: Entraînement d'un modèle"""
    print("\n" + "="*60)
    print("TEST 1: Entraînement d'un modèle")
    print("="*60)
    
    from src.training.train import main as train_main
    import sys as sys_module
    
    # Simuler les arguments
    sys_module.argv = ['train.py', '--model-type', 'random_forest']
    
    try:
        train_main()
        print("[OK] Test 1 réussi: Modèle entraîné")
        return True
    except Exception as e:
        print(f"[ERROR] Test 1 échoué: {e}")
        return False


def test_api():
    """Test 2: API de prédiction"""
    print("\n" + "="*60)
    print("TEST 2: API de prédiction")
    print("="*60)
    
    api_url = "http://localhost:8000"
    
    # Test health check
    try:
        response = requests.get(f"{api_url}/health", timeout=5)
        if response.status_code == 200:
            print("[OK] Health check réussi")
        else:
            print(f"[ERROR] Health check échoué: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("[WARNING] API non disponible (lancez: uvicorn src.inference.api:app)")
        print("[INFO] Ce test est optionnel si l'API n'est pas lancée")
        return None  # Retourner None pour indiquer que c'est optionnel
    except Exception as e:
        print(f"[ERROR] Erreur health check: {e}")
        return False
    
    # Test prédiction
    try:
        response = requests.post(
            f"{api_url}/predict",
            json={"text": "artificial intelligence machine learning"},
            timeout=5
        )
        if response.status_code == 200:
            result = response.json()
            print(f"[OK] Prédiction réussie: {result.get('prediction')}")
            return True
        else:
            print(f"[ERROR] Prédiction échouée: {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERROR] Erreur prédiction: {e}")
        return False


def test_retrain():
    """Test 3: Auto-retrain"""
    print("\n" + "="*60)
    print("TEST 3: Auto-retrain")
    print("="*60)
    
    try:
        retrainer = AutoRetrainer()
        result = retrainer.retrain(
            trigger=RetrainTrigger.MANUAL,
            model_type='random_forest'
        )
        
        if result.success:
            print(f"[OK] Retrain réussi: {result.reason}")
            if result.deployed:
                print(f"[OK] Modèle déployé en production")
            return True
        else:
            print(f"[ERROR] Retrain échoué: {result.reason}")
            return False
    except Exception as e:
        print(f"[ERROR] Erreur retrain: {e}")
        return False


def test_drift_detection():
    """Test 4: Détection de drift"""
    print("\n" + "="*60)
    print("TEST 4: Détection de drift")
    print("="*60)
    
    try:
        retrainer = AutoRetrainer()
        data_path = "data/processed/train.csv"
        
        drift_score, is_drift = retrainer.check_drift(data_path)
        
        print(f"[INFO] Drift score: {drift_score:.4f}")
        print(f"[INFO] Drift détecté: {is_drift}")
        print("[OK] Test 4 réussi: Détection de drift fonctionne")
        return True
    except Exception as e:
        print(f"[ERROR] Erreur détection drift: {e}")
        return False


def main():
    """Exécute tous les tests"""
    print("\n" + "="*60)
    print("TESTS END-TO-END - Pipeline MLOps")
    print("="*60)
    
    results = {
        "Training": test_training(),
        "API": test_api(),
        "Drift Detection": test_drift_detection(),
        "Auto-Retrain": test_retrain()
    }
    
    # Résumé
    print("\n" + "="*60)
    print("RÉSUMÉ DES TESTS")
    print("="*60)
    
    for test_name, result in results.items():
        if result is None:
            status = "[SKIP]"
        elif result:
            status = "[OK]"
        else:
            status = "[ERROR]"
        print(f"{status} {test_name}")
    
    # Compter seulement les tests qui ont vraiment échoué (pas les optionnels)
    total = len([r for r in results.values() if r is not None])
    passed = sum(1 for r in results.values() if r is True)
    skipped = sum(1 for r in results.values() if r is None)
    failed = sum(1 for r in results.values() if r is False)
    
    print(f"\nTotal: {passed}/{total} tests réussis")
    if skipped > 0:
        print(f"Skippés: {skipped} (optionnels)")
    if failed > 0:
        print(f"Échoués: {failed}")
    
    if failed == 0:
        print("\n[OK] Tous les tests obligatoires sont passés!")
        return 0
    else:
        print(f"\n[ERROR] {failed} test(s) obligatoire(s) ont échoué")
        return 1


if __name__ == "__main__":
    sys.exit(main())

