#!/usr/bin/env python3
"""
Main entry point for launching the RFQ Tracker Dashboard application.
"""

import sys
import json
import logging
import argparse
from PyQt6.QtWidgets import QApplication

from rfq_tracker.db_manager import DBManager
from dashboard.main_window import MainWindow

def main():
    """
    Parses arguments, sets up connections, and launches the PyQt6 application.
    """
    parser = argparse.ArgumentParser(description="RFQ Tracker Dashboard")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run with mock data without connecting to MongoDB."
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    app = QApplication(sys.argv)

    db_manager = None
    if not args.dry_run:
        try:
            with open("config.json") as f:
                config = json.load(f)
            db_manager = DBManager(
                mongo_uri=config.get("mongo_uri"),
                db_name=config.get("mongo_db")
            )
            db_manager.connect()
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logging.error(f"Failed to load config or connect to DB: {e}")
            # Optionally, show a message box to the user
            sys.exit(1)

    window = MainWindow(db_manager, dry_run=args.dry_run)
    window.show()

    exit_code = app.exec()

    if db_manager:
        db_manager.close()

    sys.exit(exit_code)

if __name__ == "__main__":
    main()