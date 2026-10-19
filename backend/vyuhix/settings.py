import os
import secrets
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = Path(os.getenv("VYUHIX_DATA_DIR", ROOT / "data" / "demo" / "acme-fintech"))
RUNTIME_DIR = Path(os.getenv("VYUHIX_RUNTIME_DIR", ROOT / "data" / "runtime"))
RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
FRONTEND_DIST = ROOT / "frontend" / "dist"
MODEL_CACHE = Path(os.getenv("VYUHIX_MODEL_CACHE", RUNTIME_DIR / "models"))   # embedding model download

_secret_file = RUNTIME_DIR / "jwt_secret"
if os.getenv("VYUHIX_JWT_SECRET"):
    JWT_SECRET = os.environ["VYUHIX_JWT_SECRET"]
else:
    if not _secret_file.exists():
        _secret_file.write_text(secrets.token_hex(32))
    JWT_SECRET = _secret_file.read_text().strip()

JWT_TTL_HOURS = 8
DEMO_PASSWORD = os.getenv("VYUHIX_DEMO_PASSWORD", "Demo@12345")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
LLM_MODEL = os.getenv("VYUHIX_LLM_MODEL", "claude-sonnet-5-5")
LLM_EFFORT = os.getenv("VYUHIX_LLM_EFFORT", "low")          # low | medium | high; see backend/evals/EXPERIMENTS.md
LLM_MAX_TURNS = 4
CORS_ORIGINS = os.getenv("VYUHIX_CORS", "http://localhost:5173").split(",")
