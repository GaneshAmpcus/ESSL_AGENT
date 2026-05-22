"""
core/processor.py
Transforms raw ESSL DeviceLogs rows into the clean payload
the HRMS API expects.

Responsibilities:
  - Strip columns HRMS doesn't need
  - Normalise direction values to 'in' / 'out' / 'unknown'
  - Handle ESSL's null-date sentinel (1900-01-01)
  - Attach source metadata
  - Flag rows that are missing critical fields
"""
from logger import get_logger

log = get_logger(__name__)

# ESSL uses this as a null-date sentinel — treat as missing punch
_NULL_DATE_PREFIXES = ("1900-01-01",)

# Map all ESSL direction variants to clean values
_DIRECTION_MAP = {
    "in":   "in",
    "out":  "out",
    "i":    "in",
    "o":    "out",
    "0":    "in",
    "1":    "out",
    "255":  "unknown",
}

def _clean_coordinate(val) -> str | None:
    """Returns None if coordinate is missing, zero, or blank."""
    if val is None:
        return None
    s = str(val).strip()
    if not s or s in ("0", "0.0", "0.00"):
        return None
    return s


def _normalise_direction(raw: str | None) -> str:
    if not raw:
        return "unknown"
    return _DIRECTION_MAP.get(str(raw).strip().lower(), "unknown")


def _is_null_date(val: str | None) -> bool:
    if not val:
        return True
    return any(str(val).startswith(p) for p in _NULL_DATE_PREFIXES)


def normalise_punch(raw_row: dict) -> dict | None:
    """
    Convert a single raw ESSL DeviceLogs row into a clean HRMS punch dict.

    Returns None if the row is unusable (missing LogDate, missing UserId).
    The caller collects None returns and logs them separately.
    """
    user_id  = str(raw_row.get("UserId", "")).strip()
    log_date = raw_row.get("LogDate")

    # Guard: skip rows with no user or null date
    if not user_id:
        log.debug("Skipping row %s — empty UserId", raw_row.get("DeviceLogId"))
        return None

    if _is_null_date(log_date):
        log.debug("Skipping row %s — null LogDate sentinel", raw_row.get("DeviceLogId"))
        return None

    # Prefer AttDirection (ESSL's processed direction) over raw Direction
    att_direction = _normalise_direction(raw_row.get("AttDirection"))
    raw_direction = _normalise_direction(raw_row.get("Direction"))
    direction = att_direction if att_direction != "unknown" else raw_direction

    return {
        "employee_code":  user_id,
    
        # Dedup key — keep as integer
        "essl_log_id":    raw_row["DeviceLogId"],
    
        # Which ESSL partition table — separate field for dedup
        "essl_source_table": raw_row.get("source_table", ""),
    
        # Core punch data
        "punch_time":     str(log_date),
        "direction":      direction,
        "device_id":      raw_row.get("DeviceId"),
    
        # Location
        "latitude":       _clean_coordinate(raw_row.get("Latitude")),
        "longitude":      _clean_coordinate(raw_row.get("Longitude")),
    
        # Metadata
        "source":         "essl",
        "raw_created_at": str(raw_row.get("CreatedDate", "")),
    }


def normalise_batch(raw_rows: list[dict]) -> tuple[list[dict], list[dict]]:
    """
    Normalise a list of raw rows.

    Returns:
        valid   — list of clean punch dicts ready to push to HRMS
        skipped — list of raw rows that could not be normalised
    """
    valid   = []
    skipped = []

    for row in raw_rows:
        result = normalise_punch(row)
        if result:
            valid.append(result)
        else:
            skipped.append(row)

    if skipped:
        log.warning(
            "%d row(s) skipped in this batch (null date or empty UserId). "
            "DeviceLogIds: %s",
            len(skipped),
            [r.get("DeviceLogId") for r in skipped[:10]],
        )

    return valid, skipped
