FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY config ./config
COPY src ./src
COPY scripts ./scripts

# Utilisateur non-root ; /app/data est monté en volume (données + journal des prédictions).
RUN useradd --create-home --uid 1000 app && mkdir -p /app/data /app/reports \
    && chown -R app:app /app
USER app

EXPOSE 8000
CMD ["uvicorn", "src.inference.api:app", "--host", "0.0.0.0", "--port", "8000"]
