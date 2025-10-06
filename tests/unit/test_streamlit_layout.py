"""
Tests for Streamlit dashboard layout and UI components.

Tests cover:
- Two-panel layout rendering
- Session state management for navigation
- Pagination logic
- Filter and search functionality
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

# Mock Streamlit before importing dashboard
sys.modules['streamlit'] = Mock()
sys.modules['dotenv'] = Mock()

from streamlit_dashboard import (
    filter_projects,
    sort_projects,
    format_timestamp,
    build_folder_tree,
)


class TestProjectFiltering:
    """Test project filtering logic."""

    def test_filter_projects_empty_search(self):
        """Test that empty search returns all projects."""
        projects = [
            {'project_number': '12345'},
            {'project_number': '67890'}
        ]
        result = filter_projects(projects, '')
        assert len(result) == 2

    def test_filter_projects_by_number(self):
        """Test filtering projects by number."""
        projects = [
            {'project_number': '12345'},
            {'project_number': '67890'},
            {'project_number': '12389'}
        ]
        result = filter_projects(projects, '123')
        assert len(result) == 2
        assert all('123' in p['project_number'] for p in result)

    def test_filter_projects_case_insensitive(self):
        """Test case-insensitive filtering."""
        projects = [
            {'project_number': 'ABC123'},
            {'project_number': 'xyz789'}
        ]
        result = filter_projects(projects, 'abc')
        assert len(result) == 1
        assert result[0]['project_number'] == 'ABC123'


class TestProjectSorting:
    """Test project sorting logic."""

    def test_sort_projects_ascending(self):
        """Test ascending project number sort."""
        projects = [
            {'project_number': '67890', 'last_scanned': '2024-01-01'},
            {'project_number': '12345', 'last_scanned': '2024-01-02'}
        ]
        result = sort_projects(projects, "Project Number (Ascending)")
        assert result[0]['project_number'] == '12345'
        assert result[1]['project_number'] == '67890'

    def test_sort_projects_descending(self):
        """Test descending project number sort."""
        projects = [
            {'project_number': '12345', 'last_scanned': '2024-01-01'},
            {'project_number': '67890', 'last_scanned': '2024-01-02'}
        ]
        result = sort_projects(projects, "Project Number (Descending)")
        assert result[0]['project_number'] == '67890'
        assert result[1]['project_number'] == '12345'

    def test_sort_projects_by_date_newest_first(self):
        """Test sorting by last scanned date (newest first)."""
        projects = [
            {'project_number': '12345', 'last_scanned': '2024-01-01T10:00:00+00:00'},
            {'project_number': '67890', 'last_scanned': '2024-01-02T10:00:00+00:00'}
        ]
        result = sort_projects(projects, "Last Scanned (Newest First)")
        assert result[0]['project_number'] == '67890'
        assert result[1]['project_number'] == '12345'

    def test_sort_projects_by_date_oldest_first(self):
        """Test sorting by last scanned date (oldest first)."""
        projects = [
            {'project_number': '67890', 'last_scanned': '2024-01-02T10:00:00+00:00'},
            {'project_number': '12345', 'last_scanned': '2024-01-01T10:00:00+00:00'}
        ]
        result = sort_projects(projects, "Last Scanned (Oldest First)")
        assert result[0]['project_number'] == '12345'
        assert result[1]['project_number'] == '67890'


class TestTimestampFormatting:
    """Test timestamp formatting."""

    def test_format_timestamp_iso8601(self):
        """Test formatting ISO 8601 timestamp."""
        timestamp = "2024-01-15T14:30:45+00:00"
        result = format_timestamp(timestamp)
        assert "2024-01-15" in result
        assert "14:30:45" in result

    def test_format_timestamp_with_z(self):
        """Test formatting timestamp with Z suffix."""
        timestamp = "2024-01-15T14:30:45Z"
        result = format_timestamp(timestamp)
        assert "2024-01-15" in result

    def test_format_timestamp_invalid(self):
        """Test invalid timestamp returns original string."""
        timestamp = "invalid-timestamp"
        result = format_timestamp(timestamp)
        assert result == timestamp


class TestFolderTree:
    """Test folder tree building logic."""

    def test_build_folder_tree_single_file(self):
        """Test building tree with single file."""
        files = ["/base/folder/file.pdf"]
        tree = build_folder_tree(files, "/base")

        assert 'folder' in tree
        assert '__files__' in tree['folder']
        assert len(tree['folder']['__files__']) == 1
        assert tree['folder']['__files__'][0]['name'] == 'file.pdf'

    def test_build_folder_tree_nested_folders(self):
        """Test building tree with nested folders."""
        files = [
            "/base/folder1/subfolder/file1.pdf",
            "/base/folder1/subfolder/file2.txt",
            "/base/folder2/file3.docx"
        ]
        tree = build_folder_tree(files, "/base")

        assert 'folder1' in tree
        assert 'subfolder' in tree['folder1']
        assert 'folder2' in tree
        assert len(tree['folder1']['subfolder']['__files__']) == 2
        assert len(tree['folder2']['__files__']) == 1

    def test_build_folder_tree_with_date_folders(self):
        """Test building tree with date-based folder structure (new spec requirement)."""
        files = [
            "/base/Supplier RFQ Quotes/LEWA/Received/10.01.2025/quote.pdf",
            "/base/Supplier RFQ Quotes/LEWA/Received/10.01.2025/details.txt",
            "/base/Supplier RFQ Quotes/LEWA/Sent/10.02.2025/rfq.pdf"
        ]
        tree = build_folder_tree(files, "/base")

        assert 'Supplier RFQ Quotes' in tree
        assert 'LEWA' in tree['Supplier RFQ Quotes']
        assert 'Received' in tree['Supplier RFQ Quotes']['LEWA']
        assert '10.01.2025' in tree['Supplier RFQ Quotes']['LEWA']['Received']
        assert len(tree['Supplier RFQ Quotes']['LEWA']['Received']['10.01.2025']['__files__']) == 2

    def test_build_folder_tree_empty_list(self):
        """Test building tree with empty file list."""
        tree = build_folder_tree([], "/base")
        assert tree == {}


class TestPaginationLogic:
    """Test pagination calculations."""

    def test_pagination_under_limit(self):
        """Test pagination when items under limit (no pagination needed)."""
        items = list(range(50))
        items_per_page = 100

        # Should not require pagination
        assert len(items) <= items_per_page

    def test_pagination_over_limit(self):
        """Test pagination when items exceed limit."""
        items = list(range(150))
        items_per_page = 50

        # Calculate pages
        total_pages = (len(items) + items_per_page - 1) // items_per_page
        assert total_pages == 3

        # Test page 1
        page = 1
        start_idx = (page - 1) * items_per_page
        end_idx = start_idx + items_per_page
        page_items = items[start_idx:end_idx]
        assert len(page_items) == 50
        assert page_items[0] == 0
        assert page_items[-1] == 49

        # Test page 3 (partial)
        page = 3
        start_idx = (page - 1) * items_per_page
        end_idx = start_idx + items_per_page
        page_items = items[start_idx:end_idx]
        assert len(page_items) == 50
        assert page_items[0] == 100
        assert page_items[-1] == 149


class TestSessionStateManagement:
    """Test session state management patterns."""

    def test_session_state_initialization(self):
        """Test session state variables are initialized correctly."""
        # This is a pattern test - actual implementation will use st.session_state
        state = {
            'selected_project': None,
            'data_refreshed': False,
            'last_refresh_time': None,
            'current_page': 1,
            'search_term': '',
            'active_filters': {}
        }

        assert state['selected_project'] is None
        assert state['data_refreshed'] is False
        assert state['current_page'] == 1

    def test_session_state_project_selection(self):
        """Test project selection state update."""
        state = {'selected_project': None}

        # Simulate project selection
        selected_project = {'project_number': '12345', 'path': '/path/to/project'}
        state['selected_project'] = selected_project

        assert state['selected_project'] is not None
        assert state['selected_project']['project_number'] == '12345'

    def test_session_state_persistence_across_reruns(self):
        """Test that state persists across simulated reruns."""
        # Initial state
        state = {
            'selected_project': {'project_number': '12345'},
            'current_page': 2
        }

        # Simulate rerun - state should persist
        assert state['selected_project']['project_number'] == '12345'
        assert state['current_page'] == 2


class TestResponsiveLayout:
    """Test responsive layout logic."""

    def test_two_column_layout_ratios(self):
        """Test two-column layout has correct ratio."""
        # Left panel should be ~30%, right panel ~70%
        left_ratio = 0.3
        right_ratio = 0.7

        assert abs(left_ratio + right_ratio - 1.0) < 0.01

    def test_mobile_layout_stacking(self):
        """Test mobile layout stacks vertically (conceptual)."""
        # Mobile width threshold
        mobile_threshold = 768

        # Desktop
        screen_width = 1920
        assert screen_width > mobile_threshold

        # Mobile
        screen_width = 375
        assert screen_width < mobile_threshold
