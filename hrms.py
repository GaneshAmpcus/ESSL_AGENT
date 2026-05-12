"""
db/hrms.py
HTTP client that pushes normalised punch data to the HRMS REST API.
All communication with HRMS goes through this module.
"""
import time
from typing import Any

import requests

import config
from logger import get_logger

log = get_logger(__name__)

# Shared session — reuses TCP connections across calls
_session = requests.Session()
_session.headers.update({
    "Content-Type": "application/json",
    "X-API-Key": config.HRMS_API_KEY,
    "User-Agent": "ESSL-Agent/1.0",
})


def _url(path: str) -> str:
    return f"{config.HRMS_API_BASE_URL}/{path.lstrip('/')}"


def test_connection() -> bool:
    """Ping HRMS health endpoint."""
    try:
        r = _session.get(_url("/health"), timeout=10)
        r.raise_for_status()
        log.info("HRMS API reachable. Status: %s", r.status_code)
        return True
    except Exception as e:
        log.error("HRMS API unreachable: %s", e)
        return False


def push_punches(punches: list[dict]) -> dict[str, Any]:
    """
    POST a batch of normalised punch records to the HRMS ingest endpoint.

    Expected HRMS endpoint:
        POST /api/v1/attendance/ingest
        Body: { "punches": [ ... ] }

    Expected HRMS response:
        {
            "accepted": 498,
            "duplicates": 2,
            "errors": []
        }

    Raises requests.HTTPError on non-2xx responses.
    """
    payload = {"punches": punches}

    attempt = 0
    last_error = None

    while attempt < config.RETRY_ATTEMPTS:
        attempt += 1
        try:
            response = _session.post(
                _url("/ingest/"),
                json=payload,
                timeout=60,
            )
            response.raise_for_status()
            result = response.json()
            log.info(
                "HRMS accepted %d punches (duplicates: %d) in attempt %d",
                result.get("accepted", len(punches)),
                result.get("duplicates", 0),
                attempt,
            )
            return result

        except requests.exceptions.Timeout as e:
            last_error = e
            log.warning("HRMS push timed out (attempt %d/%d)", attempt, config.RETRY_ATTEMPTS)

        except requests.exceptions.ConnectionError as e:
            last_error = e
            log.warning("HRMS connection error (attempt %d/%d): %s", attempt, config.RETRY_ATTEMPTS, e)

        except requests.exceptions.HTTPError as e:
            last_error = e
            status = e.response.status_code if e.response else "?"
            body   = e.response.text[:500] if e.response else ""
            log.error(
                "HRMS returned HTTP %s (attempt %d/%d) — %s",
                status, attempt, config.RETRY_ATTEMPTS, body
            )
            # 4xx errors won't recover with retry — raise immediately
            if e.response and 400 <= e.response.status_code < 500:
                raise

        if attempt < config.RETRY_ATTEMPTS:
            wait = config.RETRY_DELAY_SECONDS * (2 ** (attempt - 1)) # exponential-ish backoff
            log.info("Retrying in %ds...", wait)
            time.sleep(wait)

    raise RuntimeError(
        f"HRMS push failed after {config.RETRY_ATTEMPTS} attempts. Last error: {last_error}"
    )
