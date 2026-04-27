"""
GamblingApp – Main Entry Point
================================
Bootstraps the database schema and launches the interactive terminal menu.

Usage:
    python main.py              # Interactive menu
    python main.py --demo       # Run automated demo (no DB required)
    python main.py --test-db    # Test DB connection only
"""
from __future__ import annotations

import argparse
import logging
import sys

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="GamblingApp")
    parser.add_argument("--demo",     action="store_true", help="Run offline demo")
    parser.add_argument("--test-db",  action="store_true", help="Test DB connection only")
    parser.add_argument("--host",     default=None)
    parser.add_argument("--port",     default=None, type=int)
    parser.add_argument("--user",     default=None)
    parser.add_argument("--password", default=None)
    parser.add_argument("--database", default=None)
    return parser.parse_args()


def _apply_db_overrides(args: argparse.Namespace) -> None:
    import os
    if args.host:     os.environ["DB_HOST"]     = args.host
    if args.port:     os.environ["DB_PORT"]     = str(args.port)
    if args.user:     os.environ["DB_USER"]     = args.user
    if args.password: os.environ["DB_PASSWORD"] = args.password
    if args.database: os.environ["DB_NAME"]     = args.database


def _run_demo() -> None:
    from app.demo.demo_app import run_demo
    run_demo()


def _test_db() -> None:
    from app.config.db_config import DatabaseConfig
    print("\n  Testing MySQL connection …")
    ok, msg = DatabaseConfig.test_connection()
    if ok:
        print(f"  OK: {msg}")
    else:
        print(f"  FAILED: {msg}")
        sys.exit(1)


def _init_db() -> bool:
    from app.config.db_config import DatabaseConfig
    try:
        DatabaseConfig.initialize_schema()
        return True
    except Exception as exc:
        logger.error("DB init failed: %s", exc)
        return False


def _offer_demo_fallback() -> None:
    try:
        choice = input("  Run automated demo instead? [y/N]: ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        return
    if choice == "y":
        _run_demo()


def _run_interactive() -> None:
    from app.ui.interactive_menu import InteractiveMenu

    print("\n" + "═" * 60)
    print("  🎰  GAMBLING SIMULATION APPLICATION")
    print("═" * 60)
    print("  Connecting to MySQL …", end=" ", flush=True)

    if not _init_db():
        print("FAILED\n")
        print("  ⚠️  Could not connect to MySQL.")
        print("  Make sure MySQL is running and credentials are correct.")
        print("  You can override defaults with CLI flags or env vars:")
        print("    DB_HOST  DB_PORT  DB_USER  DB_PASSWORD  DB_NAME")
        print()
        _offer_demo_fallback()
        return

    print("OK ✅\n")

    menu = InteractiveMenu()
    menu.run()


def main() -> None:
    args = _parse_args()
    _apply_db_overrides(args)

    try:
        if args.test_db:
            _test_db()
        elif args.demo:
            _run_demo()
        else:
            _run_interactive()
    except KeyboardInterrupt:
        print("\n\n  👋  Goodbye!\n")
        sys.exit(0)


if __name__ == "__main__":
    main()