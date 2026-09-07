"""
Script pour générer du trafic vers l'API et remplir Prometheus/Grafana
"""
import requests
import time
import sys
from pathlib import Path

# Ajouter le répertoire parent au path
sys.path.append(str(Path(__file__).parent.parent))

API_URL = "http://localhost:8000"

# Exemples de textes pour tester
TEXTS = [
    "Oil prices fall as OPEC signals higher output next quarter",
    "Senate debates new sanctions after overnight diplomatic talks",
    "Chipmaker forecasts weaker data-center demand this year",
    "Central bank holds rates as inflation cools for a third month",
]

SPORTS_TEXTS = [
    "Lakers defeat Celtics in overtime NBA playoff thriller",
    "Manchester United wins Champions League final on penalties",
    "Wimbledon champion claims third straight Grand Slam title",
    "Olympic swimmer breaks 200 meter freestyle world record",
    "Tour de France leader extends yellow jersey advantage",
    "World Cup quarterfinal goes to a penalty shootout",
]


def test_health():
    """Test le health check"""
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        if response.status_code == 200:
            print("[OK] API est accessible")
            return True
        else:
            print(f"[ERROR] Health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("[ERROR] API non accessible. Lancez: uvicorn src.inference.api:app --reload")
        return False
    except Exception as e:
        print(f"[ERROR] Erreur: {e}")
        return False


def generate_traffic(num_requests=20, delay=1, skew="none"):
    """Génère du trafic vers l'API"""
    print(f"\n[INFO] Generation de {num_requests} requetes...")
    print(f"[INFO] API URL: {API_URL}\n")
    
    success = 0
    errors = 0
    
    for i in range(num_requests):
        pool = SPORTS_TEXTS if skew == "sports" else TEXTS
        text = pool[i % len(pool)]
        
        try:
            response = requests.post(
                f"{API_URL}/predict",
                json={"text": text},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"[OK] Request {i+1}/{num_requests}: {result.get('prediction')} (confidence: {result.get('confidence', 0):.2f})")
                success += 1
            else:
                print(f"[ERROR] Request {i+1}/{num_requests}: Status {response.status_code}")
                errors += 1
        
        except Exception as e:
            print(f"[ERROR] Request {i+1}/{num_requests}: {e}")
            errors += 1
        
        # Attendre entre les requêtes
        if i < num_requests - 1:
            time.sleep(delay)
    
    print(f"\n[INFO] Resume:")
    print(f"  Reussies: {success}/{num_requests}")
    print(f"  Erreurs: {errors}/{num_requests}")
    print(f"\n[INFO] Les metriques sont maintenant dans Prometheus!")
    print(f"[INFO] Verifiez: http://localhost:9090 (chercher 'api_requests_total')")
    print(f"[INFO] Verifiez: http://localhost:3000 (dashboard Grafana)")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Generer du trafic vers l API')
    parser.add_argument(
        '--requests',
        type=int,
        default=20,
        help='Nombre de requetes a generer (default: 20)'
    )
    parser.add_argument(
        '--delay',
        type=float,
        default=1.0,
        help='Delai entre les requetes en secondes (default: 1.0)'
    )
    parser.add_argument(
        "--skew",
        choices=["none", "sports"],
        default="none",
        help="sports: mix biaisé pour déclencher le drift sur le journal",
    )
    
    args = parser.parse_args()
    
    print("="*60)
    print("  GENERATION DE TRAFIC - API MLOps")
    print("="*60)
    
    # Test health check
    if not test_health():
        print("\n[ERROR] L'API n'est pas accessible. Lancez-la d'abord:")
        print("  uvicorn src.inference.api:app --reload --port 8000")
        sys.exit(1)
    
    # Générer le trafic
    generate_traffic(num_requests=args.requests, delay=args.delay, skew=args.skew)
    print("[INFO] Predictions loguees dans data/processed/predictions.csv")


if __name__ == "__main__":
    main()

