import pytest
import mongomock
from unittest.mock import patch

from rfq_tracker.crawler import RFQCrawler
from rfq_tracker.db_manager import DBManager

# Mock configuration matching the one in unit tests for consistency
MOCK_CONFIG = {
    "root_path": "/mock_projects_root",
    "filter_tags": ["Template", "archive"],
    "file_filter_tags": [".db"],
    "rfq_folder_names": ["RFQ", "Supplier RFQ"]
}

MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "integration_test_db"

@pytest.fixture
def test_environment(fs):
    """
    Sets up a complete test environment with a fake file system,
    a real DBManager instance using mongomock, and a real RFQCrawler.
    """
    # 1. Set up the fake file system with a project structure
    root = MOCK_CONFIG["root_path"]
    # Project 1: Standard case
    fs.create_file(f"{root}/12345/RFQ/SupplierA/Sent/2023-01-01 Quote/quote.pdf")
    fs.create_file(f"{root}/12345/RFQ/SupplierA/Received/2023-01-10 Revision/response.pdf")
    # Project 2: Different RFQ folder name
    fs.create_file(f"{root}/67890/Supplier RFQ/SupplierB/Sent/2023-02-01 Request/request.zip")
    # Project 3: A folder to be skipped
    fs.create_dir(f"{root}/Project_Template")
    # Project 4: A project folder with no RFQ directory
    fs.create_dir(f"{root}/54321/Drawings")

    # 2. Set up the DBManager with mongomock
    # Directly assign mongomock client to db_manager to bypass MongoClient initialization
    db_manager = DBManager(mongo_uri=MONGO_URI, db_name=DB_NAME)
    db_manager.client = mongomock.MongoClient()
    db_manager.db = db_manager.client[DB_NAME]
    db_manager._ensure_indexes()

    # Override close method to prevent it from closing the client during fixture cleanup
    db_manager.close = lambda: None

    # 3. Set up the RFQCrawler
    crawler = RFQCrawler(config=MOCK_CONFIG, db_manager=db_manager)

    return crawler, db_manager

def test_full_pipeline(test_environment):
    """
    Tests the end-to-end pipeline from crawling the file system to saving in the database.
    """
    crawler, db_manager = test_environment

    # Run the full crawl and save process
    crawler.crawl()

    # --- Verification ---
    # Use the db_manager's database instance (already connected with mongomock)
    db = db_manager.db

    # 1. Verify Projects
    # Note: Project 54321 is also saved even though it has no RFQ folder
    assert db.projects.count_documents({}) == 3
    project_numbers = {p["project_number"] for p in db.projects.find()}
    assert project_numbers == {"12345", "67890", "54321"}
    
    proj_12345 = db.projects.find_one({"project_number": "12345"})
    assert proj_12345["path"] == f"{MOCK_CONFIG['root_path']}/12345"

    # 2. Verify Suppliers
    assert db.suppliers.count_documents({}) == 2
    supplier_names = {s["supplier_name"] for s in db.suppliers.find()}
    assert supplier_names == {"SupplierA", "SupplierB"}

    supplier_A = db.suppliers.find_one({"supplier_name": "SupplierA"})
    assert supplier_A["project_number"] == "12345"

    # 3. Verify Submissions
    assert db.submissions.count_documents({}) == 3
    
    # Check Supplier A's submissions
    sent_submission_A = db.submissions.find_one({"type": "sent", "supplier_name": "SupplierA"})
    assert sent_submission_A is not None
    assert sent_submission_A["folder_name"] == "2023-01-01 Quote"
    assert len(sent_submission_A["files"]) == 1

    received_submission_A = db.submissions.find_one({"type": "received", "supplier_name": "SupplierA"})
    assert received_submission_A is not None
    assert received_submission_A["folder_name"] == "2023-01-10 Revision"
    assert len(received_submission_A["files"]) == 1

    # Check Supplier B's submission
    sent_submission_B = db.submissions.find_one({"type": "sent", "supplier_name": "SupplierB"})
    assert sent_submission_B is not None
    assert sent_submission_B["folder_name"] == "2023-02-01 Request"
    assert len(sent_submission_B["files"]) == 1
    assert sent_submission_B["project_number"] == "67890"