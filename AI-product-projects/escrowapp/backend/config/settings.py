"""
config/settings.py
------------------
Centralized app settings loaded from environment variables.
"""

from dotenv import load_dotenv
import os

load_dotenv()

# ── JWT ──────────────────────────────────────────────────────
JWT_SECRET_KEY   = os.getenv("JWT_SECRET_KEY", "change-me-in-production")
JWT_ALGORITHM    = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "1440"))  # 24 hours

# ── App ──────────────────────────────────────────────────────
APP_HOST  = os.getenv("APP_HOST", "0.0.0.0")
APP_PORT  = int(os.getenv("APP_PORT", "8000"))
DEBUG     = os.getenv("DEBUG", "True").lower() == "true"

# ── CORS ─────────────────────────────────────────────────────
_raw_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5500,http://127.0.0.1:5500")
CORS_ORIGINS = [o.strip() for o in _raw_origins.split(",")]
