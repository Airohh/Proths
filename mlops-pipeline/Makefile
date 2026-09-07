.PHONY: help install train api test clean docker-up docker-down

help:
	@echo "Commandes disponibles:"
	@echo "  make install          - Installer les dépendances"
	@echo "  make download-data    - Télécharger un dataset (par défaut: news)"
	@echo "  make generate-data    - Générer des données de test"
	@echo "  make train            - Entraîner le modèle"
	@echo "  make api              - Lancer l'API"
	@echo "  make test             - Lancer les tests"
	@echo "  make docker-up        - Lancer les services Docker"
	@echo "  make docker-down      - Arrêter les services Docker"
	@echo "  make clean            - Nettoyer les fichiers temporaires"

install:
	pip install -r requirements.txt

download-data:
	python scripts/download_dataset.py --source popular --type news
	python scripts/prepare_ag_news.py

generate-data:
	python scripts/generate_sample_data.py

train:
	python src/training/train.py

api:
	uvicorn src.inference.api:app --reload

test:
	pytest tests/ -v

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

clean:
	find . -type d -name __pycache__ -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov

