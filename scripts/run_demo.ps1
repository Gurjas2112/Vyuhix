# One-command demo for Windows PowerShell.
$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..")
if (-not (Test-Path .venv)) { py -3 -m venv .venv }
& .\.venv\Scripts\Activate.ps1
pip install -q -r backend\requirements.txt
Push-Location frontend; npm install --silent; npm run build --silent; Pop-Location
if (Test-Path data\runtime) { Remove-Item -Recurse -Force data\runtime }
Write-Host "Vyuhix running at http://localhost:8000  (demo password: Demo@12345)"
Set-Location backend
python -m uvicorn vyuhix.main:app --port 8000
