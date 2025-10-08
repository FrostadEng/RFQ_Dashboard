"""
Tests for RFQ Crawler folder structure parsing.

Tests both legacy folder structure and new folder structure:
- Legacy: Projects/{project}/RFQ/{supplier}/{Received|Sent}/{date}/
- New: Projects/{project}/1-RFQ/Supplier RFQ Quotes/{supplier}/{Received|Sent}/{date}/
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from rfq_tracker.crawler import RFQCrawler


class TestFolderStructureParsing:
    """Test folder structure detection and parsing."""

    @pytest.fixture
    def mock_db_manager(self):
        """Create a mock database manager."""
        db_manager = Mock()
        db_manager.connect = Mock()
        db_manager.close = Mock()
        db_manager.save_project_data = Mock()
        return db_manager

    @pytest.fixture
    def temp_project_root(self):
        """Create a temporary directory for test projects."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)

    def create_legacy_structure(self, root: Path, project_num: str, supplier: str):
        """Create legacy folder structure for testing."""
        project_path = root / project_num / "RFQ" / supplier
        (project_path / "Received" / "2024-01-15").mkdir(parents=True)
        (project_path / "Sent" / "2024-01-20").mkdir(parents=True)

        # Create some test files
        (project_path / "Received" / "2024-01-15" / "response.pdf").touch()
        (project_path / "Sent" / "2024-01-20" / "request.pdf").touch()

        return project_path

    def create_new_structure(self, root: Path, project_num: str, supplier: str):
        """Create new folder structure for testing."""
        project_path = root / project_num / "1-RFQ" / "Supplier RFQ Quotes" / supplier
        (project_path / "Received" / "10.01.2025").mkdir(parents=True)
        (project_path / "Sent" / "10.02.2025").mkdir(parents=True)

        # Create some test files
        (project_path / "Received" / "10.01.2025" / "quote.pdf").touch()
        (project_path / "Sent" / "10.02.2025" / "rfq.pdf").touch()

        return project_path

    def test_detect_legacy_rfq_folder(self, temp_project_root, mock_db_manager):
        """Test detection of legacy RFQ folder."""
        self.create_legacy_structure(temp_project_root, "12345", "SupplierA")

        config = {"root_path": str(temp_project_root)}
        crawler = RFQCrawler(config, mock_db_manager, dry_run=True)

        project_path = temp_project_root / "12345"
        rfq_folders = crawler.find_rfq_folders(project_path)

        assert len(rfq_folders) == 1
        assert rfq_folders[0].name == "RFQ"

    def test_detect_new_rfq_folder(self, temp_project_root, mock_db_manager):
        """Test detection of new 1-RFQ folder."""
        self.create_new_structure(temp_project_root, "24038", "LEWA")

        config = {"root_path": str(temp_project_root)}
        crawler = RFQCrawler(config, mock_db_manager, dry_run=True)

        project_path = temp_project_root / "24038"
        rfq_folders = crawler.find_rfq_folders(project_path)

        assert len(rfq_folders) == 1
        assert rfq_folders[0].name == "1-RFQ"

    def test_process_legacy_structure(self, temp_project_root, mock_db_manager):
        """Test processing of legacy folder structure."""
        self.create_legacy_structure(temp_project_root, "12345", "SupplierA")

        config = {"root_path": str(temp_project_root)}
        crawler = RFQCrawler(config, mock_db_manager, dry_run=True)

        project_folder = temp_project_root / "12345"
        project_data = crawler.process_project_folder(project_folder)

        assert project_data["project"]["project_number"] == "12345"
        assert len(project_data["suppliers"]) == 1
        assert project_data["suppliers"][0]["supplier_name"] == "SupplierA"

        # Should have submissions from both Received and Sent
        assert len(project_data["submissions"]) >= 1

    def test_process_new_structure(self, temp_project_root, mock_db_manager):
        """Test processing of new folder structure with 1-RFQ and Supplier RFQ Quotes."""
        self.create_new_structure(temp_project_root, "24038", "LEWA")

        config = {"root_path": str(temp_project_root)}
        crawler = RFQCrawler(config, mock_db_manager, dry_run=True)

        project_folder = temp_project_root / "24038"
        project_data = crawler.process_project_folder(project_folder)

        assert project_data["project"]["project_number"] == "24038"
        assert len(project_data["suppliers"]) == 1
        assert project_data["suppliers"][0]["supplier_name"] == "LEWA"

        # Should have submissions from both Received and Sent
        assert len(project_data["submissions"]) >= 1

    def test_backward_compatibility_both_structures(self, temp_project_root, mock_db_manager):
        """Test that crawler can handle both old and new structures simultaneously."""
        # Create one project with legacy structure
        self.create_legacy_structure(temp_project_root, "12345", "SupplierA")

        # Create another project with new structure
        self.create_new_structure(temp_project_root, "24038", "LEWA")

        config = {"root_path": str(temp_project_root)}
        crawler = RFQCrawler(config, mock_db_manager, dry_run=False)

        crawler.crawl()

        # Should have called save_project_data twice (once for each project)
        assert mock_db_manager.save_project_data.call_count == 2

    def test_supplier_quotes_intermediate_layer(self, temp_project_root, mock_db_manager):
        """Test navigation through 'Supplier RFQ Quotes' intermediate layer."""
        self.create_new_structure(temp_project_root, "24038", "LEWA")

        config = {"root_path": str(temp_project_root)}
        crawler = RFQCrawler(config, mock_db_manager, dry_run=True)

        # Navigate through the structure
        project_path = temp_project_root / "24038"
        rfq_folder = project_path / "1-RFQ"
        supplier_quotes_folder = rfq_folder / "Supplier RFQ Quotes"

        # Verify the intermediate layer exists
        assert supplier_quotes_folder.exists()
        assert supplier_quotes_folder.is_dir()

        # Process the project
        project_data = crawler.process_project_folder(project_path)

        # Verify supplier was found despite intermediate layer
        assert len(project_data["suppliers"]) == 1
        assert project_data["suppliers"][0]["supplier_name"] == "LEWA"

    def test_file_extraction_new_structure(self, temp_project_root, mock_db_manager):
        """Test file extraction from new folder structure."""
        project_path = self.create_new_structure(temp_project_root, "24038", "LEWA")

        # Add more test files
        (project_path / "Received" / "10.01.2025" / "file1.pdf").touch()
        (project_path / "Received" / "10.01.2025" / "file2.txt").touch()

        config = {"root_path": str(temp_project_root)}
        crawler = RFQCrawler(config, mock_db_manager, dry_run=True)

        project_data = crawler.process_project_folder(temp_project_root / "24038")

        # Find the received submission
        received_submissions = [s for s in project_data["submissions"] if s["type"] == "received"]
        assert len(received_submissions) >= 1

        # Check files were extracted
        submission = received_submissions[0]
        assert len(submission["files"]) >= 2

    def test_case_insensitive_received_recieved(self, temp_project_root, mock_db_manager):
        """Test handling of 'Received' vs 'Recieved' spelling variations."""
        # Create structure with misspelled 'Recieved'
        project_path = temp_project_root / "24038" / "1-RFQ" / "Supplier RFQ Quotes" / "LEWA"
        (project_path / "Recieved" / "10.01.2025").mkdir(parents=True)
        (project_path / "Sent" / "10.02.2025").mkdir(parents=True)

        (project_path / "Recieved" / "10.01.2025" / "file.pdf").touch()

        config = {"root_path": str(temp_project_root)}
        crawler = RFQCrawler(config, mock_db_manager, dry_run=True)

        # Process and verify it handles the misspelling
        project_data = crawler.process_project_folder(temp_project_root / "24038")

        # Should still find submissions (implementation will handle case variations)
        assert len(project_data["submissions"]) >= 1


class TestPartnerTypeDetection:
    """Test partner_type field detection and assignment based on folder structure."""

    @pytest.fixture
    def mock_db_manager(self):
        """Create a mock database manager."""
        db_manager = Mock()
        db_manager.connect = Mock()
        db_manager.close = Mock()
        db_manager.save_project_data = Mock()
        return db_manager

    @pytest.fixture
    def temp_project_root(self):
        """Create a temporary directory for test projects."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)

    def create_contractor_structure(self, root: Path, project_num: str, contractor: str):
        """Create Contractor RFQ Quotes folder structure for testing."""
        project_path = root / project_num / "1-RFQ" / "Contractor RFQ Quotes" / contractor
        (project_path / "Received" / "2024-03-01-Initial-Response").mkdir(parents=True)
        (project_path / "Sent" / "2024-02-15-RFQ-Package").mkdir(parents=True)

        # Create test files
        (project_path / "Received" / "2024-03-01-Initial-Response" / "bid.pdf").touch()
        (project_path / "Sent" / "2024-02-15-RFQ-Package" / "scope.pdf").touch()

        return project_path

    def create_supplier_structure(self, root: Path, project_num: str, supplier: str):
        """Create Supplier RFQ Quotes folder structure for testing."""
        project_path = root / project_num / "1-RFQ" / "Supplier RFQ Quotes" / supplier
        (project_path / "Received" / "2024-03-10-Quote").mkdir(parents=True)
        (project_path / "Sent" / "2024-03-05-Request").mkdir(parents=True)

        # Create test files
        (project_path / "Received" / "2024-03-10-Quote" / "quote.pdf").touch()
        (project_path / "Sent" / "2024-03-05-Request" / "request.pdf").touch()

        return project_path

    def create_legacy_structure(self, root: Path, project_num: str, supplier: str):
        """Create legacy folder structure (default supplier type)."""
        project_path = root / project_num / "RFQ" / supplier
        (project_path / "Received" / "2024-01-15").mkdir(parents=True)
        (project_path / "Sent" / "2024-01-20").mkdir(parents=True)

        # Create test files
        (project_path / "Received" / "2024-01-15" / "response.pdf").touch()
        (project_path / "Sent" / "2024-01-20" / "request.pdf").touch()

        return project_path

    def test_detect_contractor_rfq_quotes_path(self, temp_project_root, mock_db_manager):
        """Test detection of 'Contractor RFQ Quotes' folder pattern in path."""
        self.create_contractor_structure(temp_project_root, "12345", "ContractorA")

        config = {"root_path": str(temp_project_root)}
        crawler = RFQCrawler(config, mock_db_manager, dry_run=True)

        project_path = temp_project_root / "12345"
        rfq_folder = project_path / "1-RFQ"
        contractor_quotes_folder = rfq_folder / "Contractor RFQ Quotes"

        # Verify folder exists
        assert contractor_quotes_folder.exists()
        assert contractor_quotes_folder.is_dir()

        # Verify RFQ folder is detected
        rfq_folders = crawler.find_rfq_folders(project_path)
        assert len(rfq_folders) == 1
        assert rfq_folders[0].name == "1-RFQ"

    def test_detect_supplier_rfq_quotes_path(self, temp_project_root, mock_db_manager):
        """Test detection of 'Supplier RFQ Quotes' folder pattern in path."""
        self.create_supplier_structure(temp_project_root, "24038", "SupplierB")

        config = {"root_path": str(temp_project_root)}
        crawler = RFQCrawler(config, mock_db_manager, dry_run=True)

        project_path = temp_project_root / "24038"
        rfq_folder = project_path / "1-RFQ"
        supplier_quotes_folder = rfq_folder / "Supplier RFQ Quotes"

        # Verify folder exists
        assert supplier_quotes_folder.exists()
        assert supplier_quotes_folder.is_dir()

        # Verify RFQ folder is detected
        rfq_folders = crawler.find_rfq_folders(project_path)
        assert len(rfq_folders) == 1

    def test_partner_type_contractor_assigned_to_supplier_doc(self, temp_project_root, mock_db_manager):
        """Test that partner_type='Contractor' is assigned to supplier document from Contractor path."""
        self.create_contractor_structure(temp_project_root, "12345", "ContractorA")

        config = {"root_path": str(temp_project_root)}
        crawler = RFQCrawler(config, mock_db_manager, dry_run=True)

        project_data = crawler.process_project_folder(temp_project_root / "12345")

        # Verify supplier document has partner_type='Contractor'
        assert len(project_data["suppliers"]) == 1
        supplier_doc = project_data["suppliers"][0]
        assert supplier_doc["supplier_name"] == "ContractorA"
        assert supplier_doc.get("partner_type") == "Contractor"

    def test_partner_type_supplier_assigned_to_supplier_doc(self, temp_project_root, mock_db_manager):
        """Test that partner_type='Supplier' is assigned to supplier document from Supplier path."""
        self.create_supplier_structure(temp_project_root, "24038", "SupplierB")

        config = {"root_path": str(temp_project_root)}
        crawler = RFQCrawler(config, mock_db_manager, dry_run=True)

        project_data = crawler.process_project_folder(temp_project_root / "24038")

        # Verify supplier document has partner_type='Supplier'
        assert len(project_data["suppliers"]) == 1
        supplier_doc = project_data["suppliers"][0]
        assert supplier_doc["supplier_name"] == "SupplierB"
        assert supplier_doc.get("partner_type") == "Supplier"

    def test_partner_type_default_supplier_for_legacy_structure(self, temp_project_root, mock_db_manager):
        """Test that partner_type defaults to 'Supplier' for legacy folder structure."""
        self.create_legacy_structure(temp_project_root, "99999", "LegacySupplier")

        config = {"root_path": str(temp_project_root)}
        crawler = RFQCrawler(config, mock_db_manager, dry_run=True)

        project_data = crawler.process_project_folder(temp_project_root / "99999")

        # Verify supplier document defaults to partner_type='Supplier'
        assert len(project_data["suppliers"]) == 1
        supplier_doc = project_data["suppliers"][0]
        assert supplier_doc["supplier_name"] == "LegacySupplier"
        assert supplier_doc.get("partner_type") == "Supplier"

    def test_partner_type_contractor_assigned_to_submission_docs(self, temp_project_root, mock_db_manager):
        """Test that partner_type='Contractor' is assigned to all submission documents."""
        self.create_contractor_structure(temp_project_root, "12345", "ContractorA")

        config = {"root_path": str(temp_project_root)}
        crawler = RFQCrawler(config, mock_db_manager, dry_run=True)

        project_data = crawler.process_project_folder(temp_project_root / "12345")

        # Verify all submissions have partner_type='Contractor'
        assert len(project_data["submissions"]) >= 2  # At least sent and received
        for submission in project_data["submissions"]:
            assert submission["supplier_name"] == "ContractorA"
            assert submission.get("partner_type") == "Contractor"

    def test_partner_type_supplier_assigned_to_submission_docs(self, temp_project_root, mock_db_manager):
        """Test that partner_type='Supplier' is assigned to all submission documents."""
        self.create_supplier_structure(temp_project_root, "24038", "SupplierB")

        config = {"root_path": str(temp_project_root)}
        crawler = RFQCrawler(config, mock_db_manager, dry_run=True)

        project_data = crawler.process_project_folder(temp_project_root / "24038")

        # Verify all submissions have partner_type='Supplier'
        assert len(project_data["submissions"]) >= 2  # At least sent and received
        for submission in project_data["submissions"]:
            assert submission["supplier_name"] == "SupplierB"
            assert submission.get("partner_type") == "Supplier"

    def test_partner_type_mixed_project_both_types(self, temp_project_root, mock_db_manager):
        """Test project with both Contractor and Supplier RFQ Quotes folders."""
        # Create both contractor and supplier structures in same project
        contractor_path = temp_project_root / "50000" / "1-RFQ" / "Contractor RFQ Quotes" / "ContractorX"
        (contractor_path / "Received" / "2024-04-01").mkdir(parents=True)
        (contractor_path / "Received" / "2024-04-01" / "bid.pdf").touch()

        supplier_path = temp_project_root / "50000" / "1-RFQ" / "Supplier RFQ Quotes" / "SupplierY"
        (supplier_path / "Received" / "2024-04-02").mkdir(parents=True)
        (supplier_path / "Received" / "2024-04-02" / "quote.pdf").touch()

        config = {"root_path": str(temp_project_root)}
        crawler = RFQCrawler(config, mock_db_manager, dry_run=True)

        project_data = crawler.process_project_folder(temp_project_root / "50000")

        # Verify we have both suppliers with correct partner_types
        assert len(project_data["suppliers"]) == 2

        contractor_docs = [s for s in project_data["suppliers"] if s["supplier_name"] == "ContractorX"]
        supplier_docs = [s for s in project_data["suppliers"] if s["supplier_name"] == "SupplierY"]

        assert len(contractor_docs) == 1
        assert contractor_docs[0].get("partner_type") == "Contractor"

        assert len(supplier_docs) == 1
        assert supplier_docs[0].get("partner_type") == "Supplier"

        # Verify submissions have matching partner_types
        contractor_submissions = [s for s in project_data["submissions"] if s["supplier_name"] == "ContractorX"]
        supplier_submissions = [s for s in project_data["submissions"] if s["supplier_name"] == "SupplierY"]

        for sub in contractor_submissions:
            assert sub.get("partner_type") == "Contractor"

        for sub in supplier_submissions:
            assert sub.get("partner_type") == "Supplier"

    def test_partner_type_propagated_to_both_sent_and_received(self, temp_project_root, mock_db_manager):
        """Test that partner_type is propagated to both sent and received submissions."""
        self.create_contractor_structure(temp_project_root, "12345", "ContractorA")

        config = {"root_path": str(temp_project_root)}
        crawler = RFQCrawler(config, mock_db_manager, dry_run=True)

        project_data = crawler.process_project_folder(temp_project_root / "12345")

        sent_submissions = [s for s in project_data["submissions"] if s["type"] == "sent"]
        received_submissions = [s for s in project_data["submissions"] if s["type"] == "received"]

        # Both sent and received should exist and have partner_type='Contractor'
        assert len(sent_submissions) >= 1
        assert len(received_submissions) >= 1

        for sub in sent_submissions:
            assert sub.get("partner_type") == "Contractor"

        for sub in received_submissions:
            assert sub.get("partner_type") == "Contractor"
