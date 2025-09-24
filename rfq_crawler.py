#!/usr/bin/env python3
"""
RFQ Metadata Crawler
Scans project directories for RFQ transmissions and stores metadata in MongoDB.

This enhanced version uses an "upsert" strategy to avoid data loss during
scans and supports flexible configuration via 'config.json'.

Example config.json:
{
  "filter_tags": ["Template", "archive"],
  "mongo_uri": "mongodb://localhost:27017",
  "mongo_db": "rfq_tracker"
}
"""

import os
import sys
import json
import logging
import argparse
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
import pymongo
from pymongo import MongoClient, UpdateOne

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RFQCrawler:
    """Main crawler class for extracting RFQ metadata from project folders."""

    def __init__(self, root_path: str, config_path: str = "config.json", dry_run: bool = False):
        """
        Initialize the RFQ Crawler.

        Args:
            root_path: Root directory to scan for projects.
            config_path: Path to configuration file.
            dry_run: If True, simulates a run without writing to the database.
        """
        self.root_path = Path(root_path)
        self.config = self._load_config(config_path)
        self.filter_tags = self.config.get("filter_tags", ["Template", "archive"])
        self.file_filter_tags = self.config.get("file_filter_tags", [".db", ".zip"])
        self.mongo_uri = self.config.get("mongo_uri", "mongodb://localhost:27017")
        self.mongo_db_name = self.config.get("mongo_db", "rfq_tracker")
        self.db_client = None
        self.db = None
        self.dry_run = dry_run

        # RFQ folder names to search for (case-insensitive)
        self.rfq_folder_names = ["RFQ", "Supplier RFQ", "Contractor"]

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                logger.info(f"Loaded configuration from {config_path}")
                return config
        except FileNotFoundError:
            logger.warning(f"Config file '{config_path}' not found. Using defaults.")
            return {}
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing config file: {e}. Using defaults.")
            return {}

    def connect_to_mongodb(self):
        """Connect to MongoDB instance and ensure indexes exist."""
        if self.dry_run:
            logger.info("Dry run enabled. Skipping MongoDB connection.")
            return
        try:
            self.db_client = MongoClient(self.mongo_uri)
            self.db = self.db_client[self.mongo_db_name]

            # Test connection
            self.db_client.server_info()
            logger.info(f"Successfully connected to MongoDB database '{self.mongo_db_name}'")

            # Ensure indexes exist for efficient queries and upserts
            self.db.projects.create_index("project_number", unique=True)
            self.db.suppliers.create_index([("project_number", 1), ("supplier_name", 1)], unique=True)
            self.db.transmissions.create_index("zip_path", unique=True)
            self.db.receipts.create_index("received_folder_path", unique=True)
            logger.info("Database indexes ensured.")

        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            sys.exit(1)

    def is_project_folder(self, folder_name: str) -> bool:
        """Check if folder name consists entirely of digits."""
        return folder_name.isdigit()

    def should_skip_folder(self, folder_name: str) -> bool:
        """Check if folder should be skipped based on filter tags."""
        return any(tag.lower() in folder_name.lower() for tag in self.filter_tags)

    def should_skip_file(self, file_name: str) -> bool:
        """Check if a file should be skipped based on its extension."""
        return any(file_name.lower().endswith(ext) for ext in self.file_filter_tags)

    def find_rfq_folders(self, project_path: Path) -> List[Path]:
        """Find RFQ-related folders within a project folder."""
        rfq_folders = []
        try:
            for item in project_path.iterdir():
                if item.is_dir():
                    if any(rfq_name.lower() == item.name.lower() for rfq_name in self.rfq_folder_names):
                        rfq_folders.append(item)
                        logger.debug(f"Found RFQ folder: {item}")
        except FileNotFoundError:
            logger.warning(f"Project path {project_path} not found during RFQ folder search.")
        return rfq_folders

    def get_file_creation_time(self, file_path: Path) -> str:
        """Get file creation time as an ISO 8601 UTC string."""
        try:
            timestamp = file_path.stat().st_ctime
            dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
            return dt.isoformat()
        except Exception as e:
            logger.error(f"Error getting timestamp for {file_path}: {e}")
            return datetime.now(timezone.utc).isoformat()

    def process_sent_folder(self, sent_folder: Path, project_number: str,
                          supplier_name: str) -> List[Dict[str, Any]]:
        """Process Sent folder to extract transmission metadata."""
        transmissions = []
        if not sent_folder.exists():
            return transmissions

        for zip_file in sent_folder.glob("*.zip"):
            transmission = {
                "project_number": project_number,
                "supplier_name": supplier_name,
                "zip_name": zip_file.name,
                "zip_path": str(zip_file),
                "sent_date": self.get_file_creation_time(zip_file),
                "source_files": []
            }

            source_folder = sent_folder / zip_file.stem
            if source_folder.is_dir():
                transmission["source_files"] = [str(f) for f in source_folder.rglob("*") if f.is_file()]
                logger.debug(f"Found {len(transmission['source_files'])} source files for {zip_file.name}")

            transmissions.append(transmission)

        logger.info(f"Found {len(transmissions)} transmissions in {sent_folder}")
        return transmissions

    def process_received_folder(self, received_folder: Path, project_number: str,
                              supplier_name: str) -> List[Dict[str, Any]]:
        """Process Received folder to extract receipt metadata."""
        receipts = []
        if not received_folder.exists():
            return receipts

        for receipt_folder in received_folder.iterdir():
            if receipt_folder.is_dir():
                receipt = {
                    "project_number": project_number,
                    "supplier_name": supplier_name,
                    "received_folder_path": str(receipt_folder),
                    "received_date": self.get_file_creation_time(receipt_folder),
                    "received_files": [str(f) for f in receipt_folder.rglob("*") if f.is_file() and not self.should_skip_file(f.name)]
                }
                receipts.append(receipt)
                logger.debug(f"Found {len(receipt['received_files'])} files in receipt {receipt_folder.name}")

        logger.info(f"Found {len(receipts)} receipts in {received_folder}")
        return receipts

    def process_supplier_folder(self, supplier_folder: Path,
                              project_number: str) -> Dict[str, Any]:
        """Process a single supplier folder."""
        supplier_name = supplier_folder.name
        logger.info(f"Processing supplier: {supplier_name} in project {project_number}")

        supplier_doc = {"project_number": project_number, "supplier_name": supplier_name, "path": str(supplier_folder)}
        transmissions = self.process_sent_folder(supplier_folder / "Sent", project_number, supplier_name)
        receipts = self.process_received_folder(supplier_folder / "Received", project_number, supplier_name)

        return {"supplier": supplier_doc, "transmissions": transmissions, "receipts": receipts}

    def process_project_folder(self, project_folder: Path) -> Dict[str, Any]:
        """Process a single project folder."""
        project_number = project_folder.name
        logger.info(f"Processing project: {project_number}")

        project_doc = {
            "project_number": project_number,
            "path": str(project_folder),
            "last_scanned": datetime.now(timezone.utc).isoformat()
        }

        all_suppliers, all_transmissions, all_receipts = [], [], []

        for rfq_folder in self.find_rfq_folders(project_folder):
            for supplier_folder in rfq_folder.iterdir():
                if supplier_folder.is_dir() and not self.should_skip_folder(supplier_folder.name):
                    result = self.process_supplier_folder(supplier_folder, project_number)
                    all_suppliers.append(result["supplier"])
                    all_transmissions.extend(result["transmissions"])
                    all_receipts.extend(result["receipts"])

        return {
            "project": project_doc,
            "suppliers": all_suppliers,
            "transmissions": all_transmissions,
            "receipts": all_receipts
        }

    def save_to_mongodb(self, data: Dict[str, Any]):
        """Save extracted data to MongoDB using an upsert strategy."""
        if self.dry_run:
            logger.info(f"Dry Run: Would upsert data for project {data['project']['project_number']}")
            logger.info(f"Project: {json.dumps(data['project'], indent=2)}")
            logger.info(f"Suppliers: {json.dumps(data['suppliers'], indent=2)}")
            logger.info(f"Transmissions: {json.dumps(data['transmissions'], indent=2)}")
            logger.info(f"Receipts: {json.dumps(data['receipts'], indent=2)}")
            return

        try:
            # Upsert project
            if data["project"]:
                self.db.projects.replace_one(
                    {"project_number": data["project"]["project_number"]},
                    data["project"],
                    upsert=True
                )

            # Bulk upsert suppliers
            if data["suppliers"]:
                requests = [
                    UpdateOne(
                        {"project_number": s["project_number"], "supplier_name": s["supplier_name"]},
                        {"$set": s},
                        upsert=True
                    ) for s in data["suppliers"]
                ]
                self.db.suppliers.bulk_write(requests)

            # Bulk upsert transmissions
            if data["transmissions"]:
                requests = [
                    UpdateOne({"zip_path": t["zip_path"]}, {"$set": t}, upsert=True)
                    for t in data["transmissions"]
                ]
                self.db.transmissions.bulk_write(requests)

            # Bulk upsert receipts
            if data["receipts"]:
                requests = [
                    UpdateOne({"received_folder_path": r["received_folder_path"]}, {"$set": r}, upsert=True)
                    for r in data["receipts"]
                ]
                self.db.receipts.bulk_write(requests)

            logger.info(f"Upserted data for project {data['project']['project_number']}")

        except Exception as e:
            logger.error(f"Error saving to MongoDB for project {data.get('project', {}).get('project_number')}: {e}")

    def crawl(self):
        """Main crawling method."""
        if not self.root_path.is_dir():
            logger.error(f"Root path is not a valid directory: {self.root_path}")
            sys.exit(1)

        self.connect_to_mongodb()
        logger.info(f"Starting crawl from: {self.root_path}")
        logger.info(f"Folder filter tags: {self.filter_tags}")
        logger.info(f"File filter tags: {self.file_filter_tags}")

        project_count = 0
        for item in self.root_path.iterdir():
            if item.is_dir():
                if self.should_skip_folder(item.name):
                    logger.debug(f"Skipping filtered folder: {item.name}")
                    continue

                if self.is_project_folder(item.name):
                    project_data = self.process_project_folder(item)
                    self.save_to_mongodb(project_data)
                    project_count += 1

        logger.info(f"Crawl complete. Processed {project_count} projects.")

        if self.db_client:
            self.db_client.close()


def main():
    """Main entry point with command-line argument parsing."""
    parser = argparse.ArgumentParser(
        description="RFQ Metadata Crawler for project directories.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "root_path",
        help="The root directory to scan for projects.\nExample: S:\\SADNA\\SGTAC\\Projects"
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

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    crawler = RFQCrawler(args.root_path, config_path=args.config, dry_run=args.dry_run)

    try:
        crawler.crawl()
        logger.info("Crawling completed successfully.")
    except KeyboardInterrupt:
        logger.info("Crawling interrupted by user.")
        sys.exit(0)
    except Exception as e:
        logger.error(f"An unexpected error occurred during crawling: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
