#!/usr/bin/env python3
"""
Command-line entry point for running the RFQ Metadata Crawler.
"""

import sys
import json
import logging
import argparse
import os
from typing import Dict, Any

from rfq_tracker.crawler import RFQCrawler
from rfq_tracker.db_manager import DBManager

def load_config(config_path: str) -> Dict[str, Any]:
    """Load configuration from a JSON file."""
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
            logging.info(f"Loaded configuration from {config_path}")
            return config
    except FileNotFoundError:
        logging.warning(f"Config file '{config_path}' not found. Using defaults.")
        return {}
    except json.JSONDecodeError as e:
        logging.error(f"Error parsing config file: {e}. Using defaults.")
        return {}

def main():
    """Main entry point with command-line argument parsing."""
    parser = argparse.ArgumentParser(
        description="RFQ Metadata Crawler for project directories.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "--config",
        default="config.json",
        help="Path to the JSON configuration file (default: config.json)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate a crawl without writing to the database."
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging."
    )
    args = parser.parse_args()

    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    config = load_config(args.config)

    # Override with environment variables if they exist
    mongo_uri = os.getenv('MONGO_URI', config.get("mongo_uri", "mongodb://localhost:27017"))
    mongo_db = os.getenv('MONGO_DB', config.get("mongo_db", "rfq_tracker"))

    db_manager = DBManager(
        mongo_uri=mongo_uri,
        db_name=mongo_db
    )

    crawler = RFQCrawler(config=config, db_manager=db_manager, dry_run=args.dry_run)

    try:
        crawler.crawl()
        logging.info("Crawling completed successfully.")
    except KeyboardInterrupt:
        logging.info("Crawling interrupted by user.")
        sys.exit(0)
    except Exception as e:
        logging.error(f"An unexpected error occurred during crawling: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()