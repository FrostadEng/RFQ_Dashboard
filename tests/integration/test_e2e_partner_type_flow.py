"""
End-to-End integration tests for partner type feature.

Tests the complete flow from crawler detection through database storage to UI display.
"""

import pytest
import mongomock
from unittest.mock import patch
from pathlib import Path

from rfq_tracker.db_manager import DBManager
from rfq_tracker.crawler import RFQCrawler
from dashboard.data.queries import (
    fetch_suppliers_by_partner_type,
    get_project_statistics,
    get_partner_statistics
)

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


# ============================================================================
# Test 5.1: Full Crawler-to-UI Flow with Contractor RFQ Quotes
# ============================================================================

def test_e2e_contractor_rfq_quotes_flow(db_manager, tmp_path):
    """
    Test complete flow for Contractor RFQ Quotes:
    1. Crawler detects 'Contractor RFQ Quotes' folder
    2. Sets partner_type='Contractor' on suppliers and submissions
    3. Data stored in MongoDB correctly
    4. UI queries return only contractors
    5. Statistics calculated correctly
    """
    # Step 1: Create mock Contractor RFQ Quotes folder structure
    project_dir = tmp_path / "12345"
    contractor_rfq_dir = project_dir / "1-RFQ" / "Contractor RFQ Quotes"

    # ContractorA with sent and received
    contractor_a_sent = contractor_rfq_dir / "ContractorA" / "Sent" / "2024-01-15-Initial-RFQ"
    contractor_a_sent.mkdir(parents=True, exist_ok=True)
    (contractor_a_sent / "rfq_document.pdf").write_text("RFQ content")

    contractor_a_received = contractor_rfq_dir / "ContractorA" / "Received" / "2024-01-20-Response"
    contractor_a_received.mkdir(parents=True, exist_ok=True)
    (contractor_a_received / "quote.pdf").write_text("Quote content")

    # ContractorB with sent only
    contractor_b_sent = contractor_rfq_dir / "ContractorB" / "Sent" / "2024-01-16-Initial-RFQ"
    contractor_b_sent.mkdir(parents=True, exist_ok=True)
    (contractor_b_sent / "rfq_document.pdf").write_text("RFQ content")

    # Step 2: Run crawler
    config = {"root_path": str(tmp_path)}
    crawler = RFQCrawler(config, db_manager)
    project_data = crawler.process_project_folder(Path(project_dir))

    # Step 3: Verify crawler detected partner_type correctly
    assert project_data is not None
    assert len(project_data['suppliers']) == 2

    for supplier in project_data['suppliers']:
        assert supplier['partner_type'] == 'Contractor'
        assert supplier['supplier_name'] in ['ContractorA', 'ContractorB']

    for submission in project_data['submissions']:
        assert submission['partner_type'] == 'Contractor'
        assert submission['supplier_name'] in ['ContractorA', 'ContractorB']

    # Step 4: Save to database
    db_manager.save_project_data(project_data)

    # Step 5: Verify UI queries return contractors correctly
    contractors = fetch_suppliers_by_partner_type(db_manager, "12345", "Contractor")
    assert len(contractors) == 2
    contractor_names = {c['supplier_name'] for c in contractors}
    assert contractor_names == {'ContractorA', 'ContractorB'}

    # Step 6: Verify no suppliers returned when filtering by 'Supplier'
    suppliers = fetch_suppliers_by_partner_type(db_manager, "12345", "Supplier")
    assert len(suppliers) == 0

    # Step 7: Verify project statistics
    stats = get_project_statistics(db_manager, "12345", "Contractor")
    assert stats['contacted_count'] == 2  # Both contractors have sent submissions
    assert stats['response_count'] == 1   # Only ContractorA has received submissions

    # Step 8: Verify partner statistics
    partner_stats = get_partner_statistics(db_manager, "12345", "Contractor")
    assert len(partner_stats) == 2

    contractor_a_stats = next((p for p in partner_stats if p['supplier_name'] == 'ContractorA'), None)
    assert contractor_a_stats['sent_count'] == 1
    assert contractor_a_stats['received_count'] == 1

    contractor_b_stats = next((p for p in partner_stats if p['supplier_name'] == 'ContractorB'), None)
    assert contractor_b_stats['sent_count'] == 1
    assert contractor_b_stats['received_count'] == 0


# ============================================================================
# Test 5.2: Full Crawler-to-UI Flow with Supplier RFQ Quotes
# ============================================================================

def test_e2e_supplier_rfq_quotes_flow(db_manager, tmp_path):
    """
    Test complete flow for Supplier RFQ Quotes:
    1. Crawler detects 'Supplier RFQ Quotes' or default 'RFQ Quotes' folder
    2. Sets partner_type='Supplier' on suppliers and submissions
    3. Data stored in MongoDB correctly
    4. UI queries return only suppliers
    5. Statistics calculated correctly
    """
    # Step 1: Create mock Supplier RFQ Quotes folder structure
    project_dir = tmp_path / "67890"
    supplier_rfq_dir = project_dir / "1-RFQ" / "Supplier RFQ Quotes"

    # SupplierA with sent and received
    supplier_a_sent = supplier_rfq_dir / "SupplierA" / "Sent" / "2024-02-01-Initial-RFQ"
    supplier_a_sent.mkdir(parents=True, exist_ok=True)
    (supplier_a_sent / "rfq_document.pdf").write_text("RFQ content")

    supplier_a_received = supplier_rfq_dir / "SupplierA" / "Received" / "2024-02-05-Response"
    supplier_a_received.mkdir(parents=True, exist_ok=True)
    (supplier_a_received / "quote.pdf").write_text("Quote content")

    # SupplierB with sent only
    supplier_b_sent = supplier_rfq_dir / "SupplierB" / "Sent" / "2024-02-02-Initial-RFQ"
    supplier_b_sent.mkdir(parents=True, exist_ok=True)
    (supplier_b_sent / "rfq_document.pdf").write_text("RFQ content")

    # Step 2: Run crawler
    config = {"root_path": str(tmp_path)}
    crawler = RFQCrawler(config, db_manager)
    project_data = crawler.process_project_folder(Path(project_dir))

    # Step 3: Verify crawler detected partner_type correctly
    assert project_data is not None
    assert len(project_data['suppliers']) == 2

    for supplier in project_data['suppliers']:
        assert supplier['partner_type'] == 'Supplier'
        assert supplier['supplier_name'] in ['SupplierA', 'SupplierB']

    for submission in project_data['submissions']:
        assert submission['partner_type'] == 'Supplier'
        assert submission['supplier_name'] in ['SupplierA', 'SupplierB']

    # Step 4: Save to database
    db_manager.save_project_data(project_data)

    # Step 5: Verify UI queries return suppliers correctly
    suppliers = fetch_suppliers_by_partner_type(db_manager, "67890", "Supplier")
    assert len(suppliers) == 2
    supplier_names = {s['supplier_name'] for s in suppliers}
    assert supplier_names == {'SupplierA', 'SupplierB'}

    # Step 6: Verify no contractors returned when filtering by 'Contractor'
    contractors = fetch_suppliers_by_partner_type(db_manager, "67890", "Contractor")
    assert len(contractors) == 0

    # Step 7: Verify project statistics
    stats = get_project_statistics(db_manager, "67890", "Supplier")
    assert stats['contacted_count'] == 2  # Both suppliers have sent submissions
    assert stats['response_count'] == 1   # Only SupplierA has received submissions

    # Step 8: Verify partner statistics
    partner_stats = get_partner_statistics(db_manager, "67890", "Supplier")
    assert len(partner_stats) == 2

    supplier_a_stats = next((p for p in partner_stats if p['supplier_name'] == 'SupplierA'), None)
    assert supplier_a_stats['sent_count'] == 1
    assert supplier_a_stats['received_count'] == 1

    supplier_b_stats = next((p for p in partner_stats if p['supplier_name'] == 'SupplierB'), None)
    assert supplier_b_stats['sent_count'] == 1
    assert supplier_b_stats['received_count'] == 0


def test_e2e_default_rfq_quotes_flow(db_manager, tmp_path):
    """
    Test complete flow for default 'RFQ Quotes' folder (no 'Supplier' prefix):
    Should default to partner_type='Supplier'
    """
    # Step 1: Create mock default RFQ Quotes folder structure (no prefix)
    project_dir = tmp_path / "11111"
    default_rfq_dir = project_dir / "1-RFQ" / "RFQ Quotes"

    supplier_sent = default_rfq_dir / "DefaultSupplier" / "Sent" / "2024-03-01-Initial-RFQ"
    supplier_sent.mkdir(parents=True, exist_ok=True)
    (supplier_sent / "rfq_document.pdf").write_text("RFQ content")

    # Step 2: Run crawler
    config = {"root_path": str(tmp_path)}
    crawler = RFQCrawler(config, db_manager)
    project_data = crawler.process_project_folder(Path(project_dir))

    # Step 3: Verify defaults to 'Supplier'
    assert project_data is not None
    assert len(project_data['suppliers']) == 1
    assert project_data['suppliers'][0]['partner_type'] == 'Supplier'

    # Step 4: Save and verify
    db_manager.save_project_data(project_data)
    suppliers = fetch_suppliers_by_partner_type(db_manager, "11111", "Supplier")
    assert len(suppliers) == 1


# ============================================================================
# Test 5.3: Partner Type Toggle Switching
# ============================================================================

def test_partner_type_toggle_switching(db_manager, tmp_path):
    """
    Test that partner type toggle correctly switches between Suppliers and Contractors:
    1. Project has both suppliers and contractors
    2. Toggle to 'Suppliers' → see only suppliers
    3. Toggle to 'Contractors' → see only contractors
    4. Data remains isolated between views
    """
    # Setup: Create project with both suppliers and contractors
    project_dir = tmp_path / "99999"

    # Create Supplier RFQ Quotes
    supplier_dir = project_dir / "1-RFQ" / "Supplier RFQ Quotes" / "SupplierX" / "Sent" / "2024-04-01-RFQ"
    supplier_dir.mkdir(parents=True, exist_ok=True)
    (supplier_dir / "supplier_rfq.pdf").write_text("Supplier RFQ")

    # Create Contractor RFQ Quotes
    contractor_dir = project_dir / "1-RFQ" / "Contractor RFQ Quotes" / "ContractorX" / "Sent" / "2024-04-02-RFQ"
    contractor_dir.mkdir(parents=True, exist_ok=True)
    (contractor_dir / "contractor_rfq.pdf").write_text("Contractor RFQ")

    # Run crawler
    config = {"root_path": str(tmp_path)}
    crawler = RFQCrawler(config, db_manager)
    project_data = crawler.process_project_folder(Path(project_dir))
    db_manager.save_project_data(project_data)

    # Test toggle to Suppliers
    suppliers = fetch_suppliers_by_partner_type(db_manager, "99999", "Supplier")
    supplier_stats = get_project_statistics(db_manager, "99999", "Supplier")

    assert len(suppliers) == 1
    assert suppliers[0]['supplier_name'] == 'SupplierX'
    assert supplier_stats['contacted_count'] == 1

    # Test toggle to Contractors
    contractors = fetch_suppliers_by_partner_type(db_manager, "99999", "Contractor")
    contractor_stats = get_project_statistics(db_manager, "99999", "Contractor")

    assert len(contractors) == 1
    assert contractors[0]['supplier_name'] == 'ContractorX'
    assert contractor_stats['contacted_count'] == 1

    # Verify data isolation
    supplier_names = {s['supplier_name'] for s in suppliers}
    contractor_names = {c['supplier_name'] for c in contractors}
    assert supplier_names.isdisjoint(contractor_names)


# ============================================================================
# Test 5.4: Project-Level Statistics Update on Toggle
# ============================================================================

def test_project_statistics_update_on_toggle(db_manager):
    """
    Test that project-level statistics update correctly when toggle changes:
    1. Insert test data with different counts for suppliers vs contractors
    2. Verify stats for suppliers
    3. Verify stats for contractors
    4. Ensure counts are different and correct
    """
    # Setup: Project with 3 suppliers (2 with responses) and 2 contractors (1 with response)
    db_manager.db.projects.insert_one({"project_number": "55555", "path": "/test/55555"})

    # Suppliers
    db_manager.db.suppliers.insert_many([
        {"project_number": "55555", "supplier_name": "Sup1", "partner_type": "Supplier", "path": "/path/sup1"},
        {"project_number": "55555", "supplier_name": "Sup2", "partner_type": "Supplier", "path": "/path/sup2"},
        {"project_number": "55555", "supplier_name": "Sup3", "partner_type": "Supplier", "path": "/path/sup3"}
    ])

    # Contractors
    db_manager.db.suppliers.insert_many([
        {"project_number": "55555", "supplier_name": "Con1", "partner_type": "Contractor", "path": "/path/con1"},
        {"project_number": "55555", "supplier_name": "Con2", "partner_type": "Contractor", "path": "/path/con2"}
    ])

    # Supplier submissions: 3 sent, 2 received
    db_manager.db.submissions.insert_many([
        {"project_number": "55555", "supplier_name": "Sup1", "partner_type": "Supplier", "type": "sent", "folder_name": "F1", "folder_path": "/f1", "files": ["a.pdf"], "content_hash": "h1", "date": "2024-01-01"},
        {"project_number": "55555", "supplier_name": "Sup1", "partner_type": "Supplier", "type": "received", "folder_name": "F2", "folder_path": "/f2", "files": ["b.pdf"], "content_hash": "h2", "date": "2024-01-02"},
        {"project_number": "55555", "supplier_name": "Sup2", "partner_type": "Supplier", "type": "sent", "folder_name": "F3", "folder_path": "/f3", "files": ["c.pdf"], "content_hash": "h3", "date": "2024-01-03"},
        {"project_number": "55555", "supplier_name": "Sup2", "partner_type": "Supplier", "type": "received", "folder_name": "F4", "folder_path": "/f4", "files": ["d.pdf"], "content_hash": "h4", "date": "2024-01-04"},
        {"project_number": "55555", "supplier_name": "Sup3", "partner_type": "Supplier", "type": "sent", "folder_name": "F5", "folder_path": "/f5", "files": ["e.pdf"], "content_hash": "h5", "date": "2024-01-05"}
    ])

    # Contractor submissions: 2 sent, 1 received
    db_manager.db.submissions.insert_many([
        {"project_number": "55555", "supplier_name": "Con1", "partner_type": "Contractor", "type": "sent", "folder_name": "F6", "folder_path": "/f6", "files": ["f.pdf"], "content_hash": "h6", "date": "2024-01-06"},
        {"project_number": "55555", "supplier_name": "Con1", "partner_type": "Contractor", "type": "received", "folder_name": "F7", "folder_path": "/f7", "files": ["g.pdf"], "content_hash": "h7", "date": "2024-01-07"},
        {"project_number": "55555", "supplier_name": "Con2", "partner_type": "Contractor", "type": "sent", "folder_name": "F8", "folder_path": "/f8", "files": ["h.pdf"], "content_hash": "h8", "date": "2024-01-08"}
    ])

    # Test Supplier stats
    supplier_stats = get_project_statistics(db_manager, "55555", "Supplier")
    assert supplier_stats['contacted_count'] == 3  # Sup1, Sup2, Sup3
    assert supplier_stats['response_count'] == 2   # Sup1, Sup2

    # Test Contractor stats
    contractor_stats = get_project_statistics(db_manager, "55555", "Contractor")
    assert contractor_stats['contacted_count'] == 2  # Con1, Con2
    assert contractor_stats['response_count'] == 1   # Con1

    # Verify they're different
    assert supplier_stats != contractor_stats


# ============================================================================
# Test 5.5: Partner List Updates on Toggle
# ============================================================================

def test_partner_list_updates_on_toggle(db_manager):
    """
    Test that partner list updates correctly when toggle changes:
    1. Populate database with suppliers and contractors
    2. Fetch partner list for suppliers → verify correct list
    3. Fetch partner list for contractors → verify correct list
    4. Verify inline counts are correct for each
    """
    # Setup data (reuse from previous test)
    db_manager.db.projects.insert_one({"project_number": "66666", "path": "/test/66666"})

    db_manager.db.suppliers.insert_many([
        {"project_number": "66666", "supplier_name": "SupA", "partner_type": "Supplier", "path": "/path/supa"},
        {"project_number": "66666", "supplier_name": "SupB", "partner_type": "Supplier", "path": "/path/supb"},
        {"project_number": "66666", "supplier_name": "ConA", "partner_type": "Contractor", "path": "/path/cona"}
    ])

    db_manager.db.submissions.insert_many([
        # SupA: 2 sent, 1 received
        {"project_number": "66666", "supplier_name": "SupA", "partner_type": "Supplier", "type": "sent", "folder_name": "F1", "folder_path": "/f1", "files": ["a.pdf"], "content_hash": "h1", "date": "2024-01-01"},
        {"project_number": "66666", "supplier_name": "SupA", "partner_type": "Supplier", "type": "sent", "folder_name": "F2", "folder_path": "/f2", "files": ["b.pdf"], "content_hash": "h2", "date": "2024-01-02"},
        {"project_number": "66666", "supplier_name": "SupA", "partner_type": "Supplier", "type": "received", "folder_name": "F3", "folder_path": "/f3", "files": ["c.pdf"], "content_hash": "h3", "date": "2024-01-03"},
        # SupB: 1 sent, 0 received
        {"project_number": "66666", "supplier_name": "SupB", "partner_type": "Supplier", "type": "sent", "folder_name": "F4", "folder_path": "/f4", "files": ["d.pdf"], "content_hash": "h4", "date": "2024-01-04"},
        # ConA: 1 sent, 2 received
        {"project_number": "66666", "supplier_name": "ConA", "partner_type": "Contractor", "type": "sent", "folder_name": "F5", "folder_path": "/f5", "files": ["e.pdf"], "content_hash": "h5", "date": "2024-01-05"},
        {"project_number": "66666", "supplier_name": "ConA", "partner_type": "Contractor", "type": "received", "folder_name": "F6", "folder_path": "/f6", "files": ["f.pdf"], "content_hash": "h6", "date": "2024-01-06"},
        {"project_number": "66666", "supplier_name": "ConA", "partner_type": "Contractor", "type": "received", "folder_name": "F7", "folder_path": "/f7", "files": ["g.pdf"], "content_hash": "h7", "date": "2024-01-07"}
    ])

    # Test Supplier partner list
    supplier_list = fetch_suppliers_by_partner_type(db_manager, "66666", "Supplier")
    supplier_stats_list = get_partner_statistics(db_manager, "66666", "Supplier")

    assert len(supplier_list) == 2
    assert len(supplier_stats_list) == 2

    sup_a_stats = next((p for p in supplier_stats_list if p['supplier_name'] == 'SupA'), None)
    assert sup_a_stats['sent_count'] == 2
    assert sup_a_stats['received_count'] == 1

    sup_b_stats = next((p for p in supplier_stats_list if p['supplier_name'] == 'SupB'), None)
    assert sup_b_stats['sent_count'] == 1
    assert sup_b_stats['received_count'] == 0

    # Test Contractor partner list
    contractor_list = fetch_suppliers_by_partner_type(db_manager, "66666", "Contractor")
    contractor_stats_list = get_partner_statistics(db_manager, "66666", "Contractor")

    assert len(contractor_list) == 1
    assert len(contractor_stats_list) == 1

    con_a_stats = contractor_stats_list[0]
    assert con_a_stats['supplier_name'] == 'ConA'
    assert con_a_stats['sent_count'] == 1
    assert con_a_stats['received_count'] == 2


# ============================================================================
# Test 5.8: Comprehensive Integration Test
# ============================================================================

def test_comprehensive_integration_validation(db_manager, tmp_path):
    """
    Comprehensive end-to-end test validating entire partner type feature:
    1. Create project with mixed suppliers and contractors
    2. Crawler detects and classifies correctly
    3. Database stores with correct partner_type
    4. All UI queries work correctly
    5. Statistics are accurate
    6. Toggle behavior works properly
    """
    # Create comprehensive test project
    project_dir = tmp_path / "88888"

    # Suppliers (2 suppliers, both with responses)
    for supplier_name in ['Alpha', 'Beta']:
        supplier_sent = project_dir / "1-RFQ" / "Supplier RFQ Quotes" / supplier_name / "Sent" / "2024-05-01-RFQ"
        supplier_sent.mkdir(parents=True, exist_ok=True)
        (supplier_sent / f"{supplier_name}_rfq.pdf").write_text(f"{supplier_name} RFQ")

        supplier_received = project_dir / "1-RFQ" / "Supplier RFQ Quotes" / supplier_name / "Received" / "2024-05-05-Response"
        supplier_received.mkdir(parents=True, exist_ok=True)
        (supplier_received / f"{supplier_name}_quote.pdf").write_text(f"{supplier_name} Quote")

    # Contractors (3 contractors, 2 with responses)
    for contractor_name in ['Gamma', 'Delta', 'Epsilon']:
        contractor_sent = project_dir / "1-RFQ" / "Contractor RFQ Quotes" / contractor_name / "Sent" / "2024-05-02-RFQ"
        contractor_sent.mkdir(parents=True, exist_ok=True)
        (contractor_sent / f"{contractor_name}_rfq.pdf").write_text(f"{contractor_name} RFQ")

        # Only Gamma and Delta have responses
        if contractor_name in ['Gamma', 'Delta']:
            contractor_received = project_dir / "1-RFQ" / "Contractor RFQ Quotes" / contractor_name / "Received" / "2024-05-06-Response"
            contractor_received.mkdir(parents=True, exist_ok=True)
            (contractor_received / f"{contractor_name}_quote.pdf").write_text(f"{contractor_name} Quote")

    # Run crawler
    config = {"root_path": str(tmp_path)}
    crawler = RFQCrawler(config, db_manager)
    project_data = crawler.process_project_folder(Path(project_dir))
    db_manager.save_project_data(project_data)

    # Validate crawler classification
    assert len(project_data['suppliers']) == 5  # 2 suppliers + 3 contractors
    supplier_count = sum(1 for s in project_data['suppliers'] if s['partner_type'] == 'Supplier')
    contractor_count = sum(1 for s in project_data['suppliers'] if s['partner_type'] == 'Contractor')
    assert supplier_count == 2
    assert contractor_count == 3

    # Validate database storage
    total_suppliers_in_db = db_manager.db.suppliers.count_documents({"project_number": "88888"})
    assert total_suppliers_in_db == 5

    # Validate UI queries - Suppliers view
    suppliers = fetch_suppliers_by_partner_type(db_manager, "88888", "Supplier")
    assert len(suppliers) == 2
    supplier_names = {s['supplier_name'] for s in suppliers}
    assert supplier_names == {'Alpha', 'Beta'}

    supplier_stats = get_project_statistics(db_manager, "88888", "Supplier")
    assert supplier_stats['contacted_count'] == 2
    assert supplier_stats['response_count'] == 2

    # Validate UI queries - Contractors view
    contractors = fetch_suppliers_by_partner_type(db_manager, "88888", "Contractor")
    assert len(contractors) == 3
    contractor_names = {c['supplier_name'] for c in contractors}
    assert contractor_names == {'Gamma', 'Delta', 'Epsilon'}

    contractor_stats = get_project_statistics(db_manager, "88888", "Contractor")
    assert contractor_stats['contacted_count'] == 3
    assert contractor_stats['response_count'] == 2  # Gamma and Delta

    # Validate partner-level statistics
    supplier_partner_stats = get_partner_statistics(db_manager, "88888", "Supplier")
    assert all(p['sent_count'] == 1 and p['received_count'] == 1 for p in supplier_partner_stats)

    contractor_partner_stats = get_partner_statistics(db_manager, "88888", "Contractor")
    assert len(contractor_partner_stats) == 3

    gamma_stats = next(p for p in contractor_partner_stats if p['supplier_name'] == 'Gamma')
    assert gamma_stats['sent_count'] == 1 and gamma_stats['received_count'] == 1

    delta_stats = next(p for p in contractor_partner_stats if p['supplier_name'] == 'Delta')
    assert delta_stats['sent_count'] == 1 and delta_stats['received_count'] == 1

    epsilon_stats = next(p for p in contractor_partner_stats if p['supplier_name'] == 'Epsilon')
    assert epsilon_stats['sent_count'] == 1 and epsilon_stats['received_count'] == 0

    # Validate data isolation
    assert supplier_names.isdisjoint(contractor_names)
