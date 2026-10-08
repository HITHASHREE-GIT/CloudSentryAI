"""
LaunchNest — Configuration
============================
Central settings for paths, API metadata, and JWT configuration.
"""

import os
from pathlib import Path

# ═══════════════════════════════════════════════════════
# PATHS
# ═══════════════════════════════════════════════════════

APP_DIR = Path(__file__).resolve().parent
BACKEND_DIR = APP_DIR.parent
DATA_DIR = BACKEND_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

DB_PATH = DATA_DIR / "launchnest.db"
DATABASE_URL = f"sqlite:///{DB_PATH}"

# ═══════════════════════════════════════════════════════
# API METADATA
# ═══════════════════════════════════════════════════════

API_TITLE = "LaunchNest API"
API_DESCRIPTION = "Customer SaaS demo for CloudSentry AI"
API_VERSION = "0.1.0"

# ═══════════════════════════════════════════════════════
# SECURITY / JWT
# ═══════════════════════════════════════════════════════

# In production: load from environment variables
SECRET_KEY = "launchnest-demo-secret-key-do-not-use-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

# ═══════════════════════════════════════════════════════
# CORS
# ═══════════════════════════════════════════════════════

# Where the React frontend will run
ALLOWED_ORIGINS = [
    "http://localhost:5174",
    "http://localhost:5173",  # in case of conflict
]

# Production frontend URL (set as env var on Render)
_frontend_url = os.getenv("FRONTEND_URL")
if _frontend_url:
    ALLOWED_ORIGINS.append(_frontend_url)

# ═══════════════════════════════════════════════════════
# DEBUG
# ═══════════════════════════════════════════════════════

DEBUG = True