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
    """Test connection failure."""
    # Configure the mock to raise ConnectionFailure
    mock_client_instance = MagicMock()
    mock_client_instance.admin.command.side_effect = ConnectionFailure("Test connection error")
    mock_mongo_constructor.return_value = mock_client_instance

    manager = DBManager(mongo_uri=MONGO_URI, db_name=DB_NAME)
    
    with pytest.raises(SystemExit) as e:
        manager.connect()
    assert e.type == SystemExit
    assert e.value.code == 1

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
                "files": ["file1.pdf"]
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

def test_close_connection(db_manager, mock_mongo_client):
    """Test closing the connection."""
    db_manager.connect()
    assert db_manager.client is not None
    
    db_manager.close()
    
    # Check that the mock client's close method was called
    mock_mongo_client.close.assert_called_once()