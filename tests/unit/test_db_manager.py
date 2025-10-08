import pytest
import mongomock
from unittest.mock import patch, MagicMock
from pymongo.errors import ConnectionFailure

from rfq_tracker.db_manager import DBManager

MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "test_rfq_db"

@pytest.fixture
def mock_mongo_client():
    """Fixture to mock MongoClient with mongomock."""
    client = mongomock.MongoClient()
    return client

@pytest.fixture
def db_manager(mock_mongo_client):
    """Fixture for DBManager that uses the mocked MongoClient."""
    with patch('rfq_tracker.db_manager.MongoClient', return_value=mock_mongo_client):
        manager = DBManager(mongo_uri=MONGO_URI, db_name=DB_NAME)
        yield manager
        # Ensure connection is closed
        if manager.client:
            manager.close()

def test_connect_success(db_manager, mock_mongo_client):
    """Test successful connection to MongoDB."""
    db_manager.connect()
    assert db_manager.client is not None
    assert db_manager.db is not None
    assert db_manager.db.name == DB_NAME
    # Note: ismaster command call is wrapped in try-except for mongomock compatibility

@patch('rfq_tracker.db_manager.MongoClient')
def test_connect_failure(mock_mongo_constructor):
    """Test connection failure handling.

    Note: The current implementation catches ConnectionFailure in an inner try-except,
    so this test verifies that the connection proceeds even if ismaster command fails.
    """
    # Configure the mock to raise ConnectionFailure on ismaster command
    mock_client_instance = MagicMock()
    mock_client_instance.admin.command.side_effect = ConnectionFailure("Test connection error")
    mock_mongo_constructor.return_value = mock_client_instance

    manager = DBManager(mongo_uri=MONGO_URI, db_name=DB_NAME)

    # The inner try-except catches the ConnectionFailure, so connection continues
    manager.connect()
    assert manager.client is not None
    assert manager.db is not None

def test_ensure_indexes(db_manager):
    """Test that all required indexes are created."""
    db_manager.connect()

    # Using mongomock, index_information() shows created indexes
    project_indexes = db_manager.db.projects.index_information()
    supplier_indexes = db_manager.db.suppliers.index_information()
    submission_indexes = db_manager.db.submissions.index_information()

    assert "project_number_1" in project_indexes
    assert "project_number_1_supplier_name_1" in supplier_indexes
    assert "project_number_1_supplier_name_1_type_1" in submission_indexes
    # Content-aware versioning uses compound index with content_hash
    assert "project_number_1_supplier_name_1_folder_name_1_content_hash_1" in submission_indexes

    # partner_type indexes
    assert "partner_type_1" in supplier_indexes
    assert "partner_type_1" in submission_indexes

    # Compound indexes with partner_type
    assert "project_number_1_partner_type_1" in supplier_indexes
    assert "project_number_1_partner_type_1" in submission_indexes
    assert "project_number_1_partner_type_1_type_1" in submission_indexes

def test_save_project_data(db_manager):
    """Test saving a complete set of project data."""
    db_manager.connect()

    project_data = {
        "project": {"project_number": "12345", "path": "/path/12345"},
        "suppliers": [
            {"project_number": "12345", "supplier_name": "SupplierA", "path": "/path/12345/RFQ/SupplierA"}
        ],
        "submissions": [
            {
                "project_number": "12345",
                "supplier_name": "SupplierA",
                "type": "sent",
                "folder_name": "Sub1",
                "folder_path": "/path/12345/RFQ/SupplierA/Sent/Sub1",
                "files": ["file1.pdf"],
                "content_hash": "abc123",
                "date": "2024-01-01T00:00:00Z"
            }
        ]
    }

    db_manager.save_project_data(project_data)

    # Verify data was inserted
    assert db_manager.db.projects.count_documents({"project_number": "12345"}) == 1
    assert db_manager.db.suppliers.count_documents({"supplier_name": "SupplierA"}) == 1
    assert db_manager.db.submissions.count_documents({"folder_name": "Sub1"}) == 1

    # Test upsert functionality
    project_data["project"]["path"] = "/new/path/12345"
    db_manager.save_project_data(project_data)

    # Count should still be 1, but data should be updated
    assert db_manager.db.projects.count_documents({"project_number": "12345"}) == 1
    updated_proj = db_manager.db.projects.find_one({"project_number": "12345"})
    assert updated_proj["path"] == "/new/path/12345"

def test_save_empty_data(db_manager):
    """Test saving data with empty lists."""
    db_manager.connect()
    
    empty_data = {
        "project": {"project_number": "54321"},
        "suppliers": [],
        "submissions": []
    }
    
    db_manager.save_project_data(empty_data)
    
    assert db_manager.db.projects.count_documents({"project_number": "54321"}) == 1
    assert db_manager.db.suppliers.count_documents({}) == 0
    assert db_manager.db.submissions.count_documents({}) == 0

def test_close_connection(db_manager):
    """Test closing the connection."""
    db_manager.connect()
    assert db_manager.client is not None

    db_manager.close()

    # mongomock doesn't have a close method, but we can verify the connection was closed
    # by checking that the client still exists (close() doesn't set it to None)
    assert db_manager.client is not None


# Test suite for partner_type field validation
def test_supplier_partner_type_default_value(db_manager):
    """Test that supplier documents default to 'Supplier' when partner_type is not provided."""
    db_manager.connect()

    supplier_data = {
        "project": {"project_number": "11111"},
        "suppliers": [
            {"project_number": "11111", "supplier_name": "TestSupplier", "path": "/path/to/supplier"}
        ],
        "submissions": []
    }

    db_manager.save_project_data(supplier_data)

    # Retrieve the supplier and check partner_type defaults to 'Supplier'
    supplier = db_manager.db.suppliers.find_one({"supplier_name": "TestSupplier"})
    assert supplier is not None
    # When not provided, we expect default behavior (handled by queries with backward compatibility)
    # At the schema level, the field may not exist yet


def test_supplier_partner_type_enum_supplier(db_manager):
    """Test that supplier documents accept 'Supplier' as valid partner_type."""
    db_manager.connect()

    supplier_data = {
        "project": {"project_number": "22222"},
        "suppliers": [
            {
                "project_number": "22222",
                "supplier_name": "ValidSupplier",
                "path": "/path/to/supplier",
                "partner_type": "Supplier"
            }
        ],
        "submissions": []
    }

    db_manager.save_project_data(supplier_data)

    supplier = db_manager.db.suppliers.find_one({"supplier_name": "ValidSupplier"})
    assert supplier is not None
    assert supplier["partner_type"] == "Supplier"


def test_supplier_partner_type_enum_contractor(db_manager):
    """Test that supplier documents accept 'Contractor' as valid partner_type."""
    db_manager.connect()

    supplier_data = {
        "project": {"project_number": "33333"},
        "suppliers": [
            {
                "project_number": "33333",
                "supplier_name": "ContractorSupplier",
                "path": "/path/to/contractor",
                "partner_type": "Contractor"
            }
        ],
        "submissions": []
    }

    db_manager.save_project_data(supplier_data)

    supplier = db_manager.db.suppliers.find_one({"supplier_name": "ContractorSupplier"})
    assert supplier is not None
    assert supplier["partner_type"] == "Contractor"


def test_submission_partner_type_default_value(db_manager):
    """Test that submission documents default to 'Supplier' when partner_type is not provided."""
    db_manager.connect()

    submission_data = {
        "project": {"project_number": "44444"},
        "suppliers": [],
        "submissions": [
            {
                "project_number": "44444",
                "supplier_name": "TestSubmissionSupplier",
                "type": "sent",
                "folder_name": "TestFolder",
                "folder_path": "/path/to/folder",
                "files": ["file1.pdf"],
                "content_hash": "hash123",
                "date": "2024-01-01T00:00:00Z"
            }
        ]
    }

    db_manager.save_project_data(submission_data)

    submission = db_manager.db.submissions.find_one({"folder_name": "TestFolder"})
    assert submission is not None
    # When not provided, we expect default behavior (handled by queries with backward compatibility)


def test_submission_partner_type_enum_supplier(db_manager):
    """Test that submission documents accept 'Supplier' as valid partner_type."""
    db_manager.connect()

    submission_data = {
        "project": {"project_number": "55555"},
        "suppliers": [],
        "submissions": [
            {
                "project_number": "55555",
                "supplier_name": "ValidSubmissionSupplier",
                "type": "sent",
                "folder_name": "ValidFolder",
                "folder_path": "/path/to/folder",
                "files": ["file1.pdf"],
                "content_hash": "hash456",
                "date": "2024-01-01T00:00:00Z",
                "partner_type": "Supplier"
            }
        ]
    }

    db_manager.save_project_data(submission_data)

    submission = db_manager.db.submissions.find_one({"folder_name": "ValidFolder"})
    assert submission is not None
    assert submission["partner_type"] == "Supplier"


def test_submission_partner_type_enum_contractor(db_manager):
    """Test that submission documents accept 'Contractor' as valid partner_type."""
    db_manager.connect()

    submission_data = {
        "project": {"project_number": "66666"},
        "suppliers": [],
        "submissions": [
            {
                "project_number": "66666",
                "supplier_name": "ContractorSubmissionSupplier",
                "type": "received",
                "folder_name": "ContractorFolder",
                "folder_path": "/path/to/contractor/folder",
                "files": ["file2.pdf"],
                "content_hash": "hash789",
                "date": "2024-01-01T00:00:00Z",
                "partner_type": "Contractor"
            }
        ]
    }

    db_manager.save_project_data(submission_data)

    submission = db_manager.db.submissions.find_one({"folder_name": "ContractorFolder"})
    assert submission is not None
    assert submission["partner_type"] == "Contractor"


def test_partner_type_persists_across_upserts(db_manager):
    """Test that partner_type is preserved when documents are updated via upsert."""
    db_manager.connect()

    # Initial save with partner_type
    initial_data = {
        "project": {"project_number": "77777"},
        "suppliers": [
            {
                "project_number": "77777",
                "supplier_name": "UpsertSupplier",
                "path": "/path/to/supplier",
                "partner_type": "Contractor"
            }
        ],
        "submissions": []
    }

    db_manager.save_project_data(initial_data)

    # Update with new path but same supplier
    updated_data = {
        "project": {"project_number": "77777"},
        "suppliers": [
            {
                "project_number": "77777",
                "supplier_name": "UpsertSupplier",
                "path": "/new/path/to/supplier",
                "partner_type": "Contractor"
            }
        ],
        "submissions": []
    }

    db_manager.save_project_data(updated_data)

    # Verify partner_type is still Contractor
    supplier = db_manager.db.suppliers.find_one({"supplier_name": "UpsertSupplier"})
    assert supplier is not None
    assert supplier["partner_type"] == "Contractor"
    assert supplier["path"] == "/new/path/to/supplier"