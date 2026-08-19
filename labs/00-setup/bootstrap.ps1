# Windows bootstrap: virtualenv + deps, then hand off to the cross-platform setup.py.
#   pwsh -ExecutionPolicy Bypass -File labs\00-setup\bootstrap.ps1
$ErrorActionPreference = 'Stop'
Set-Location (Join-Path $PSScriptRoot '..\..')

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: Python 3.10+ not found. Install from https://www.python.org/downloads/" -ForegroundColor Red
    exit 1
}
Write-Host "==> $(python --version)"

if (-not (Test-Path '.venv')) { python -m venv .venv }
& .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip wheel | Out-Null
pip install -r requirements.txt

python .\labs\00-setup\setup.py

Write-Host ""
Write-Host "==> Activate the venv in new terminals with: .\.venv\Scripts\Activate.ps1" -ForegroundColor Green
