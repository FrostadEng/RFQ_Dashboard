"""
Unit tests for dashboard query functions with partner_type filtering.
"""

import pytest
import mongomock
from unittest.mock import patch, MagicMock
from dashboard.data.queries import (
    fetch_all_suppliers,
    fetch_projects,
    fetch_supplier_data,
    fetch_suppliers_by_partner_type,
    fetch_submissions_by_partner_type,
    get_project_statistics,
    get_partner_statistics
)
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
        manager.connect()
        yield manager
        manager.close()


@pytest.fixture
def populated_db(db_manager):
    """Fixture that populates the database with test data including partner_type."""
    # Insert test projects
    db_manager.db.projects.insert_many([
        {"project_number": "12345", "path": "/path/12345"},
        {"project_number": "67890", "path": "/path/67890"}
    ])

    # Insert suppliers with different partner_types
    db_manager.db.suppliers.insert_many([
        {
            "project_number": "12345",
            "supplier_name": "SupplierA",
            "partner_type": "Supplier",
            "path": "/path/12345/RFQ/SupplierA"
        },
        {
            "project_number": "12345",
            "supplier_name": "SupplierB",
            "partner_type": "Supplier",
            "path": "/path/12345/RFQ/SupplierB"
        },
        {
            "project_number": "12345",
            "supplier_name": "ContractorA",
            "partner_type": "Contractor",
            "path": "/path/12345/Contractor RFQ/ContractorA"
        },
        {
            "project_number": "12345",
            "supplier_name": "ContractorB",
            "partner_type": "Contractor",
            "path": "/path/12345/Contractor RFQ/ContractorB"
        },
        {
            "project_number": "67890",
            "supplier_name": "SupplierC",
            "partner_type": "Supplier",
            "path": "/path/67890/RFQ/SupplierC"
        },
        # Legacy supplier without partner_type (for backward compatibility testing)
        {
            "project_number": "67890",
            "supplier_name": "LegacySupplier",
            "path": "/path/67890/RFQ/LegacySupplier"
        }
    ])

    # Insert submissions with different partner_types and directions
    db_manager.db.submissions.insert_many([
        # SupplierA submissions (project 12345)
        {
            "project_number": "12345",
            "supplier_name": "SupplierA",
            "partner_type": "Supplier",
            "type": "sent",
            "folder_name": "Initial-RFQ",
            "folder_path": "/path/12345/RFQ/SupplierA/Sent/Initial-RFQ",
            "files": ["rfq.pdf"],
            "content_hash": "hash1",
            "date": "2024-01-01T00:00:00Z"
        },
        {
            "project_number": "12345",
            "supplier_name": "SupplierA",
            "partner_type": "Supplier",
            "type": "received",
            "folder_name": "Response-1",
            "folder_path": "/path/12345/RFQ/SupplierA/Received/Response-1",
            "files": ["quote.pdf"],
            "content_hash": "hash2",
            "date": "2024-01-05T00:00:00Z"
        },
        # SupplierB submissions (project 12345) - sent only
        {
            "project_number": "12345",
            "supplier_name": "SupplierB",
            "partner_type": "Supplier",
            "type": "sent",
            "folder_name": "Initial-RFQ",
            "folder_path": "/path/12345/RFQ/SupplierB/Sent/Initial-RFQ",
            "files": ["rfq.pdf"],
            "content_hash": "hash3",
            "date": "2024-01-02T00:00:00Z"
        },
        # ContractorA submissions (project 12345)
        {
            "project_number": "12345",
            "supplier_name": "ContractorA",
            "partner_type": "Contractor",
            "type": "sent",
            "folder_name": "Initial-RFQ",
            "folder_path": "/path/12345/Contractor RFQ/ContractorA/Sent/Initial-RFQ",
            "files": ["rfq.pdf"],
            "content_hash": "hash4",
            "date": "2024-01-03T00:00:00Z"
        },
        {
            "project_number": "12345",
            "supplier_name": "ContractorA",
            "partner_type": "Contractor",
            "type": "received",
            "folder_name": "Response-1",
            "folder_path": "/path/12345/Contractor RFQ/ContractorA/Received/Response-1",
            "files": ["quote.pdf"],
            "content_hash": "hash5",
            "date": "2024-01-07T00:00:00Z"
        },
        # ContractorB submissions (project 12345) - sent only
        {
            "project_number": "12345",
            "supplier_name": "ContractorB",
            "partner_type": "Contractor",
            "type": "sent",
            "folder_name": "Initial-RFQ",
            "folder_path": "/path/12345/Contractor RFQ/ContractorB/Sent/Initial-RFQ",
            "files": ["rfq.pdf"],
            "content_hash": "hash6",
            "date": "2024-01-04T00:00:00Z"
        },
        # SupplierC submissions (project 67890)
        {
            "project_number": "67890",
            "supplier_name": "SupplierC",
            "partner_type": "Supplier",
            "type": "sent",
            "folder_name": "Initial-RFQ",
            "folder_path": "/path/67890/RFQ/SupplierC/Sent/Initial-RFQ",
            "files": ["rfq.pdf"],
            "content_hash": "hash7",
            "date": "2024-02-01T00:00:00Z"
        },
        # Legacy submission without partner_type
        {
            "project_number": "67890",
            "supplier_name": "LegacySupplier",
            "type": "sent",
            "folder_name": "Old-RFQ",
            "folder_path": "/path/67890/RFQ/LegacySupplier/Sent/Old-RFQ",
            "files": ["old_rfq.pdf"],
            "content_hash": "hash8",
            "date": "2023-12-01T00:00:00Z"
        }
    ])

    return db_manager


# ============================================================================
# Tests for Task 3.1: Filtering suppliers by partner_type
# ============================================================================

def test_fetch_suppliers_by_partner_type_supplier_only(populated_db):
    """Test filtering suppliers to return only 'Supplier' partner_type."""
    suppliers = fetch_suppliers_by_partner_type(populated_db, "12345", "Supplier")

    assert len(suppliers) == 2
    supplier_names = [s["supplier_name"] for s in suppliers]
    assert "SupplierA" in supplier_names
    assert "SupplierB" in supplier_names
    assert "ContractorA" not in supplier_names
    assert "ContractorB" not in supplier_names

    # Verify all returned suppliers have partner_type='Supplier'
    for supplier in suppliers:
        assert supplier["partner_type"] == "Supplier"


def test_fetch_suppliers_by_partner_type_contractor_only(populated_db):
    """Test filtering suppliers to return only 'Contractor' partner_type."""
    suppliers = fetch_suppliers_by_partner_type(populated_db, "12345", "Contractor")

    assert len(suppliers) == 2
    supplier_names = [s["supplier_name"] for s in suppliers]
    assert "ContractorA" in supplier_names
    assert "ContractorB" in supplier_names
    assert "SupplierA" not in supplier_names
    assert "SupplierB" not in supplier_names

    # Verify all returned suppliers have partner_type='Contractor'
    for supplier in suppliers:
        assert supplier["partner_type"] == "Contractor"


def test_fetch_suppliers_by_partner_type_no_results(populated_db):
    """Test filtering suppliers when no matching partner_type exists."""
    # Project 67890 has no contractors
    suppliers = fetch_suppliers_by_partner_type(populated_db, "67890", "Contractor")
    assert len(suppliers) == 0


def test_fetch_suppliers_by_partner_type_nonexistent_project(populated_db):
    """Test filtering suppliers for a nonexistent project."""
    suppliers = fetch_suppliers_by_partner_type(populated_db, "99999", "Supplier")
    assert len(suppliers) == 0


def test_fetch_suppliers_by_partner_type_with_backward_compatibility(populated_db):
    """Test that legacy suppliers without partner_type are treated as 'Supplier'."""
    # This test verifies backward compatibility (Task 3.9)
    # LegacySupplier has no partner_type field, should be treated as 'Supplier'
    suppliers = fetch_suppliers_by_partner_type(populated_db, "67890", "Supplier")

    supplier_names = [s["supplier_name"] for s in suppliers]
    assert "SupplierC" in supplier_names
    assert "LegacySupplier" in supplier_names
    assert len(suppliers) == 2


# ============================================================================
# Tests for Task 3.2: Filtering submissions by partner_type
# ============================================================================

def test_fetch_submissions_by_partner_type_supplier_only(populated_db):
    """Test filtering submissions to return only 'Supplier' partner_type."""
    submissions = fetch_submissions_by_partner_type(populated_db, "12345", "Supplier")

    # Should have 3 submissions: 2 from SupplierA, 1 from SupplierB
    assert len(submissions) == 3

    # Verify all returned submissions have partner_type='Supplier'
    for submission in submissions:
        assert submission["partner_type"] == "Supplier"

    # Verify supplier names
    supplier_names = {s["supplier_name"] for s in submissions}
    assert supplier_names == {"SupplierA", "SupplierB"}


def test_fetch_submissions_by_partner_type_contractor_only(populated_db):
    """Test filtering submissions to return only 'Contractor' partner_type."""
    submissions = fetch_submissions_by_partner_type(populated_db, "12345", "Contractor")

    # Should have 3 submissions: 2 from ContractorA, 1 from ContractorB
    assert len(submissions) == 3

    # Verify all returned submissions have partner_type='Contractor'
    for submission in submissions:
        assert submission["partner_type"] == "Contractor"

    # Verify supplier names
    supplier_names = {s["supplier_name"] for s in submissions}
    assert supplier_names == {"ContractorA", "ContractorB"}


def test_fetch_submissions_by_partner_type_and_direction(populated_db):
    """Test filtering submissions by both partner_type and direction (sent/received)."""
    # Test Supplier sent submissions
    sent_suppliers = fetch_submissions_by_partner_type(
        populated_db, "12345", "Supplier", submission_type="sent"
    )
    assert len(sent_suppliers) == 2  # SupplierA and SupplierB sent

    # Test Supplier received submissions
    received_suppliers = fetch_submissions_by_partner_type(
        populated_db, "12345", "Supplier", submission_type="received"
    )
    assert len(received_suppliers) == 1  # Only SupplierA received

    # Test Contractor sent submissions
    sent_contractors = fetch_submissions_by_partner_type(
        populated_db, "12345", "Contractor", submission_type="sent"
    )
    assert len(sent_contractors) == 2  # ContractorA and ContractorB sent

    # Test Contractor received submissions
    received_contractors = fetch_submissions_by_partner_type(
        populated_db, "12345", "Contractor", submission_type="received"
    )
    assert len(received_contractors) == 1  # Only ContractorA received


def test_fetch_submissions_by_partner_type_with_backward_compatibility(populated_db):
    """Test that legacy submissions without partner_type are treated as 'Supplier'."""
    # Project 67890 has one legacy submission without partner_type
    submissions = fetch_submissions_by_partner_type(populated_db, "67890", "Supplier")

    assert len(submissions) == 2  # SupplierC + LegacySupplier
    supplier_names = {s["supplier_name"] for s in submissions}
    assert "SupplierC" in supplier_names
    assert "LegacySupplier" in supplier_names


# ============================================================================
# Tests for Task 3.3: Aggregation query for unique partners contacted (sent)
# ============================================================================

def test_get_project_statistics_contacted_count_suppliers(populated_db):
    """Test aggregation query computing unique Suppliers contacted (sent count)."""
    stats = get_project_statistics(populated_db, "12345", "Supplier")

    # 2 suppliers (SupplierA, SupplierB) have sent submissions
    assert stats["contacted_count"] == 2


def test_get_project_statistics_contacted_count_contractors(populated_db):
    """Test aggregation query computing unique Contractors contacted (sent count)."""
    stats = get_project_statistics(populated_db, "12345", "Contractor")

    # 2 contractors (ContractorA, ContractorB) have sent submissions
    assert stats["contacted_count"] == 2


def test_get_project_statistics_contacted_count_zero(populated_db):
    """Test aggregation query when no partners were contacted."""
    # Project 67890 has no contractors
    stats = get_project_statistics(populated_db, "67890", "Contractor")

    assert stats["contacted_count"] == 0


def test_get_project_statistics_contacted_count_with_backward_compatibility(populated_db):
    """Test that contacted count includes legacy submissions without partner_type."""
    # Project 67890 has SupplierC + LegacySupplier
    stats = get_project_statistics(populated_db, "67890", "Supplier")

    assert stats["contacted_count"] == 2  # Both should be counted


# ============================================================================
# Tests for Task 3.4: Aggregation query for unique partners with responses (received)
# ============================================================================

def test_get_project_statistics_response_count_suppliers(populated_db):
    """Test aggregation query computing unique Suppliers with responses (received count)."""
    stats = get_project_statistics(populated_db, "12345", "Supplier")

    # Only 1 supplier (SupplierA) has received submissions
    assert stats["response_count"] == 1


def test_get_project_statistics_response_count_contractors(populated_db):
    """Test aggregation query computing unique Contractors with responses (received count)."""
    stats = get_project_statistics(populated_db, "12345", "Contractor")

    # Only 1 contractor (ContractorA) has received submissions
    assert stats["response_count"] == 1


def test_get_project_statistics_response_count_zero(populated_db):
    """Test aggregation query when no responses were received."""
    # Project 67890 has suppliers but no received submissions
    stats = get_project_statistics(populated_db, "67890", "Supplier")

    assert stats["response_count"] == 0


def test_get_project_statistics_combined(populated_db):
    """Test that project statistics returns both contacted and response counts correctly."""
    # Test for Suppliers
    supplier_stats = get_project_statistics(populated_db, "12345", "Supplier")
    assert supplier_stats["contacted_count"] == 2
    assert supplier_stats["response_count"] == 1

    # Test for Contractors
    contractor_stats = get_project_statistics(populated_db, "12345", "Contractor")
    assert contractor_stats["contacted_count"] == 2
    assert contractor_stats["response_count"] == 1


# ============================================================================
# Tests for Task 3.5: Partner statistics aggregation (sent/received per partner)
# ============================================================================

def test_get_partner_statistics_suppliers(populated_db):
    """Test aggregation pipeline for partner-level statistics (Suppliers)."""
    partner_stats = get_partner_statistics(populated_db, "12345", "Supplier")

    assert len(partner_stats) == 2

    # Find SupplierA stats
    supplier_a = next((p for p in partner_stats if p["supplier_name"] == "SupplierA"), None)
    assert supplier_a is not None
    assert supplier_a["sent_count"] == 1
    assert supplier_a["received_count"] == 1

    # Find SupplierB stats
    supplier_b = next((p for p in partner_stats if p["supplier_name"] == "SupplierB"), None)
    assert supplier_b is not None
    assert supplier_b["sent_count"] == 1
    assert supplier_b["received_count"] == 0


def test_get_partner_statistics_contractors(populated_db):
    """Test aggregation pipeline for partner-level statistics (Contractors)."""
    partner_stats = get_partner_statistics(populated_db, "12345", "Contractor")

    assert len(partner_stats) == 2

    # Find ContractorA stats
    contractor_a = next((p for p in partner_stats if p["supplier_name"] == "ContractorA"), None)
    assert contractor_a is not None
    assert contractor_a["sent_count"] == 1
    assert contractor_a["received_count"] == 1

    # Find ContractorB stats
    contractor_b = next((p for p in partner_stats if p["supplier_name"] == "ContractorB"), None)
    assert contractor_b is not None
    assert contractor_b["sent_count"] == 1
    assert contractor_b["received_count"] == 0


def test_get_partner_statistics_sorted_alphabetically(populated_db):
    """Test that partner statistics are returned in alphabetical order by supplier_name."""
    partner_stats = get_partner_statistics(populated_db, "12345", "Supplier")

    names = [p["supplier_name"] for p in partner_stats]
    assert names == sorted(names)


def test_get_partner_statistics_with_backward_compatibility(populated_db):
    """Test that partner statistics include legacy suppliers without partner_type."""
    partner_stats = get_partner_statistics(populated_db, "67890", "Supplier")

    assert len(partner_stats) == 2

    supplier_names = {p["supplier_name"] for p in partner_stats}
    assert "SupplierC" in supplier_names
    assert "LegacySupplier" in supplier_names


def test_get_partner_statistics_empty_project(populated_db):
    """Test partner statistics for a project with no partners of the specified type."""
    partner_stats = get_partner_statistics(populated_db, "67890", "Contractor")

    assert len(partner_stats) == 0
