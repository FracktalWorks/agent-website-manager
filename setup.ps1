# agent-website-manager - first-run setup. Safe to run on every folder open.
#
# WHY THIS IS IDEMPOTENT AND NOT JUST `pip install -r`
#   VS Code runs this task on `folderOpen`, so it fires every time the window
#   opens. Re-resolving every dependency each time costs 20-60s of terminal for
#   no change. It now fingerprints requirements.txt and skips when the file has
#   not moved, so the second open is instant.
#
# WHY THE EXIT CODE IS CHECKED
#   The previous version piped pip through --quiet and never looked at
#   $LASTEXITCODE. torch (2.5GB, since split out to requirements-ml.txt) had
#   been failing to install on every single open while this script printed
#   "Dependencies installed" in green. A setup script that cannot fail is not a
#   setup script.

Write-Host "agent-website-manager - environment" -ForegroundColor Cyan

$py = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Python not found on PATH" -ForegroundColor Red
    exit 1
}
Write-Host "  $py"

if (-not (Test-Path ".venv")) {
    Write-Host "  creating .venv ..." -ForegroundColor Yellow
    python -m venv .venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: could not create .venv" -ForegroundColor Red
        exit 1
    }
}
& .\.venv\Scripts\Activate.ps1

# Fingerprint the requirements file. The marker lives INSIDE .venv so that
# deleting the venv correctly forces a reinstall.
$reqHash = (Get-FileHash "requirements.txt" -Algorithm SHA256).Hash
$marker = ".venv\.deps-$reqHash"

if (Test-Path $marker) {
    Write-Host "  dependencies up to date" -ForegroundColor Green
} else {
    Write-Host "  installing dependencies (first run for this requirements.txt)" -ForegroundColor Yellow
    python -m pip install --upgrade pip --quiet
    pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: pip failed - the environment is INCOMPLETE" -ForegroundColor Red
        Write-Host "       fix the error above, then reopen the folder" -ForegroundColor Red
        exit 1
    }
    Get-ChildItem ".venv" -Filter ".deps-*" -ErrorAction SilentlyContinue |
        Remove-Item -Force -ErrorAction SilentlyContinue
    New-Item -ItemType File $marker | Out-Null
    Write-Host "  dependencies installed" -ForegroundColor Green
}

# pip reporting success and `import` working are different questions once a
# wheel is platform-specific, so prove the modules the repo actually calls.
$check = python -c "import requests, PIL, segno, bs4, dotenv; print('ok')" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "  WARNING: a core module will not import:" -ForegroundColor Red
    Write-Host "  $check" -ForegroundColor Red
} else {
    Write-Host "  core imports ok" -ForegroundColor Green
}

if (-not (Test-Path ".env") -and (Test-Path ".env.example")) {
    Copy-Item ".env.example" ".env"
    Write-Host "  created .env from .env.example - ADD YOUR KEYS" -ForegroundColor Yellow
}

Write-Host "  hub opens automatically; if not, Run Task > 'workspace hub (preview in VS Code)'" -ForegroundColor Gray
Write-Host "  optional ML extras (2.5GB, media auto-tagging only): pip install -r requirements-ml.txt" -ForegroundColor DarkGray
