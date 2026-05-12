"""
core/sync.py
The heart of the agent.

Orchestrates the full pipeline for one sync cycle:
  1. Discover active ESSL partition tables
  2. For each table:
       a. Read cursor from SQLite
       b. Fetch batch of raw punches from ESSL
       c. Normalise rows
       d. Push to HRMS API
       e. Advance cursor on success
       f. Mark batch in audit trail
  3. Log cycle summary
"""
import config
import cursor as cursor_store
from processor import normalise_batch
import essl as essl_db
import hrms as hrms_client
from logger import get_logger

log = get_logger(__name__)


def _sync_table(table_name: str) -> dict:
    """
    Runs the full fetch → normalise → push pipeline for one partition table.
    Processes in batches until no more new rows exist.

    Returns a summary dict for logging.
    """
    summary = {
        "table":    table_name,
        "fetched":  0,
        "pushed":   0,
        "skipped":  0,
        "batches":  0,
        "errors":   [],
    }

    while True:
        # ── Step 1: Read current cursor ──────────────────────────────────────
        cur = cursor_store.get_cursor(table_name)
        last_synced_at = cur["last_synced_at"]
        last_log_id    = cur["last_log_id"]

        # ── Step 2: Fetch next batch from ESSL ───────────────────────────────
        try:
            raw_rows = essl_db.fetch_punches(
                table_name     = table_name,
                last_synced_at = last_synced_at,
                last_log_id    = last_log_id,
                batch_size     = config.BATCH_SIZE,
            )
        except Exception as e:
            msg = f"ESSL fetch error on '{table_name}': {e}"
            log.error(msg)
            summary["errors"].append(msg)
            break  # stop processing this table, move to next

        if not raw_rows:
            log.debug("No new rows in '%s' — cursor up to date.", table_name)
            break  # this table is fully synced for this cycle

        summary["fetched"] += len(raw_rows)

        # ── Step 3: Normalise ─────────────────────────────────────────────────
        valid_punches, skipped = normalise_batch(raw_rows)
        summary["skipped"] += len(skipped)

        if not valid_punches:
            # All rows in batch were invalid — advance cursor past them anyway
            # so we don't loop forever on bad data
            max_created = max(r["CreatedDate"] for r in raw_rows)
            max_log_id  = max(r["DeviceLogId"]  for r in raw_rows)
            cursor_store.advance_cursor(table_name, str(max_created), max_log_id, 0)
            continue

        # ── Step 4: Record batch in audit trail ───────────────────────────────
        batch_id = cursor_store.record_batch(
            table_name     = table_name,
            batch_start_id = valid_punches[0]["essl_log_id"],
            batch_end_id   = valid_punches[-1]["essl_log_id"],
            record_count   = len(valid_punches),
        )

        # ── Step 5: Push to HRMS ──────────────────────────────────────────────
        try:
            hrms_client.push_punches(valid_punches)
            cursor_store.mark_batch_pushed(batch_id)
            summary["pushed"]  += len(valid_punches)
            summary["batches"] += 1

        except Exception as e:
            msg = f"HRMS push error (batch {batch_id}): {e}"
            log.error(msg)
            cursor_store.mark_batch_failed(batch_id, str(e))
            summary["errors"].append(msg)
            # Stop processing this table on push failure —
            # cursor stays where it was, so we retry same batch next cycle
            break

        # ── Step 6: Advance cursor to end of this batch ───────────────────────
        # NOTE: max() on ISO datetime strings is safe here because the format
        # YYYY-MM-DD HH:MM:SS.mmm is lexicographically sortable
        max_created = max(r["raw_created_at"] for r in valid_punches)
        max_log_id  = max(r["essl_log_id"]    for r in valid_punches)
        cursor_store.advance_cursor(
            table_name, max_created, max_log_id, len(valid_punches)
        )

        log.info(
            "[%s] Batch pushed: %d punches | cursor → (%s, id=%d)",
            table_name, len(valid_punches), max_created, max_log_id
        )

        # If we got fewer rows than batch_size, this table is fully caught up
        if len(raw_rows) < config.BATCH_SIZE:
            break

    return summary


def run_sync_cycle() -> None:
    """
    Entry point called by the scheduler every N seconds.
    Wraps the inner cycle in a top-level exception handler so that
    APScheduler never silently swallows an unhandled crash —
    the job will always log and continue running on the next interval.
    """
    try:
        _run_sync_cycle_inner()
    except Exception as e:
        log.critical(
            "Unhandled exception in sync cycle — agent will retry next interval: %s",
            e,
            exc_info=True,
        )


def _run_sync_cycle_inner() -> None:
    """
    Processes all active partition tables in chronological order.
    Called exclusively by run_sync_cycle().
    """
    log.info("═" * 60)
    log.info("Sync cycle started.")

    try:
        active_tables = essl_db.get_active_tables()
    except Exception as e:
        log.error("Failed to discover partition tables: %s", e)
        return

    if not active_tables:
        log.warning("No active ESSL partition tables found.")
        return

    total_pushed  = 0
    total_skipped = 0
    total_errors  = 0

    for table in active_tables:
        log.info("Processing table: %s", table)
        summary = _sync_table(table)

        total_pushed  += summary["pushed"]
        total_skipped += summary["skipped"]
        total_errors  += len(summary["errors"])

        if summary["errors"]:
            for err in summary["errors"]:
                log.error("  ✗ %s", err)

    log.info(
        "Sync cycle complete — pushed: %d | skipped: %d | errors: %d",
        total_pushed, total_skipped, total_errors
    )

    # Print cursor state for visibility
    for stat in cursor_store.get_stats():
        log.info(
            "  Cursor [%s] → %s (total synced: %d)",
            stat["table_name"], stat["last_synced_at"], stat["total_synced"]
        )

    log.info("═" * 60)