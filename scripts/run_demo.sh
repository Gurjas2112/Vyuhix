#!/usr/bin/env bash
# One-command demo for macOS, Linux and Git Bash on Windows.
set -euo pipefail
cd "$(dirname "$0")/.."
PY=${PYTHON:-python3}; command -v "$PY" >/dev/null || PY=python
if [ ! -d .venv ]; then "$PY" -m venv .venv; fi
if [ -f .venv/Scripts/activate ]; then source .venv/Scripts/activate; else source .venv/bin/activate; fi
pip install -q -r backend/requirements.txt
( cd frontend && npm install --silent && npm run build --silent )
rm -rf data/runtime            # fresh demo state
echo "Vyuhix running at http://localhost:8000  (demo password: Demo@12345)"
cd backend && exec python -m uvicorn vyuhix.main:app --port 8000
