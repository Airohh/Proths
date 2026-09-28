.PHONY: help install data data-small train compare api monitor traffic drift demo test lint format seed up down logs clean

PY ?= python

help: ## Liste des commandes
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

install: ## Dépendances (runtime + dev)
	$(PY) -m pip install -r requirements-dev.txt

# --- Local, sans Docker -------------------------------------------------------

data: ## AG News complet -> data/processed/{train,holdout,stream}.csv
	$(PY) scripts/prepare_ag_news.py

data-small: ## Démarrage à froid : 5 000 articles de train
	$(PY) scripts/prepare_ag_news.py --train-size 5000

train: ## Entraîne un candidat, duel avec le champion, promotion éventuelle
	$(PY) -m src.training.train

compare: ## Compare logreg / linear_svc / naive_bayes / random_forest
	$(PY) scripts/compare_models.py

api: ## API sur :8000
	uvicorn src.inference.api:app --port 8000

monitor: ## Monitoring en boucle (/metrics sur :8001)
	$(PY) -m src.monitoring.monitor

traffic: ## 500 requêtes équilibrées + feedback
	$(PY) scripts/simulate_traffic.py --n 500

drift: ## 500 requêtes à 70 % Sports + feedback
	$(PY) scripts/simulate_traffic.py --n 500 --skew Sports --ratio 0.7

demo: ## Boucle complète hors Docker -> reports/demo.{json,png}
	$(PY) scripts/demo.py

# --- Qualité -----------------------------------------------------------------

test: ## Tests + couverture
	$(PY) -m pytest --cov --cov-report=term-missing

lint: ## ruff check + format --check
	ruff check .
	ruff format --check .

format: ## Formate le code
	ruff check --fix .
	ruff format .

# --- Docker ------------------------------------------------------------------

seed: ## Données + premier champion dans la stack (TRAIN_SIZE=5000 pour la démo)
	docker compose up -d mlflow
	docker compose run --rm trainer

up: ## MLflow :5000 · API :8000 · Prometheus :9090 · Grafana :3000
	docker compose up -d --build

down: ## Arrête la stack (les volumes restent)
	docker compose down

logs: ## Logs API + monitor
	docker compose logs -f api monitor

clean: ## Supprime données locales, runs MLflow et volumes Docker
	docker compose down -v
	rm -rf mlruns data/demo data/processed/*.csv data/predictions.db* reports/_*
