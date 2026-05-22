"""
config.py
Loads all settings from .env file.
Single source of truth — all other modules import from here.
"""
import os
from dotenv import load_dotenv

load_dotenv()


def _require(key: str) -> str:
    val = os.getenv(key)
    if not val:
        raise EnvironmentError(
            f"Required env var '{key}' is not set. Check your .env file."
        )
    return val


# ── ESSL SQL Server ───────────────────────────────────────────────────────────
ESSL_SERVER   = _require("ESSL_SERVER")
ESSL_PORT     = os.getenv("ESSL_PORT", "1433")
ESSL_DATABASE = _require("ESSL_DATABASE")
ESSL_DRIVER   = os.getenv("ESSL_DRIVER", "ODBC Driver 17 for SQL Server")

# Optional when using Windows Authentication
ESSL_USERNAME = os.getenv("ESSL_USERNAME", "")
ESSL_PASSWORD = os.getenv("ESSL_PASSWORD", "")

# ── HRMS API ──────────────────────────────────────────────────────────────────
HRMS_API_BASE_URL = _require("HRMS_API_BASE_URL").rstrip("/")
HRMS_API_KEY      = _require("HRMS_API_KEY")

# ── Agent behaviour ───────────────────────────────────────────────────────────
SYNC_INTERVAL_SECONDS = int(os.getenv("SYNC_INTERVAL_SECONDS", "300"))
BATCH_SIZE            = int(os.getenv("BATCH_SIZE", "500"))
RETRY_ATTEMPTS        = int(os.getenv("RETRY_ATTEMPTS", "3"))
RETRY_DELAY_SECONDS   = int(os.getenv("RETRY_DELAY_SECONDS", "10"))
MONTH_OVERLAP_DAYS    = int(os.getenv("MONTH_OVERLAP_DAYS", "3"))

# ── Local state ───────────────────────────────────────────────────────────────
STATE_DB_PATH = os.getenv("STATE_DB_PATH", "agent_state.db")
LOG_DIR       = os.getenv("LOG_DIR", "logs")
LOG_LEVEL     = os.getenv("LOG_LEVEL", "INFO")


# ── Device sync ───────────────────────────────────────────────────────────────
DEVICE_SYNC_INTERVAL_SECONDS = int(os.getenv("DEVICE_SYNC_INTERVAL_SECONDS", "86400"))
COMPANY_ID                   = _require("COMPANY_ID")