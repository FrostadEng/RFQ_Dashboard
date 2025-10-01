"""
Core crawler logic for scanning RFQ metadata from project directories.
"""

import sys
import json
import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Any

from .db_manager import DBManager

logger = logging.getLogger(__name__)


class RFQCrawler:
    """Main crawler class for extracting RFQ metadata from project folders."""

    def __init__(self, config: Dict[str, Any], db_manager: DBManager, dry_run: bool = False):
        """
        Initialize the RFQ Crawler.

        Args:
            config: A dictionary containing configuration settings.
            db_manager: An instance of DBManager to handle database operations.
            dry_run: If True, simulates a run without writing to the database.
        """
        self.root_path = Path(config.get("root_path", "."))
        self.filter_tags = config.get("filter_tags", ["Template", "archive"])
        self.file_filter_tags = config.get("file_filter_tags", [".db"])
        self.db_manager = db_manager
        self.dry_run = dry_run

        # RFQ folder names to search for (case-insensitive)
        self.rfq_folder_names = ["RFQ", "Supplier RFQ", "Contractor"]

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

    def process_submission_folder(self, folder_path: Path, project_number: str,
                                  supplier_name: str, folder_type: str) -> List[Dict[str, Any]]:
        """
        Process a submission folder (Sent or Received) to extract metadata.

        Args:
            folder_path: Path to Sent or Received folder
            project_number: Project number
            supplier_name: Supplier name
            folder_type: "sent" or "received"

        Returns:
            List of submission dictionaries
        """
        submissions = []

        if not folder_path.exists():
            return submissions

        # Iterate through submission folders
        for submission_folder in folder_path.iterdir():
            if submission_folder.is_dir():
                # Skip filtered folders
                if self.should_skip_folder(submission_folder.name):
                    continue

                submission = {
                    "project_number": project_number,
                    "supplier_name": supplier_name,
                    "type": folder_type,  # "sent" or "received"
                    "folder_name": submission_folder.name,
                    "folder_path": str(submission_folder),
                    "date": self.get_file_creation_time(submission_folder),
                    "files": [
                        str(f) for f in submission_folder.rglob("*")
                        if f.is_file() and not self.should_skip_file(f.name)
                    ]
                }

                submissions.append(submission)
                logger.debug(f"Found {len(submission['files'])} files in {folder_type} folder {submission_folder.name}")

        logger.info(f"Found {len(submissions)} {folder_type} submissions in {folder_path}")
        return submissions

    def process_supplier_folder(self, supplier_folder: Path,
                              project_number: str) -> Dict[str, Any]:
        """Process a single supplier folder."""
        supplier_name = supplier_folder.name
        logger.info(f"Processing supplier: {supplier_name} in project {project_number}")

        supplier_doc = {
            "project_number": project_number,
            "supplier_name": supplier_name,
            "path": str(supplier_folder)
        }

        # Process Sent and Received folders identically
        sent_submissions = self.process_submission_folder(
            supplier_folder / "Sent", project_number, supplier_name, "sent"
        )

        received_submissions = self.process_submission_folder(
            supplier_folder / "Received", project_number, supplier_name, "received"
        )

        # Combine into single submissions list
        all_submissions = sent_submissions + received_submissions

        return {
            "supplier": supplier_doc,
            "submissions": all_submissions  # Single list instead of separate transmissions/receipts
        }

    def process_project_folder(self, project_folder: Path) -> Dict[str, Any]:
        """Process a single project folder."""
        project_number = project_folder.name
        logger.info(f"Processing project: {project_number}")

        project_doc = {
            "project_number": project_number,
            "path": str(project_folder),
            "last_scanned": datetime.now(timezone.utc).isoformat()
        }

        all_suppliers, all_submissions = [], []

        for rfq_folder in self.find_rfq_folders(project_folder):
            for supplier_folder in rfq_folder.iterdir():
                if supplier_folder.is_dir() and not self.should_skip_folder(supplier_folder.name):
                    result = self.process_supplier_folder(supplier_folder, project_number)
                    all_suppliers.append(result["supplier"])
                    all_submissions.extend(result["submissions"])

        return {
            "project": project_doc,
            "suppliers": all_suppliers,
            "submissions": all_submissions
        }

    def crawl(self):
        """Main crawling method."""
        if not self.root_path.is_dir():
            logger.error(f"Root path is not a valid directory: {self.root_path}")
            return

        if not self.dry_run:
            self.db_manager.connect()

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
                    if self.dry_run:
                        logger.info(f"Dry Run: Would save data for project {project_data['project']['project_number']}")
                        logger.info(f"Project: {json.dumps(project_data['project'], indent=2)}")
                        logger.info(f"Suppliers: {json.dumps(project_data['suppliers'], indent=2)}")
                        logger.info(f"Transmissions: {json.dumps(project_data['transmissions'], indent=2)}")
                        logger.info(f"Receipts: {json.dumps(project_data['receipts'], indent=2)}")
                    else:
                        self.db_manager.save_project_data(project_data)
                    project_count += 1

        logger.info(f"Crawl complete. Processed {project_count} projects.")

        if not self.dry_run:
            self.db_manager.close()