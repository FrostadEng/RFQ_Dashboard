"""
Streamlit-based RFQ Dashboard
Web interface for viewing and searching RFQ project data
"""

import os
import json
import logging
import platform
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from urllib.parse import quote
import streamlit as st
from dotenv import load_dotenv

from rfq_tracker.db_manager import DBManager
from dashboard.styles import get_custom_css, get_statistics_badge, format_file_size

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="RFQ Dashboard",
    page_icon="📊",
    layout="wide"
)

# Inject custom CSS
st.markdown(get_custom_css(), unsafe_allow_html=True)


def load_config() -> Dict[str, Any]:
    """Load configuration from config.json or environment variables."""
    config = {}

    # Try to load from config.json
    config_path = "config.json"
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config = json.load(f)

    # Override with environment variables if present
    config['mongo_uri'] = os.getenv('MONGO_URI', config.get('mongo_uri', 'mongodb://localhost:27017'))
    config['mongo_db'] = os.getenv('MONGO_DB', config.get('mongo_db', 'rfq_tracker'))

    return config


@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_all_suppliers(_db_manager: DBManager) -> List[str]:
    """
    Fetch all unique supplier names from the database.

    Args:
        _db_manager: DBManager instance

    Returns:
        Sorted list of unique supplier names
    """
    try:
        suppliers = _db_manager.db.suppliers.distinct("supplier_name")
        return sorted(suppliers)
    except Exception as e:
        logger.error(f"Error fetching suppliers: {e}")
        return []


@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_projects(_db_manager: DBManager) -> List[Dict[str, Any]]:
    """
    Fetch all projects from MongoDB with caching.

    Args:
        _db_manager: DBManager instance (underscore prefix prevents Streamlit from hashing)

    Returns:
        List of project dictionaries
    """
    try:
        projects = list(_db_manager.db.projects.find().sort("project_number", -1))
        logger.info(f"Loaded {len(projects)} projects from database")
        return projects
    except Exception as e:
        logger.error(f"Error fetching projects: {e}")
        st.error(f"Error fetching projects: {e}")
        return []


@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_supplier_data(_db_manager: DBManager, project_number: str) -> List[Dict[str, Any]]:
    """
    Fetch all supplier data (suppliers, transmissions, receipts) for a project with caching.

    Args:
        _db_manager: DBManager instance (underscore prefix prevents Streamlit from hashing)
        project_number: Project number to fetch suppliers for

    Returns:
        List of dictionaries containing supplier data with transmissions and receipts
    """
    try:
        # Fetch all suppliers for the project, sorted alphabetically
        suppliers = list(_db_manager.db.suppliers.find(
            {"project_number": project_number}
        ).sort("supplier_name", 1))

        supplier_data = []

        for supplier in suppliers:
            supplier_name = supplier['supplier_name']

            # Fetch all submissions for this supplier, sorted by date descending (newest first)
            submissions = list(_db_manager.db.submissions.find({
                "project_number": project_number,
                "supplier_name": supplier_name
            }).sort("date", -1))

            # Separate into sent and received
            transmissions = [s for s in submissions if s.get('type') == 'sent']
            receipts = [s for s in submissions if s.get('type') == 'received']

            supplier_data.append({
                'supplier': supplier,
                'transmissions': transmissions,
                'receipts': receipts
            })

        logger.info(f"Loaded {len(supplier_data)} suppliers for project {project_number}")
        return supplier_data

    except Exception as e:
        logger.error(f"Error fetching supplier data for project {project_number}: {e}")
        st.error(f"Error loading supplier data: {e}")
        return []


def initialize_db_manager() -> Optional[DBManager]:
    """Initialize database connection with error handling."""
    config = load_config()

    try:
        db_manager = DBManager(config['mongo_uri'], config['mongo_db'])
        db_manager.connect()
        return db_manager
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        st.error("❌ Failed to connect to MongoDB. Please check the database is running.")
        st.info("**Troubleshooting:**\n- Verify MongoDB is running\n- Check config.json for correct connection settings\n- Ensure network connectivity")

        if st.button("🔄 Retry Connection"):
            st.rerun()

        return None


def filter_projects(
    projects: List[Dict[str, Any]],
    search_term: str,
    selected_suppliers: List[str] = None,
    date_range_start: datetime = None,
    date_range_end: datetime = None,
    db_manager: DBManager = None
) -> List[Dict[str, Any]]:
    """
    Filter projects by search term, suppliers, and date range.

    Args:
        projects: List of project dictionaries
        search_term: Search string for project number
        selected_suppliers: List of supplier names to filter by
        date_range_start: Start date for filtering (last_scanned)
        date_range_end: End date for filtering (last_scanned)
        db_manager: Database manager for supplier lookups

    Returns:
        Filtered list of projects
    """
    filtered = projects

    # Filter by search term
    if search_term:
        search_lower = search_term.lower()
        filtered = [p for p in filtered if search_lower in p['project_number'].lower()]

    # Filter by suppliers (if project has at least one selected supplier)
    if selected_suppliers and db_manager:
        projects_with_suppliers = set()
        for supplier_name in selected_suppliers:
            # Find all projects that have this supplier
            supplier_docs = db_manager.db.suppliers.find(
                {"supplier_name": supplier_name},
                {"project_number": 1}
            )
            projects_with_suppliers.update(doc['project_number'] for doc in supplier_docs)

        filtered = [p for p in filtered if p['project_number'] in projects_with_suppliers]

    # Filter by date range (last_scanned)
    if date_range_start or date_range_end:
        date_filtered = []
        for p in filtered:
            if 'last_scanned' not in p or not p['last_scanned']:
                continue

            try:
                project_date = datetime.fromisoformat(p['last_scanned'].replace('Z', '+00:00'))

                if date_range_start and project_date < date_range_start:
                    continue
                if date_range_end and project_date > date_range_end:
                    continue

                date_filtered.append(p)
            except:
                continue

        filtered = date_filtered

    return filtered


def sort_projects(projects: List[Dict[str, Any]], sort_option: str) -> List[Dict[str, Any]]:
    """Sort projects based on selected option."""
    if sort_option == "Project Number (Ascending)":
        return sorted(projects, key=lambda p: p['project_number'])
    elif sort_option == "Project Number (Descending)":
        return sorted(projects, key=lambda p: p['project_number'], reverse=True)
    elif sort_option == "Last Scanned (Newest First)":
        return sorted(projects, key=lambda p: p.get('last_scanned', ''), reverse=True)
    elif sort_option == "Last Scanned (Oldest First)":
        return sorted(projects, key=lambda p: p.get('last_scanned', ''))

    return projects


def format_timestamp(timestamp_str: str) -> str:
    """Format ISO 8601 timestamp to human-readable format."""
    try:
        dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except:
        return timestamp_str


def calculate_folder_statistics(files: List[str]) -> Dict[str, Any]:
    """
    Calculate statistics for a list of files.

    Args:
        files: List of file paths

    Returns:
        Dictionary with file_count and total_size
    """
    total_size = 0
    existing_files = 0

    for file_path in files:
        try:
            path = Path(file_path)
            if path.exists():
                total_size += path.stat().st_size
                existing_files += 1
        except:
            continue

    return {
        'file_count': len(files),
        'existing_count': existing_files,
        'total_size': total_size
    }


def calculate_supplier_statistics(transmissions: List[Dict], receipts: List[Dict]) -> Dict[str, Any]:
    """
    Calculate aggregate statistics for a supplier (all sent + received).

    Args:
        transmissions: List of transmission documents
        receipts: List of receipt documents

    Returns:
        Dictionary with sent_count, received_count, total_files, total_size
    """
    sent_files = []
    received_files = []

    for trans in transmissions:
        sent_files.extend(trans.get('files', []))

    for receipt in receipts:
        received_files.extend(receipt.get('files', []))

    sent_stats = calculate_folder_statistics(sent_files)
    received_stats = calculate_folder_statistics(received_files)

    return {
        'sent_count': sent_stats['file_count'],
        'received_count': received_stats['file_count'],
        'total_files': sent_stats['file_count'] + received_stats['file_count'],
        'total_size': sent_stats['total_size'] + received_stats['total_size']
    }


def group_events_by_folder_name(events: List[Dict]) -> Dict[str, List[Dict]]:
    """
    Group events by their exact folder_name to track versions.
    Multiple entries with the same folder_name represent different versions.

    Args:
        events: List of transmission or receipt dictionaries

    Returns:
        Dictionary mapping folder names to lists of versions (sorted by date descending)
    """
    from collections import defaultdict

    grouped = defaultdict(list)

    for event in events:
        folder_name = event.get('folder_name', 'Unknown')
        grouped[folder_name].append(event)

    # Sort each group by date (newest first)
    for folder_name in grouped:
        grouped[folder_name].sort(key=lambda x: x.get('date', ''), reverse=True)

    return dict(grouped)


def create_file_link(file_path: str, link_text: str = "Open") -> str:
    """
    Create clickable link to open file in system default application.

    Args:
        file_path: Absolute path to file
        link_text: Display text for link

    Returns:
        Markdown link string
    """
    try:
        # Convert to absolute path and normalize
        abs_path = str(Path(file_path).resolve())

        # URL encode the path
        encoded_path = quote(abs_path.replace('\\', '/'))

        # Platform-specific file URL format
        if platform.system() == 'Windows':
            file_url = f"file:///{encoded_path}"
        else:
            file_url = f"file://{encoded_path}"

        return f"[{link_text}]({file_url})"
    except Exception as e:
        logger.error(f"Error creating file link for {file_path}: {e}")
        return f"⚠️ {link_text} (path error)"


def run_startup_crawler() -> tuple[bool, str]:
    """
    Run the crawler on dashboard startup to refresh data.

    Returns:
        Tuple of (success: bool, message: str)
    """
    try:
        # Run crawler with 5 minute timeout
        result = subprocess.run(
            [sys.executable, "run_crawler.py"],
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes
        )

        if result.returncode == 0:
            return True, "Data refreshed successfully"
        else:
            error_msg = result.stderr if result.stderr else "Unknown error"
            logger.warning(f"Crawler completed with errors: {error_msg}")
            return False, f"Crawler completed with warnings: {error_msg[:100]}"
    except subprocess.TimeoutExpired:
        logger.error("Crawler timed out after 5 minutes")
        return False, "Crawler timed out after 5 minutes"
    except Exception as e:
        logger.error(f"Error running crawler: {e}")
        return False, f"Error refreshing data: {str(e)[:100]}"


def run_manual_refresh() -> tuple[bool, str]:
    """
    Run manual refresh synchronously (not in background).

    Returns:
        Tuple of (success: bool, message: str)
    """
    try:
        result = subprocess.run(
            [sys.executable, "run_crawler.py"],
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes
        )

        if result.returncode == 0:
            return True, "Data refreshed successfully"
        else:
            error_msg = result.stderr if result.stderr else "Unknown error"
            logger.warning(f"Manual refresh completed with errors: {error_msg}")
            return False, f"Completed with warnings: {error_msg[:100]}"
    except subprocess.TimeoutExpired:
        logger.error("Manual refresh timed out")
        return False, "Refresh timed out after 5 minutes"
    except Exception as e:
        logger.error(f"Manual refresh error: {e}")
        return False, f"Error: {str(e)[:100]}"


def create_download_button(file_path: str, button_label: str = "⬇️ Download", key_suffix: str = ""):
    """
    Create Streamlit download button for a file.

    Args:
        file_path: Absolute path to file
        button_label: Display text for button
        key_suffix: Unique suffix for button key

    Returns:
        Streamlit download button widget
    """
    try:
        if not Path(file_path).exists():
            st.caption("⚠️ File not found")
            return None

        with open(file_path, 'rb') as f:
            file_data = f.read()

        file_name = Path(file_path).name

        return st.download_button(
            label=button_label,
            data=file_data,
            file_name=file_name,
            mime='application/octet-stream',
            key=f"download_{key_suffix}_{hash(file_path)}"
        )
    except Exception as e:
        logger.error(f"Error creating download button for {file_path}: {e}")
        st.caption(f"⚠️ Download error: {str(e)[:50]}")
        return None


def create_preview_button(file_path: str, key_suffix: str = ""):
    """
    Create preview button that opens file in preview mode.

    Args:
        file_path: Path to file
        key_suffix: Unique suffix for button key

    Returns:
        None (displays button in Streamlit)
    """
    if st.button("👁️", key=f"preview_{key_suffix}_{hash(file_path)}", help="Preview file"):
        st.session_state.preview_file = file_path
        st.rerun()


def render_file_preview():
    """
    Render file preview with back button and download option.

    Returns:
        None (displays preview in Streamlit)
    """
    file_path = st.session_state.preview_file

    if not file_path:
        return

    path = Path(file_path)

    # Header with back button and download
    col1, col2, col3 = st.columns([1, 5, 1])

    with col1:
        if st.button("⬅️ Back", key="preview_back"):
            st.session_state.preview_file = None
            st.rerun()

    with col2:
        st.markdown(f"### 📄 {path.name}")

    with col3:
        create_download_button(file_path, "⬇️ Download", key_suffix="preview_download")

    st.divider()

    # Check if file exists
    if not path.exists():
        st.error(f"⚠️ File not found: {file_path}")
        return

    # Get file extension
    file_ext = path.suffix.lower()

    try:
        # Preview based on file type
        if file_ext == '.pdf':
            # PDF preview using base64 encoding in iframe
            with open(path, 'rb') as f:
                pdf_bytes = f.read()

            import base64
            base64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
            pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800px" type="application/pdf"></iframe>'
            st.markdown(pdf_display, unsafe_allow_html=True)

        elif file_ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.svg']:
            # Image preview
            st.image(str(path), use_container_width=True)

        elif file_ext in ['.txt', '.md', '.log', '.json', '.xml', '.csv', '.py', '.js', '.html', '.css']:
            # Text file preview
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Syntax highlighting for code files
            if file_ext in ['.py', '.js', '.html', '.css', '.json', '.xml']:
                st.code(content, language=file_ext[1:])
            else:
                st.text_area("File Content", content, height=600, disabled=True)

        else:
            # Unsupported file type
            st.info(f"📄 Preview not available for {file_ext} files. Use the download button above.")
            st.caption(f"File size: {format_file_size(path.stat().st_size)}")

    except Exception as e:
        logger.error(f"Error previewing file {file_path}: {e}")
        st.error(f"⚠️ Error loading preview: {str(e)[:200]}")


def build_folder_tree(file_paths: List[str], base_path: str) -> Dict[str, Any]:
    """
    Build nested folder structure from flat file list.

    Args:
        file_paths: List of absolute file paths
        base_path: Root folder path to remove from display

    Returns:
        Nested dict representing folder hierarchy
    """
    tree = {}

    for path in file_paths:
        try:
            relative_path = path.replace(base_path, '').lstrip('/').lstrip('\\')
            parts = relative_path.split(os.sep)

            current_level = tree
            for i, part in enumerate(parts):
                if i == len(parts) - 1:  # File
                    if '__files__' not in current_level:
                        current_level['__files__'] = []
                    current_level['__files__'].append({
                        'name': part,
                        'path': path
                    })
                else:  # Folder
                    if part not in current_level:
                        current_level[part] = {}
                    current_level = current_level[part]
        except Exception as e:
            logger.error(f"Error parsing path {path}: {e}")
            continue

    return tree


def render_folder_tree(tree: Dict[str, Any], indent_level: int = 0, key_prefix: str = ""):
    """
    Recursively render folder tree structure with indentation and file links.

    Args:
        tree: Nested dict representing folder hierarchy
        indent_level: Current indentation level (for recursion)
        key_prefix: Prefix for unique widget keys
    """
    indent = "  " * indent_level

    # Render folders first
    for folder_name, subtree in sorted(tree.items()):
        if folder_name == '__files__':
            continue

        st.markdown(f"{indent}📁 **{folder_name}**")
        render_folder_tree(subtree, indent_level + 1, f"{key_prefix}_{folder_name}")

    # Render files
    if '__files__' in tree:
        for file_info in sorted(tree['__files__'], key=lambda x: x['name']):
            file_name = file_info['name']
            file_path = file_info['path']

            # Use tight columns for close icon alignment
            col1, col2, col3 = st.columns([10, 1, 1])
            with col1:
                st.markdown(f"{indent}📄 {file_name}")
            with col2:
                create_preview_button(file_path, key_suffix=f"{key_prefix}_{file_name}")
            with col3:
                create_download_button(
                    file_path,
                    "⬇️",
                    key_suffix=f"{key_prefix}_{file_name}"
                )


def main():
    """Main application logic."""

    # Title
    st.title("📊 RFQ Dashboard")

    # Initialize session state
    if 'selected_project' not in st.session_state:
        st.session_state.selected_project = None
    if 'data_refreshed' not in st.session_state:
        st.session_state.data_refreshed = False
    if 'last_refresh_time' not in st.session_state:
        st.session_state.last_refresh_time = None
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 1
    if 'search_term' not in st.session_state:
        st.session_state.search_term = ''
    if 'sort_option' not in st.session_state:
        st.session_state.sort_option = "Project Number (Descending)"
    if 'selected_suppliers' not in st.session_state:
        st.session_state.selected_suppliers = []
    if 'date_range_start' not in st.session_state:
        st.session_state.date_range_start = None
    if 'date_range_end' not in st.session_state:
        st.session_state.date_range_end = None
    if 'preview_file' not in st.session_state:
        st.session_state.preview_file = None
    if 'selected_supplier' not in st.session_state:
        st.session_state.selected_supplier = None

    # Initialize database connection
    db_manager = initialize_db_manager()

    if db_manager is None:
        return  # Exit if database connection failed

    # Fetch projects and suppliers
    with st.spinner("Loading projects from database..."):
        all_projects = fetch_projects(db_manager)
        all_suppliers = fetch_all_suppliers(db_manager)

    # Run startup crawler ONLY if database is empty AND not already attempted this session
    if not all_projects and not st.session_state.data_refreshed:
        with st.spinner("🔄 Database is empty. Running initial data scan..."):
            success, message = run_startup_crawler()
            st.session_state.data_refreshed = True

            if success:
                st.success(f"✅ {message}")
                st.rerun()  # Reload to show the data
            elif "timeout" in message.lower():
                st.error(f"⏱️ {message}")
                st.info("Dashboard will load with existing data. Please check crawler logs for details.")
            else:
                st.warning(f"⚠️ {message}")
                st.info("You can manually refresh data using the button in the sidebar.")

    # Handle empty project list (after potential refresh attempt)
    if not all_projects:
        st.info("📭 No projects found. Use the '🔄 Refresh Data' button in the left panel to scan for projects.")
        # Don't return - let the panel render so user can click refresh button

    # Three-panel layout: Left (Projects) | Center (Content) | Right (Suppliers)
    # Left: 20%, Center: 55%, Right: 25%
    left_col, center_col, right_col = st.columns([2, 5.5, 2.5])

    # LEFT PANEL - Project List with Filters and Pagination
    with left_col:
        # Manual Refresh Button at top
        if st.button("🔄 Refresh Data", key="refresh_btn_left", use_container_width=True):
            with st.spinner("🔄 Refreshing data..."):
                success, message = run_manual_refresh()
                st.session_state.last_refresh_time = datetime.now()
                fetch_projects.clear()
                fetch_supplier_data.clear()
                fetch_all_suppliers.clear()

                if success:
                    st.success("✅ Refreshed")
                    st.rerun()
                elif "timeout" in message.lower():
                    st.error(f"⏱️ {message}")
                else:
                    st.warning(f"⚠️ {message}")

        st.divider()

        # Collapsible Filters Section
        with st.expander("🔍 Filters", expanded=False):
            # Search input
            search_term = st.text_input(
                "Search Project Number",
                placeholder="Enter project number...",
                key="search_input"
            )

            # Supplier multiselect filter
            if all_suppliers:
                selected_suppliers = st.multiselect(
                    "Filter by Supplier",
                    options=all_suppliers,
                    default=st.session_state.selected_suppliers,
                    key="supplier_filter"
                )
                st.session_state.selected_suppliers = selected_suppliers
            else:
                selected_suppliers = []

            # Date range filter
            col_date1, col_date2 = st.columns(2)
            with col_date1:
                date_start = st.date_input(
                    "From Date",
                    value=st.session_state.date_range_start,
                    key="date_start"
                )
                if date_start:
                    st.session_state.date_range_start = datetime.combine(date_start, datetime.min.time())
            with col_date2:
                date_end = st.date_input(
                    "To Date",
                    value=st.session_state.date_range_end,
                    key="date_end"
                )
                if date_end:
                    st.session_state.date_range_end = datetime.combine(date_end, datetime.max.time())

            # Clear filters button
            if search_term or selected_suppliers or st.session_state.date_range_start or st.session_state.date_range_end:
                if st.button("🗑️ Clear All Filters", key="clear_filters", use_container_width=True):
                    st.session_state.search_term = ''
                    st.session_state.selected_suppliers = []
                    st.session_state.date_range_start = None
                    st.session_state.date_range_end = None
                    st.session_state.current_page = 1
                    st.rerun()

        # If no filters in expander, use empty values
        if 'search_term' not in locals():
            search_term = ''
            selected_suppliers = st.session_state.selected_suppliers

        # Sort options (always visible)
        sort_option = st.selectbox(
            "Sort by",
            [
                "Project Number (Descending)",
                "Project Number (Ascending)",
                "Last Scanned (Newest First)",
                "Last Scanned (Oldest First)"
            ],
            key="sort_select"
        )

        # Filter and sort projects
        filtered_projects = filter_projects(
            all_projects,
            search_term,
            selected_suppliers,
            st.session_state.date_range_start,
            st.session_state.date_range_end,
            db_manager
        )
        sorted_projects = sort_projects(filtered_projects, sort_option)

        # Pagination setup
        ITEMS_PER_PAGE = 15
        total_projects = len(sorted_projects)
        total_pages = max(1, (total_projects + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE)

        # Reset to page 1 if current page is out of bounds
        if st.session_state.current_page > total_pages:
            st.session_state.current_page = 1

        # Calculate pagination indices
        start_idx = (st.session_state.current_page - 1) * ITEMS_PER_PAGE
        end_idx = min(start_idx + ITEMS_PER_PAGE, total_projects)
        paginated_projects = sorted_projects[start_idx:end_idx]

        # Display filter stats
        st.caption(f"Showing {start_idx + 1}-{end_idx} of {total_projects} projects (Page {st.session_state.current_page}/{total_pages})")

        st.divider()

        # Project selection
        if paginated_projects:
            project_options = [f"Project {p['project_number']}" for p in paginated_projects]

            # Find current selection index
            default_index = 0
            if st.session_state.selected_project:
                try:
                    default_index = next(
                        i for i, p in enumerate(paginated_projects)
                        if p['project_number'] == st.session_state.selected_project['project_number']
                    )
                except StopIteration:
                    default_index = 0

            selected_project_label = st.radio(
                "Select Project",
                project_options,
                index=default_index,
                label_visibility="collapsed",
                key="project_radio"
            )

            # Update session state with selected project
            selected_index = project_options.index(selected_project_label)
            st.session_state.selected_project = paginated_projects[selected_index]
        else:
            st.warning("No projects match your filters.")
            st.session_state.selected_project = None

        # Pagination controls
        if total_pages > 1:
            st.divider()
            col_prev, col_info, col_next = st.columns([1, 2, 1])

            with col_prev:
                if st.button("◀", key="prev_page", disabled=st.session_state.current_page <= 1):
                    st.session_state.current_page -= 1
                    st.rerun()

            with col_info:
                st.markdown(f"<div style='text-align: center; padding: 0.5rem;'>Page {st.session_state.current_page} / {total_pages}</div>", unsafe_allow_html=True)

            with col_next:
                if st.button("▶", key="next_page", disabled=st.session_state.current_page >= total_pages):
                    st.session_state.current_page += 1
                    st.rerun()

    # CENTER PANEL - Main content area for selected supplier
    with center_col:
        # Check if in preview mode
        if st.session_state.preview_file:
            render_file_preview()
            return  # Exit early, don't render project details

        if st.session_state.selected_project:
            project = st.session_state.selected_project

            # Fetch supplier data for the project
            with st.spinner("Loading supplier data..."):
                supplier_data = fetch_supplier_data(db_manager, project['project_number'])

            # Auto-select first supplier if none selected or current selection invalid
            if supplier_data:
                supplier_names = [d['supplier']['supplier_name'] for d in supplier_data]

                if (not st.session_state.selected_supplier or
                    st.session_state.selected_supplier not in supplier_names):
                    st.session_state.selected_supplier = supplier_names[0]

                # Find the selected supplier's data
                selected_data = next(
                    (d for d in supplier_data if d['supplier']['supplier_name'] == st.session_state.selected_supplier),
                    None
                )

                if selected_data:
                    supplier = selected_data['supplier']
                    transmissions = selected_data['transmissions']
                    receipts = selected_data['receipts']

                    # Header: Project + Supplier
                    st.markdown(f"## Project {project['project_number']} - {supplier['supplier_name']}")

                    # Display last scanned date
                    if 'last_scanned' in project and project['last_scanned']:
                        formatted_date = format_timestamp(project['last_scanned'])
                        st.caption(f"📅 Last Scanned: {formatted_date}")

                    # Calculate and display supplier statistics
                    supplier_stats = calculate_supplier_statistics(transmissions, receipts)
                    stats_html = (
                        f"{get_statistics_badge('Files', str(supplier_stats['total_files']), 'files')} "
                        f"{get_statistics_badge('Size', format_file_size(supplier_stats['total_size']), 'size')}"
                    )
                    st.markdown(stats_html, unsafe_allow_html=True)

                    st.divider()

                    # Two-column layout: Sent (left) | Received (right)
                    col_sent, col_received = st.columns(2)

                    # Left column: Sent Transmissions
                    with col_sent:
                            st.subheader("📤 Sent Transmissions")

                            if not transmissions:
                                st.caption("_No transmissions found_")
                            else:
                                # Group transmissions by folder name for version tracking
                                grouped_transmissions = group_events_by_folder_name(transmissions)

                                for group_idx, (folder_name, versions) in enumerate(grouped_transmissions.items()):
                                    # If multiple versions exist, show version history
                                    if len(versions) > 1:
                                        # Calculate combined statistics
                                        total_files = sum(len(v.get('files', [])) for v in versions)
                                        total_size = sum(
                                            calculate_folder_statistics(v.get('files', []))['total_size']
                                            for v in versions
                                        )

                                        with st.expander(f"📂 {folder_name} ({len(versions)} versions)", expanded=False):
                                            st.caption(f"{total_files} files • {format_file_size(total_size)}")
                                            st.markdown("---")
                                            st.caption("**Version History** (newest first)")

                                            for trans_idx, trans in enumerate(versions):
                                                files = trans.get('files', [])
                                                version_date = format_timestamp(trans.get('date', 'N/A'))

                                                # Compact version display - just timestamp and folder structure
                                                st.markdown(f"**Version {len(versions) - trans_idx}:** {version_date}")

                                                file_count = len(files)
                                                st.caption(f"{file_count} files")

                                                # Build and render folder tree (compact)
                                                if files:
                                                    files_to_display = files[:50]  # Limit to first 50 for version history
                                                    try:
                                                        tree = build_folder_tree(files_to_display, trans.get('folder_path', ''))
                                                        with st.expander("📁 Folder Structure", expanded=False):
                                                            render_folder_tree(
                                                                tree,
                                                                key_prefix=f"tree_sent_{supplier['supplier_name']}_{group_idx}_{trans_idx}"
                                                            )
                                                    except Exception as e:
                                                        logger.error(f"Error rendering folder tree for transmission: {e}")
                                                        st.caption(f"⚠️ Error displaying folder structure")

                                                if trans_idx < len(versions) - 1:
                                                    st.markdown("---")  # Separator between versions

                                    else:
                                        # Single version - render directly without version history
                                        trans = versions[0]
                                        trans_idx = 0

                                        # Wrap each transmission in a container/card
                                        with st.container():
                                            st.markdown('<div class="event-card">', unsafe_allow_html=True)

                                            folder_name = trans.get('folder_name', 'Unknown')
                                            files = trans.get('files', [])

                                            # Calculate date folder statistics
                                            folder_stats = calculate_folder_statistics(files)
                                            folder_stats_html = (
                                                f"{get_statistics_badge('Files', str(folder_stats['file_count']), 'files')} "
                                                f"{get_statistics_badge('Size', format_file_size(folder_stats['total_size']), 'size')}"
                                            )

                                            # Header bar with title
                                            st.markdown(f'<div class="event-card-header"><strong>📂 {folder_name}</strong></div>', unsafe_allow_html=True)

                                            # Body with metadata and stats
                                            st.markdown('<div class="event-card-body">', unsafe_allow_html=True)
                                            st.markdown(folder_stats_html, unsafe_allow_html=True)

                                            # Display metadata
                                            sent_date = format_timestamp(trans.get('date', 'N/A'))
                                            st.caption(f"📅 Date: {sent_date}")

                                            # Build and render folder tree (same as receipts)
                                            if files:
                                                # Pagination for large file lists
                                                if len(files) > 100:
                                                    items_per_page = 50
                                                    total_pages = (len(files) + items_per_page - 1) // items_per_page

                                                    page = st.number_input(
                                                        f"Page",
                                                        min_value=1,
                                                        max_value=total_pages,
                                                        value=1,
                                                        key=f"page_sent_{supplier['supplier_name']}_{trans_idx}"
                                                    )

                                                    start_idx = (page - 1) * items_per_page
                                                    end_idx = start_idx + items_per_page
                                                    st.caption(f"Showing {start_idx + 1}-{min(end_idx, len(files))} of {len(files)} files")
                                                    files_to_display = files[start_idx:end_idx]
                                                else:
                                                    files_to_display = files

                                                # Build folder tree
                                                try:
                                                    tree = build_folder_tree(files_to_display, trans.get('folder_path', ''))

                                                    with st.expander("📁 Folder Structure", expanded=True):
                                                        render_folder_tree(
                                                            tree,
                                                            key_prefix=f"tree_sent_{supplier['supplier_name']}_{trans_idx}"
                                                        )
                                                except Exception as e:
                                                    logger.error(f"Error rendering folder tree for transmission: {e}")
                                                    st.error(f"Error displaying folder structure: {str(e)[:100]}")

                                                    # Fallback: flat file list
                                                    with st.expander(f"📄 Files ({len(files_to_display)} items)"):
                                                        for file_idx, file_path in enumerate(files_to_display):
                                                            col1, col2 = st.columns([3, 1])
                                                            with col1:
                                                                link = create_file_link(file_path, Path(file_path).name)
                                                                st.markdown(f"📄 {link}")
                                                            with col2:
                                                                create_download_button(
                                                                    file_path,
                                                                    "⬇️",
                                                                    key_suffix=f"flat_sent_{supplier['supplier_name']}_{trans_idx}_{file_idx}"
                                                                )

                                            st.markdown('</div>', unsafe_allow_html=True)  # Close event-card-body
                                            st.markdown('</div>', unsafe_allow_html=True)  # Close event-card

                    # Right column: Received Submissions
                    with col_received:
                        st.subheader("📥 Received Submissions")

                        if not receipts:
                            st.caption("_No submissions received_")
                        else:
                            # Group receipts by folder name for version tracking
                            grouped_receipts = group_events_by_folder_name(receipts)

                            for group_idx, (folder_name, versions) in enumerate(grouped_receipts.items()):
                                # If multiple versions exist, show version history
                                if len(versions) > 1:
                                    # Calculate combined statistics
                                    total_files = sum(len(v.get('files', [])) for v in versions)
                                    total_size = sum(
                                        calculate_folder_statistics(v.get('files', []))['total_size']
                                        for v in versions
                                    )

                                    with st.expander(f"📂 {folder_name} ({len(versions)} versions)", expanded=False):
                                        st.caption(f"{total_files} files • {format_file_size(total_size)}")
                                        st.markdown("---")
                                        st.caption("**Version History** (newest first)")

                                        for receipt_idx, receipt in enumerate(versions):
                                            received_files = receipt.get('files', [])
                                            version_date = format_timestamp(receipt.get('date', 'N/A'))

                                            # Compact version display - just timestamp and folder structure
                                            st.markdown(f"**Version {len(versions) - receipt_idx}:** {version_date}")

                                            file_count = len(received_files)
                                            st.caption(f"{file_count} files")

                                            # Build and render folder tree (compact)
                                            if received_files:
                                                files_to_display = received_files[:50]  # Limit to first 50 for version history
                                                try:
                                                    tree = build_folder_tree(files_to_display, receipt.get('folder_path', ''))
                                                    with st.expander("📁 Folder Structure", expanded=False):
                                                        render_folder_tree(
                                                            tree,
                                                            key_prefix=f"tree_rcv_{supplier['supplier_name']}_{group_idx}_{receipt_idx}"
                                                        )
                                                except Exception as e:
                                                    logger.error(f"Error rendering folder tree: {e}")
                                                    st.caption(f"⚠️ Error displaying folder structure")

                                            if receipt_idx < len(versions) - 1:
                                                st.markdown("---")  # Separator between versions

                                else:
                                    # Single version - render directly without version history
                                    receipt = versions[0]
                                    receipt_idx = 0

                                    # Wrap each receipt in a container/card
                                    with st.container():
                                        st.markdown('<div class="event-card">', unsafe_allow_html=True)

                                        folder_name = receipt.get('folder_name', 'Unknown')
                                        received_files = receipt.get('files', [])

                                        # Calculate date folder statistics
                                        folder_stats = calculate_folder_statistics(received_files)
                                        folder_stats_html = (
                                            f"{get_statistics_badge('Files', str(folder_stats['file_count']), 'files')} "
                                            f"{get_statistics_badge('Size', format_file_size(folder_stats['total_size']), 'size')}"
                                        )

                                        # Header bar with title
                                        st.markdown(f'<div class="event-card-header"><strong>📂 {folder_name}</strong></div>', unsafe_allow_html=True)

                                        # Body with metadata and stats
                                        st.markdown('<div class="event-card-body">', unsafe_allow_html=True)
                                        st.markdown(folder_stats_html, unsafe_allow_html=True)

                                        # Display metadata
                                        received_date = format_timestamp(receipt.get('date', 'N/A'))
                                        st.caption(f"📅 Date: {received_date}")

                                        # Build and render folder tree
                                        if received_files:
                                            # Pagination for large file lists
                                            if len(received_files) > 100:
                                                items_per_page = 50
                                                total_pages = (len(received_files) + items_per_page - 1) // items_per_page

                                                page = st.number_input(
                                                    f"Page",
                                                    min_value=1,
                                                    max_value=total_pages,
                                                    value=1,
                                                    key=f"page_{supplier['supplier_name']}_{receipt_idx}"
                                                )

                                                start_idx = (page - 1) * items_per_page
                                                end_idx = start_idx + items_per_page
                                                files_to_display = received_files[start_idx:end_idx]

                                                st.caption(f"Showing {start_idx + 1}-{min(end_idx, len(received_files))} of {len(received_files)} files")
                                            else:
                                                files_to_display = received_files

                                            # Build folder tree
                                            try:
                                                tree = build_folder_tree(files_to_display, receipt.get('folder_path', ''))

                                                # Render tree with expander for large structures
                                                with st.expander("📁 Folder Structure", expanded=True):
                                                    render_folder_tree(
                                                        tree,
                                                        key_prefix=f"tree_{supplier['supplier_name']}_{receipt_idx}"
                                                    )
                                            except Exception as e:
                                                logger.error(f"Error rendering folder tree: {e}")
                                                st.error(f"Error displaying folder structure: {str(e)[:100]}")

                                                # Fallback: flat file list
                                                st.caption("Showing flat file list:")
                                                for file_idx, file_path in enumerate(files_to_display[:20]):
                                                    file_name = Path(file_path).name
                                                    file_col1, file_col2 = st.columns([3, 1])
                                                    with file_col1:
                                                        file_link = create_file_link(file_path, file_name)
                                                        st.markdown(f"📄 {file_link}")
                                                    with file_col2:
                                                        create_download_button(
                                                            file_path,
                                                            "⬇️",
                                                            key_suffix=f"rcv_{supplier['supplier_name']}_{receipt_idx}_{file_idx}"
                                                        )

                                        st.markdown('</div>', unsafe_allow_html=True)  # Close event-card-body
                                        st.markdown('</div>', unsafe_allow_html=True)  # Close event-card

            else:
                # No supplier data or no valid selection
                st.info("📭 No supplier data available for this project.")
        else:
            # Default state - no project selected
            st.markdown(
                """
                <div style='text-align: center; padding: 100px 0;'>
                    <h2>👈 Select a project from the left panel to see details.</h2>
                </div>
                """,
                unsafe_allow_html=True
            )

    # RIGHT PANEL - Supplier Selection List
    with right_col:
        if st.session_state.selected_project:
            st.markdown("### 🏢 Suppliers")

            # Fetch supplier data
            with st.spinner("Loading..."):
                supplier_data = fetch_supplier_data(db_manager, st.session_state.selected_project['project_number'])

            if supplier_data:
                # Create radio buttons for supplier selection
                supplier_names = [d['supplier']['supplier_name'] for d in supplier_data]

                # Find index of currently selected supplier
                try:
                    default_index = supplier_names.index(st.session_state.selected_supplier)
                except (ValueError, AttributeError):
                    default_index = 0

                selected_supplier = st.radio(
                    "Select Supplier",
                    supplier_names,
                    index=default_index,
                    label_visibility="collapsed",
                    key="supplier_radio"
                )

                # Update session state if selection changed
                if selected_supplier != st.session_state.selected_supplier:
                    st.session_state.selected_supplier = selected_supplier
                    st.rerun()
            else:
                st.caption("_No suppliers found_")
        else:
            st.markdown(
                """
                <div style='text-align: center; padding-top: 50px;'>
                    <p style='color: #9CA3AF;'>Select a project to view suppliers</p>
                </div>
                """,
                unsafe_allow_html=True
            )


if __name__ == "__main__":
    main()
