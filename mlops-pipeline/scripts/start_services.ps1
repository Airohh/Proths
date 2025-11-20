# Script PowerShell pour lancer les services MLOps
# Usage: .\scripts\start_services.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Demarrage des Services MLOps" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Vérifier que nous sommes dans le bon répertoire
if (-not (Test-Path "mlops-pipeline")) {
    Write-Host "[ERROR] Executez ce script depuis le repertoire racine du projet" -ForegroundColor Red
    exit 1
}

Set-Location mlops-pipeline

# Fonction pour vérifier si un port est utilisé
function Test-Port {
    param([int]$Port)
    $connection = Test-NetConnection -ComputerName localhost -Port $Port -InformationLevel Quiet -WarningAction SilentlyContinue
    return $connection
}

# 1. MLflow UI
Write-Host "[1/2] Verification MLflow UI (port 5000)..." -ForegroundColor Yellow
if (Test-Port -Port 5000) {
    Write-Host "  [INFO] Port 5000 deja utilise" -ForegroundColor Yellow
    Write-Host "  [INFO] MLflow UI peut etre deja lance" -ForegroundColor Yellow
} else {
    Write-Host "  [OK] Port 5000 disponible" -ForegroundColor Green
    Write-Host "  [INFO] Pour lancer MLflow UI:" -ForegroundColor Cyan
    Write-Host "    mlflow ui --port 5000" -ForegroundColor White
}

# 2. API FastAPI
Write-Host ""
Write-Host "[2/2] Verification API FastAPI (port 8000)..." -ForegroundColor Yellow
if (Test-Port -Port 8000) {
    Write-Host "  [INFO] Port 8000 deja utilise" -ForegroundColor Yellow
    Write-Host "  [INFO] API peut etre deja lancee" -ForegroundColor Yellow
} else {
    Write-Host "  [OK] Port 8000 disponible" -ForegroundColor Green
    Write-Host "  [INFO] Pour lancer l'API:" -ForegroundColor Cyan
    Write-Host "    uvicorn src.inference.api:app --reload --port 8000" -ForegroundColor White
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Services Disponibles" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "MLflow UI:    http://localhost:5000" -ForegroundColor Green
Write-Host "API FastAPI:  http://localhost:8000" -ForegroundColor Green
Write-Host "API Docs:     http://localhost:8000/docs" -ForegroundColor Green
Write-Host ""
Write-Host "Pour lancer les services, ouvrez 2 terminaux:" -ForegroundColor Yellow
Write-Host "  Terminal 1: mlflow ui --port 5000" -ForegroundColor White
Write-Host "  Terminal 2: uvicorn src.inference.api:app --reload" -ForegroundColor White
Write-Host ""

