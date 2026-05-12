"""
main.py
Entry point for the ESSL Agent.

Run modes:
  python main.py            — start the agent (runs forever)
  python main.py --once     — run a single sync cycle and exit (useful for testing)
  python main.py --test     — test connectivity to ESSL and HRMS, then exit
  python main.py --status   — print current cursor state and exit
"""
import argparse
import sys

import cursor as cursor_store
from sync import run_sync_cycle
import essl as essl_db
import hrms as hrms_client
from logger import get_logger
from scheduler import build_scheduler

log = get_logger("main")


def cmd_test() -> None:
    log.info("Testing connections...")
    essl_ok = essl_db.test_connection()
    hrms_ok = hrms_client.test_connection()

    if essl_ok:
        tables = essl_db.discover_partition_tables()
        log.info("ESSL partition tables found: %s", tables)

    if essl_ok and hrms_ok:
        log.info("✓ All connections OK.")
        sys.exit(0)
    else:
        log.error("✗ Connection test failed.")
        sys.exit(1)


def cmd_status() -> None:
    cursor_store.init_db()
    stats = cursor_store.get_stats()
    if not stats:
        log.info("No sync history yet.")
    else:
        log.info("Current cursor state:")
        for s in stats:
            log.info(
                "  [%s]  last_synced_at=%s  last_log_id=%d  total_synced=%d",
                s["table_name"], s["last_synced_at"],
                s["last_log_id"], s["total_synced"]
            )
    sys.exit(0)


def cmd_once() -> None:
    log.info("Running single sync cycle...")
    cursor_store.init_db()
    run_sync_cycle()
    log.info("Done.")
    sys.exit(0)


def cmd_start() -> None:
    log.info("▶  ESSL Agent starting up.")
    import config
    log.info("   ESSL Server : %s", config.ESSL_SERVER)
    log.info("   HRMS API    : %s",config.HRMS_API_BASE_URL)

    # Validate connections before starting the loop
    if not essl_db.test_connection():
        log.critical("Cannot reach ESSL SQL Server. Aborting.")
        sys.exit(1)

    if not hrms_client.test_connection():
        log.critical("Cannot reach HRMS API. Aborting.")
        sys.exit(1)

    # Initialise local state DB
    cursor_store.init_db()

    # Run one immediate cycle on startup so we don't wait the full interval
    log.info("Running initial sync before starting scheduler...")
    run_sync_cycle()

    # Start the scheduler (blocks forever)
    scheduler = build_scheduler()
    log.info("Scheduler running. Press Ctrl+C to stop.")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        log.info("Agent stopped by user.")
        scheduler.shutdown(wait=False)


def main() -> None:
    parser = argparse.ArgumentParser(description="ESSL → HRMS Attendance Sync Agent")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--once",   action="store_true")
    group.add_argument("--test",   action="store_true")
    group.add_argument("--status", action="store_true")
    group.add_argument("--reset",  metavar="TABLE", nargs="?", const="__all__")
    args = parser.parse_args()

    # Evaluate in priority order — all inside if/elif chain
    if args.test:
        cmd_test()
    elif args.status:
        cmd_status()
    elif args.reset:
        cursor_store.init_db()
        cursor_store.reset_cursor(None if args.reset == "__all__" else args.reset)
        log.info("Cursor reset complete.")
        sys.exit(0)
    elif args.once:
        cmd_once()
    else:
        cmd_start()


if __name__ == "__main__":
    main()
