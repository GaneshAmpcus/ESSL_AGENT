"""
db/essl.py
All read operations against the ESSL SQL Server.
Nothing in this file writes to ESSL — strictly read-only.
"""
import re
from contextlib import contextmanager
from datetime import datetime, timedelta
from typing import Generator

import pyodbc

import config
from logger import get_logger

log = get_logger(__name__)

# ── Connection ────────────────────────────────────────────────────────────────

def _build_conn_string() -> str:
    """
    Builds the pyodbc connection string.
    Supports both Windows Authentication (Trusted_Connection)
    and SQL Server Authentication (UID/PWD) based on config.
    If ESSL_USERNAME is set in .env, SQL Server auth is used.
    If not, falls back to Windows Authentication (dev/local only).
    """
    base = (
        f"DRIVER={{{config.ESSL_DRIVER}}};"
        f"SERVER={config.ESSL_SERVER},{config.ESSL_PORT};"
        f"DATABASE={config.ESSL_DATABASE};"
        "TrustServerCertificate=yes;"
        "Connection Timeout=30;"
    )
 
    if config.ESSL_USERNAME and config.ESSL_PASSWORD:
        # SQL Server Authentication — used for production server
        return base + (
            f"UID={config.ESSL_USERNAME};"
            f"PWD={config.ESSL_PASSWORD};"
        )
    else:
        # Windows Authentication — used for local dev only
        return base + "Trusted_Connection=yes;"
 


@contextmanager
def get_connection() -> Generator[pyodbc.Connection, None, None]:
    conn = pyodbc.connect(_build_conn_string(), autocommit=True)
    try:
        yield conn
    finally:
        conn.close()


def test_connection() -> bool:
    """Ping the ESSL DB. Returns True if reachable."""
    try:
        with get_connection() as conn:
            conn.execute("SELECT 1")
        log.info("ESSL connection OK.")
        return True
    except Exception as e:
        log.error("ESSL connection FAILED: %s", e)
        return False


# ── Primary key detection ─────────────────────────────────────────────────────

def _get_pk_column(conn, table_name: str) -> str:
    """
    Auto-detects the primary key column name for a given table.
    ESSL uses 'DeviceLogId' in production but dummy/test tables may use 'Id'.
    Falls back to 'DeviceLogId' if detection fails.
    """
    sql = """
        SELECT c.COLUMN_NAME
        FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS tc
        JOIN INFORMATION_SCHEMA.CONSTRAINT_COLUMN_USAGE c
          ON c.CONSTRAINT_NAME = tc.CONSTRAINT_NAME
        WHERE tc.TABLE_NAME = ?
          AND tc.CONSTRAINT_TYPE = 'PRIMARY KEY'
    """
    row = conn.execute(sql, (table_name,)).fetchone()
    if row:
        log.debug("PK column for '%s': %s", table_name, row[0])
        return row[0]
    log.warning(
        "Could not detect PK for '%s' — falling back to 'DeviceLogId'", table_name
    )
    return "DeviceLogId"


# ── Partition table discovery ─────────────────────────────────────────────────

def _parse_table_date(table_name: str) -> datetime | None:
    """
    Parses month and year from ESSL partition table names.

    ESSL uses two naming formats:
      DeviceLogs_5_2026   (month number underscore year)
      DeviceLogs_5-2026   (month number dash year)

    Returns a datetime(year, month, 1) or None if unparseable.
    """
    # Try both separators: underscore and dash
    match = re.search(r'DeviceLogs[_](\d{1,2})[_\-](\d{4})$', table_name, re.IGNORECASE)
    if match:
        month, year = int(match.group(1)), int(match.group(2))
        if 1 <= month <= 12:
            return datetime(year, month, 1)
    return None


def discover_partition_tables() -> list[str]:
    """
    Queries INFORMATION_SCHEMA to find all DeviceLogs_* partition tables.
    Returns table names sorted chronologically — oldest first.
    Automatically handles new tables appearing at month rollover.
    """
    sql = """
        SELECT TABLE_NAME
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_NAME LIKE 'DeviceLogs[_]%'
          AND TABLE_TYPE = 'BASE TABLE'
    """
    with get_connection() as conn:
        rows = conn.execute(sql).fetchall()

    tables = []
    for row in rows:
        name = row[0]
        dt = _parse_table_date(name)
        if dt:
            tables.append((dt, name))
        else:
            log.warning("Could not parse date from table name '%s' — skipping.", name)

    # Sort chronologically so we process oldest data first
    tables.sort(key=lambda x: x[0])
    result = [name for _, name in tables]
    log.info("Discovered %d partition table(s): %s", len(result), result)
    return result


def get_active_tables() -> list[str]:
    """
    Returns only the tables we should actively sync:
    - Current month's table
    - Previous month's table (within the overlap window for late device syncs)
    """
    all_tables = discover_partition_tables()
    if not all_tables:
        return []

    now = datetime.now()
    cutoff = now - timedelta(days=config.MONTH_OVERLAP_DAYS)

    active = []
    for name in all_tables:
        dt = _parse_table_date(name)
        if dt and dt >= datetime(cutoff.year, cutoff.month, 1):
            active.append(name)

    # Always include at least the last two tables as a safety net
    if len(active) == 0 and all_tables:
        active = all_tables[-2:]
    elif len(active) == 1 and len(all_tables) >= 2:
        # Include previous table too
        last_idx = all_tables.index(active[0])
        if last_idx > 0:
            active.insert(0, all_tables[last_idx - 1])

    log.info("Active tables for this sync cycle: %s", active)
    return active


# ── Punch data fetching ───────────────────────────────────────────────────────

def fetch_punches(
    table_name: str,
    last_synced_at: str,
    last_log_id: int,
    batch_size: int = 500,
) -> list[dict]:
    """
    Fetches unsynced punch rows from a specific partition table.

    Uses a compound cursor (CreatedDate + PK) to handle the edge case
    where multiple rows share the exact same CreatedDate.

    PK column is auto-detected per table — production ESSL uses 'DeviceLogId'
    while test/dummy tables may use 'Id'. Both are aliased to 'DeviceLogId'
    so all downstream code (processor.py, sync.py) works identically.

    Returns rows ordered by CreatedDate ASC, PK ASC
    so the cursor always advances forward safely.
    """
    # Table name cannot be parameterised in MSSQL — it is validated by
    # coming exclusively from INFORMATION_SCHEMA in discover_partition_tables()
    with get_connection() as conn:
        pk = _get_pk_column(conn, table_name)

        sql = f"""
            SELECT TOP (?)
                {pk} AS DeviceLogId,
                DeviceId,
                UserId,
                LogDate,
                Direction,
                AttDirection,
                Latitude,
                Longitude,
                CreatedDate
            FROM dbo.[{table_name}]
            WHERE
                UserId IS NOT NULL
                AND UserId != ''
                AND (
                    CreatedDate > ?
                    OR (CreatedDate = ? AND {pk} > ?)
                )
            ORDER BY CreatedDate ASC, {pk} ASC
        """

        cursor = conn.execute(sql, (
            batch_size,
            last_synced_at,
            last_synced_at,
            last_log_id,
        ))
        columns = [col[0] for col in cursor.description]
        rows = []
        for row in cursor.fetchall():
            r = dict(zip(columns, row))
            # LogId alias kept for cursor tracking in sync.py
            r["LogId"]        = r["DeviceLogId"]
            # Attach source table so processor.py can pass it to HRMS
            r["source_table"] = table_name
            # Normalise datetime objects to ISO strings for JSON serialisation
            for key in ("LogDate", "CreatedDate"):
                if isinstance(r.get(key), datetime):
                    r[key] = r[key].strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            rows.append(r)

    log.debug(
        "Fetched %d rows from '%s' after cursor (%s, id=%d)",
        len(rows), table_name, last_synced_at, last_log_id
    )
    return rows




def fetch_devices() -> list[dict]:
    """
    Fetches all active devices from ESSL dbo.Devices table.

    Returns a list of device dicts ready to push to HRMS.
    Called by the device sync cycle — separate from punch sync.

    Fields mapped:
      DeviceId       → device_code (cast to string)
      DeviceFName    → device_name (primary name)
      DevicesName    → device_name fallback if DeviceFName is blank
      DeviceLocation → door_address
      DeviceType     → device_type
      IpAddress      → stored in meta_data
      LastLogDownloadDate → last_seen_at in meta_data
    """
    sql = """
        SELECT
            DeviceId,
            DeviceFName,
            DevicesName,
            DeviceLocation,
            DeviceType,
            IpAddress,
            LastLogDownloadDate,
            Timezone
        FROM dbo.Devices
        WHERE DeviceId IS NOT NULL
        ORDER BY DeviceId ASC
    """
    with get_connection() as conn:
        cursor = conn.execute(sql)
        columns = [col[0] for col in cursor.description]
        rows = []
        for row in cursor.fetchall():
            r = dict(zip(columns, row))

            # Normalise LastLogDownloadDate to ISO string
            if isinstance(r.get("LastLogDownloadDate"), datetime):
                r["LastLogDownloadDate"] = r["LastLogDownloadDate"].strftime(
                    "%Y-%m-%d %H:%M:%S"
                )

            # Build clean device dict
            device_name = (
                (r.get("DeviceFName") or "").strip()
                or (r.get("DevicesName") or "").strip()
                or f"Device-{r['DeviceId']}"
            )

            rows.append({
                "device_code":  str(r["DeviceId"]),
                "device_name":  device_name,
                "door_address": (r.get("DeviceLocation") or "").strip() or None,
                "device_type":  (r.get("DeviceType") or "").strip() or None,
                "meta_data": {
                    "ip_address":    r.get("IpAddress"),
                    "last_log_date": r.get("LastLogDownloadDate"),
                    "timezone":      r.get("Timezone"),
                    "essl_device_id": r["DeviceId"],
                },
            })

    log.info("Fetched %d devices from ESSL dbo.Devices", len(rows))
    return rows
