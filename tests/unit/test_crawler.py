import pytest
from unittest.mock import Mock
from pathlib import Path
from datetime import datetime, timezone

from rfq_tracker.crawler import RFQCrawler
from rfq_tracker.db_manager import DBManager

# Mock configuration
MOCK_CONFIG = {
    "root_path": "/mock_root",
    "filter_tags": ["Template", "archive"],
    "file_filter_tags": [".db", ".tmp"],
    "rfq_folder_names": ["RFQ", "Supplier RFQ", "Contractor"]
}

@pytest.fixture
def mock_db_manager():
    """Fixture for a mocked DBManager."""
    return Mock(spec=DBManager)

@pytest.fixture
def crawler(mock_db_manager, fs):
    """Fixture for RFQCrawler with a fake file system."""
    # Set up a fake file system
    fs.create_dir(MOCK_CONFIG["root_path"])
    return RFQCrawler(config=MOCK_CONFIG, db_manager=mock_db_manager)

def test_is_project_folder(crawler):
    assert crawler.is_project_folder("12345")
    assert not crawler.is_project_folder("ProjectA")
    assert not crawler.is_project_folder("12345A")

def test_should_skip_folder(crawler):
    assert crawler.should_skip_folder("MyProject_Template")
    assert crawler.should_skip_folder("archive_folder")
    assert not crawler.should_skip_folder("Active_Project")

def test_should_skip_file(crawler):
    assert crawler.should_skip_file("database.db")
    assert crawler.should_skip_file("temp_file.tmp")
    assert not crawler.should_skip_file("document.pdf")

def test_find_rfq_folders(crawler, fs):
    project_path = Path(f"{MOCK_CONFIG['root_path']}/12345")
    fs.create_dir(project_path)
    fs.create_dir(project_path / "RFQ")
    fs.create_dir(project_path / "Drawings")
    fs.create_dir(project_path / "Supplier RFQ")

    rfq_folders = crawler.find_rfq_folders(project_path)
    assert len(rfq_folders) == 2
    assert project_path / "RFQ" in rfq_folders
    assert project_path / "Supplier RFQ" in rfq_folders

def test_get_file_creation_time(crawler, fs):
    file_path = Path(f"{MOCK_CONFIG['root_path']}/test.txt")
    fs.create_file(file_path)
    
    # pyfakefs doesn't perfectly simulate ctime, but we can test the format
    creation_time_str = crawler.get_file_creation_time(file_path)
    
    # Verify it's a valid ISO 8601 timestamp
    parsed_time = datetime.fromisoformat(creation_time_str)
    assert parsed_time.tzinfo is not None

def test_process_submission_folder(crawler, fs):
    submission_path = Path(f"{MOCK_CONFIG['root_path']}/12345/RFQ/SupplierA/Sent/2023-01-01_Submission")
    fs.create_file(submission_path / "file1.pdf")
    fs.create_file(submission_path / "file2.docx")
    fs.create_file(submission_path / "ignore.tmp") # Should be skipped

    submissions = crawler.process_submission_folder(
        submission_path.parent, "12345", "SupplierA", "sent"
    )
    
    assert len(submissions) == 1
    sub = submissions[0]
    assert sub["project_number"] == "12345"
    assert sub["supplier_name"] == "SupplierA"
    assert sub["type"] == "sent"
    assert sub["folder_name"] == "2023-01-01_Submission"
    assert len(sub["files"]) == 2
    assert str(submission_path / "file1.pdf") in sub["files"]


def test_process_supplier_folder(crawler, fs):
    supplier_path = Path(f"{MOCK_CONFIG['root_path']}/12345/RFQ/SupplierA")
    fs.create_file(supplier_path / "Sent/2023-01-01/quote.pdf")
    fs.create_file(supplier_path / "Received/2023-01-05/response.pdf")

    result = crawler.process_supplier_folder(supplier_path, "12345")

    assert result["supplier"]["supplier_name"] == "SupplierA"
    assert len(result["submissions"]) == 2
    
    types = {s["type"] for s in result["submissions"]}
    assert types == {"sent", "received"}

def test_process_project_folder(crawler, fs):
    project_path = Path(f"{MOCK_CONFIG['root_path']}/67890")
    fs.create_file(project_path / "RFQ/SupplierB/Sent/2023-02-01/request.zip")
    fs.create_dir(project_path / "archive_drawings") # Should be skipped

    data = crawler.process_project_folder(project_path)

    assert data["project"]["project_number"] == "67890"
    assert len(data["suppliers"]) == 1
    assert data["suppliers"][0]["supplier_name"] == "SupplierB"
    assert len(data["submissions"]) == 1
    assert data["submissions"][0]["type"] == "sent"

def test_crawl_flow(crawler, mock_db_manager, fs):
    # Setup a more complex file structure
    fs.create_file(f"{MOCK_CONFIG['root_path']}/11111/RFQ/SupplierC/Sent/2023-03-01/doc1.pdf")
    fs.create_file(f"{MOCK_CONFIG['root_path']}/22222/Contractor/SupplierD/Received/2023-03-02/doc2.pdf")
    fs.create_dir(f"{MOCK_CONFIG['root_path']}/Project_Template") # Skipped
    fs.create_dir(f"{MOCK_CONFIG['root_path']}/33333") # Project with no RFQ folder

    crawler.crawl()

    # Verify that connect and close were called
    mock_db_manager.connect.assert_called_once()
    mock_db_manager.close.assert_called_once()

    # Verify save_project_data was called for all three projects (including empty project 33333)
    assert mock_db_manager.save_project_data.call_count == 3

    # Inspect the calls to save_project_data
    call_args = [call.args[0] for call in mock_db_manager.save_project_data.call_args_list]

    project_numbers = {arg["project"]["project_number"] for arg in call_args}
    assert project_numbers == {"11111", "22222", "33333"}

    # Check data for project 11111
    data_11111 = next(p for p in call_args if p["project"]["project_number"] == "11111")
    assert len(data_11111["suppliers"]) == 1
    assert data_11111["suppliers"][0]["supplier_name"] == "SupplierC"
    assert len(data_11111["submissions"]) == 1

def test_crawl_dry_run(crawler, mock_db_manager, fs):
    fs.create_file(f"{MOCK_CONFIG['root_path']}/12345/RFQ/SupplierA/Sent/2023-01-01/quote.pdf")
    
    crawler.dry_run = True
    crawler.crawl()

    # In a dry run, no database methods should be called
    mock_db_manager.connect.assert_not_called()
    mock_db_manager.save_project_data.assert_not_called()
    mock_db_manager.close.assert_not_called()