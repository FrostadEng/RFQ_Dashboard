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
            # Skip for mongomock which doesn't support this command
            try:
                self.client.admin.command('ismaster')
            except Exception:
                # Mongomock or other test environments may not support ismaster
                pass
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

        # partner_type indexes for efficient filtering
        self.db.suppliers.create_index("partner_type")
        self.db.submissions.create_index("partner_type")

        # Compound indexes with partner_type for filtered queries
        self.db.suppliers.create_index([("project_number", 1), ("partner_type", 1)])
        self.db.submissions.create_index([("project_number", 1), ("partner_type", 1)])
        self.db.submissions.create_index([("project_number", 1), ("partner_type", 1), ("type", 1)])

        # Unified submissions collection with type field
        self.db.submissions.create_index([("project_number", 1), ("supplier_name", 1), ("type", 1)])
        self.db.submissions.create_index([("project_number", 1), ("supplier_name", 1), ("folder_name", 1), ("content_hash", 1)], unique=True)
        # Index for efficient version lookups
        self.db.submissions.create_index([("project_number", 1), ("supplier_name", 1), ("folder_name", 1), ("date", -1)])
        logger.info("Database indexes ensured.")

    def save_project_data(self, data: dict):
        """
        Save all extracted data for a single project using an upsert strategy.
        This includes project details, suppliers, and submissions.
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

            # Bulk upsert suppliers with partner_type default
            if data["suppliers"]:
                for s in data["suppliers"]:
                    # Ensure partner_type has default value
                    supplier_doc = s.copy()
                    if "partner_type" not in supplier_doc:
                        supplier_doc["partner_type"] = "Supplier"

                    self.db.suppliers.update_one(
                        {"project_number": supplier_doc["project_number"], "supplier_name": supplier_doc["supplier_name"]},
                        {"$set": supplier_doc},
                        upsert=True
                    )

            # Content-aware versioning for submissions with partner_type default
            if data["submissions"]:
                for sub in data["submissions"]:
                    # Ensure partner_type has default value
                    if "partner_type" not in sub:
                        sub["partner_type"] = "Supplier"

                    # Check if this exact content already exists
                    existing = self.db.submissions.find_one({
                        "project_number": sub["project_number"],
                        "supplier_name": sub["supplier_name"],
                        "folder_name": sub["folder_name"],
                        "content_hash": sub["content_hash"]
                    })

                    if existing:
                        # Content unchanged - optionally update last_checked timestamp
                        self.db.submissions.update_one(
                            {"_id": existing["_id"]},
                            {"$set": {"last_checked": sub["date"]}}
                        )
                        logger.debug(f"Skipped duplicate: {sub['folder_name']} (hash: {sub['content_hash'][:8]}...)")
                    else:
                        # New version - insert it
                        self.db.submissions.insert_one(sub)
                        logger.debug(f"Inserted new version: {sub['folder_name']} (hash: {sub['content_hash'][:8]}...)")

            logger.info(f"Processed data for project {data['project']['project_number']}")

        except Exception as e:
            logger.error(f"Error saving to MongoDB for project {data.get('project', {}).get('project_number')}: {e}")

    def close(self):
        """Close the MongoDB connection."""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed.")