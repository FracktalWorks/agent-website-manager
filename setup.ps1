# agent-website-manager - Automated Setup Script
Write-Host "Setting up: agent-website-manager" -ForegroundColor Cyan

$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Python not found" -ForegroundColor Red; exit 1
}
Write-Host "Found $pythonVersion" -ForegroundColor Green

if (-not (Test-Path ".venv")) {
    python -m venv .venv
    Write-Host "Virtual environment created" -ForegroundColor Green
}

& .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip --quiet

if (Test-Path "requirements.txt") {
    pip install -r requirements.txt --quiet
    Write-Host "Dependencies installed" -ForegroundColor Green
}

if (-not (Test-Path ".env") -and (Test-Path ".env.example")) {
    Copy-Item ".env.example" ".env"
    Write-Host "Created .env from .env.example — EDIT WITH YOUR API KEYS!" -ForegroundColor Yellow
}

Write-Host "SETUP COMPLETE! Edit .env with your API keys." -ForegroundColor Green
Write-Host "To activate: .\.venv\Scripts\Activate.ps1" -ForegroundColor Gray
