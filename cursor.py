"""
core/cursor.py
Manages sync state in a local SQLite file.

Tables:
  sync_cursors  — one row per ESSL partition table, tracks how far we've read
  sync_batches  — audit trail of every push attempt (pending/pushed/failed)
"""
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from typing import Optional

import config
from logger import get_logger

log = get_logger(__name__)

# Epoch used as "never synced" sentinel — before any real ESSL data
_EPOCH = "1970-01-01 00:00:00.000"


@contextmanager
def _conn():
    con = sqlite3.connect(config.STATE_DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES)
    con.row_factory = sqlite3.Row
    try:
        yield con
        con.commit()
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()


def init_db() -> None:
    """Create state tables if they don't exist. Called once at agent startup."""
    with _conn() as con:
        con.executescript("""
            CREATE TABLE IF NOT EXISTS sync_cursors (
                table_name      TEXT PRIMARY KEY,
                last_synced_at  TEXT NOT NULL DEFAULT '1970-01-01 00:00:00.000',
                last_log_id     INTEGER NOT NULL DEFAULT 0,
                total_synced    INTEGER NOT NULL DEFAULT 0,
                updated_at      TEXT NOT NULL DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS sync_batches (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                table_name      TEXT NOT NULL,
                batch_start_id  INTEGER NOT NULL,
                batch_end_id    INTEGER NOT NULL,
                record_count    INTEGER NOT NULL,
                status          TEXT NOT NULL DEFAULT 'pending',
                error_message   TEXT,
                created_at      TEXT NOT NULL DEFAULT (datetime('now')),
                updated_at      TEXT NOT NULL DEFAULT (datetime('now'))
            );
        """)
    log.info("State DB initialised at '%s'", config.STATE_DB_PATH)


# ── Cursor operations ─────────────────────────────────────────────────────────

def get_cursor(table_name: str) -> dict:
    """
    Returns the current cursor for a partition table.
    Creates a fresh zero-cursor if this table has never been seen before.
    """
    with _conn() as con:
        row = con.execute(
            "SELECT * FROM sync_cursors WHERE table_name = ?", (table_name,)
        ).fetchone()

        if row is None:
            con.execute(
                "INSERT INTO sync_cursors (table_name) VALUES (?)", (table_name,)
            )
            log.info("New partition table detected: '%s' — cursor initialised.", table_name)
            return {
                "table_name":     table_name,
                "last_synced_at": _EPOCH,
                "last_log_id":    0,
                "total_synced":   0,
            }

        return dict(row)


def advance_cursor(
    table_name: str,
    last_synced_at: str,
    last_log_id: int,
    records_pushed: int
) -> None:
    """Move the cursor forward after a successful push."""
    with _conn() as con:
        con.execute("""
            UPDATE sync_cursors
            SET last_synced_at = ?,
                last_log_id    = ?,
                total_synced   = total_synced + ?,
                updated_at     = datetime('now')
            WHERE table_name = ?
        """, (last_synced_at, last_log_id, records_pushed, table_name))


# ── Batch audit trail ─────────────────────────────────────────────────────────

def record_batch(
    table_name: str,
    batch_start_id: int,
    batch_end_id: int,
    record_count: int,
) -> int:
    """Insert a pending batch record. Returns the batch id."""
    with _conn() as con:
        cur = con.execute("""
            INSERT INTO sync_batches
                (table_name, batch_start_id, batch_end_id, record_count, status)
            VALUES (?, ?, ?, ?, 'pending')
        """, (table_name, batch_start_id, batch_end_id, record_count))
        return cur.lastrowid


def mark_batch_pushed(batch_id: int) -> None:
    with _conn() as con:
        con.execute("""
            UPDATE sync_batches
            SET status = 'pushed', updated_at = datetime('now')
            WHERE id = ?
        """, (batch_id,))


def mark_batch_failed(batch_id: int, error: str) -> None:
    with _conn() as con:
        con.execute("""
            UPDATE sync_batches
            SET status = 'failed',
                error_message = ?,
                updated_at = datetime('now')
            WHERE id = ?
        """, (error[:1000], batch_id))


def get_stats() -> list[dict]:
    """Returns a summary of all cursors — useful for health logging."""
    with _conn() as con:
        rows = con.execute(
            "SELECT * FROM sync_cursors ORDER BY table_name"
        ).fetchall()
        return [dict(r) for r in rows]


def reset_cursor(table_name: str = None) -> None:
    """
    Reset cursor state.
    - Pass a table_name to reset only that table.
    - Pass nothing (or None) to reset ALL tables.
    """
    with _conn() as con:
        if table_name:
            con.execute("DELETE FROM sync_cursors WHERE table_name = ?", (table_name,))
            con.execute("DELETE FROM sync_batches WHERE table_name = ?", (table_name,))
            log.info("Cursor reset for table: '%s'", table_name)
        else:
            con.execute("DELETE FROM sync_cursors")
            con.execute("DELETE FROM sync_batches")
            log.info("All cursors reset.")