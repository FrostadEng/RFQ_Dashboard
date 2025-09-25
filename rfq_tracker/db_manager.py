import sys
import logging
from pymongo import MongoClient, UpdateOne
from pymongo.errors import ConnectionFailure

logger = logging.getLogger(__name__)

class DBManager:
    """Manages all interactions with the MongoDB database."""

    def __init__(self, mongo_uri: str, db_name: str):
        self.mongo_uri = mongo_uri
        self.db_name = db_name
        self.client = None
        self.db = None

    def connect(self):
        """Connect to the MongoDB instance and ensure indexes exist."""
        try:
            self.client = MongoClient(self.mongo_uri)
            # The ismaster command is cheap and does not require auth.
            self.client.admin.command('ismaster')
            self.db = self.client[self.db_name]
            logger.info(f"Successfully connected to MongoDB database '{self.db_name}'")
            self._ensure_indexes()
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            sys.exit(1)

    def _ensure_indexes(self):
        """Ensure all required indexes exist for efficient queries and upserts."""
        self.db.projects.create_index("project_number", unique=True)
        self.db.suppliers.create_index([("project_number", 1), ("supplier_name", 1)], unique=True)
        self.db.transmissions.create_index("zip_path", unique=True)
        self.db.receipts.create_index("received_folder_path", unique=True)
        logger.info("Database indexes ensured.")

    def save_project_data(self, data: dict):
        """
        Save all extracted data for a single project using an upsert strategy.
        This includes project details, suppliers, transmissions, and receipts.
        """
        if self.db is None:
            logger.error("Database not connected. Cannot save data.")
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

    def close(self):
        """Close the MongoDB connection."""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed.")