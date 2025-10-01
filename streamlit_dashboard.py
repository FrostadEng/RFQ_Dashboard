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
import threading
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from urllib.parse import quote
import streamlit as st
from dotenv import load_dotenv

from rfq_tracker.db_manager import DBManager

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


def run_crawler_subprocess() -> (bool, str):
    """
    Runs the crawler script as a subprocess and returns status and output.
    Timeout is 5 minutes.
    """
    command = [sys.executable, "run_crawler.py"]
    try:
        process = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=300,  # 5-minute timeout
            check=True  # Raise exception for non-zero exit codes
        )
        logger.info("Crawler subprocess finished successfully.")
        logger.debug(f"Crawler output:\n{process.stdout}")
        return True, "Crawler finished successfully."
    except subprocess.TimeoutExpired:
        logger.error("Crawler subprocess timed out.")
        return False, "Crawler process timed out after 5 minutes."
    except subprocess.CalledProcessError as e:
        error_message = f"Crawler process failed with exit code {e.returncode}."
        logger.error(error_message)
        logger.error(f"Crawler stderr:\n{e.stderr}")
        return False, f"{error_message}\nError: {e.stderr[:200]}"
    except Exception as e:
        logger.error(f"An unexpected error occurred while running the crawler: {e}")
        return False, f"An unexpected error occurred: {str(e)}"


def run_initial_crawler():
    """Run crawler on first load if not already run."""
    if not st.session_state.get('initial_crawl_run', False):
        with st.spinner("Performing initial data scan... This may take a few minutes."):
            success, message = run_crawler_subprocess()
            if success:
                st.toast("✅ Initial data scan complete!", icon="🎉")
            else:
                st.toast(f"⚠️ Initial scan failed: {message}", icon="🔥")
        st.session_state.initial_crawl_run = True # Ensure it only runs once
        st.rerun()


def run_refresh_in_thread():
    """Target function to run crawler in a background thread."""
    st.session_state.is_refreshing = True
    st.session_state.refresh_message = ("info", "🔄 Refreshing data...")
    st.rerun() # Update UI to show spinner

    success, message = run_crawler_subprocess()

    if success:
        st.session_state.refresh_message = ("success", f"✅ Successfully refreshed at {datetime.now().strftime('%H:%M:%S')}")
        # Clear caches to force data reload
        st.cache_data.clear()
    else:
        st.session_state.refresh_message = ("error", f"🔥 Refresh failed: {message}")

    st.session_state.is_refreshing = False
    st.session_state.last_refresh = datetime.now()
    st.rerun() # Update UI with final status


def filter_projects(projects: List[Dict[str, Any]], search_term: str) -> List[Dict[str, Any]]:
    """Filter projects by search term (case-insensitive)."""
    if not search_term:
        return projects

    search_lower = search_term.lower()
    return [p for p in projects if search_lower in p['project_number'].lower()]


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

            col1, col2 = st.columns([3, 1])
            with col1:
                link = create_file_link(file_path, f"{indent}📄 {file_name}")
                st.markdown(link)
            with col2:
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
    if 'is_refreshing' not in st.session_state:
        st.session_state.is_refreshing = False
    if 'refresh_message' not in st.session_state:
        st.session_state.refresh_message = None
    if 'last_refresh' not in st.session_state:
        st.session_state.last_refresh = None

    # Initialize database connection
    db_manager = initialize_db_manager()

    if db_manager is None:
        return  # Exit if database connection failed

    # Run initial crawler scan on first launch
    run_initial_crawler()

    # Fetch projects
    with st.spinner("Loading projects from database..."):
        all_projects = fetch_projects(db_manager)

    # Handle empty project list
    if not all_projects:
        st.info("📭 No projects found. Run `python run_crawler.py` to populate data.")
        return

    # Sidebar - Project List
    with st.sidebar:
        st.header("Projects")

        # Search input
        search_term = st.text_input(
            "🔍 Search",
            placeholder="Search Project Number...",
            label_visibility="collapsed"
        )

        # Sort options
        sort_option = st.selectbox(
            "Sort by",
            [
                "Project Number (Descending)",
                "Project Number (Ascending)",
                "Last Scanned (Newest First)",
                "Last Scanned (Oldest First)"
            ]
        )

        # Filter and sort projects
        filtered_projects = filter_projects(all_projects, search_term)
        sorted_projects = sort_projects(filtered_projects, sort_option)

        # Display filter count
        if search_term:
            st.caption(f"Showing {len(sorted_projects)} of {len(all_projects)} projects")
        else:
            st.caption(f"Loaded {len(all_projects)} projects")

        st.divider()

        # Manual Refresh Section
        st.subheader("Manual Refresh")

        if st.button("🔄 Refresh Data", disabled=st.session_state.is_refreshing):
            # Run refresh in a background thread to avoid blocking the UI
            thread = threading.Thread(target=run_refresh_in_thread)
            thread.start()

        # Display refresh status
        if st.session_state.is_refreshing:
            st.info("🔄 Refreshing data...")

        if st.session_state.refresh_message:
            msg_type, msg_text = st.session_state.refresh_message
            if msg_type == "success":
                st.success(msg_text)
            elif msg_type == "error":
                st.error(msg_text)
            elif msg_type == "info" and not st.session_state.is_refreshing:
                 st.info(msg_text)


        if st.session_state.last_refresh:
            st.caption(f"Last refresh: {st.session_state.last_refresh.strftime('%H:%M:%S')}")

        st.divider()

        # Project selection
        if sorted_projects:
            project_options = [f"Project {p['project_number']}" for p in sorted_projects]

            # Find current selection index
            default_index = 0
            if st.session_state.selected_project:
                try:
                    default_index = next(
                        i for i, p in enumerate(sorted_projects)
                        if p['project_number'] == st.session_state.selected_project['project_number']
                    )
                except StopIteration:
                    default_index = 0

            selected_project_label = st.radio(
                "Select Project",
                project_options,
                index=default_index,
                label_visibility="collapsed"
            )

            # Update session state with selected project
            selected_index = project_options.index(selected_project_label)
            st.session_state.selected_project = sorted_projects[selected_index]
        else:
            st.warning("No projects match your search.")
            st.session_state.selected_project = None

    # Main content area
    if st.session_state.selected_project:
        project = st.session_state.selected_project

        # Display project details with clickable project number
        project_path = project.get('path', '')
        project_link = create_file_link(project_path, f"Project {project['project_number']}")
        st.markdown(f"## {project_link}")

        # Display last scanned date
        if 'last_scanned' in project and project['last_scanned']:
            formatted_date = format_timestamp(project['last_scanned'])
            st.caption(f"📅 Last Scanned: {formatted_date}")
        else:
            st.caption("📅 Last Scanned: Not available")

        st.divider()

        st.markdown("### 📋 Supplier Details")

        # Fetch supplier data with spinner
        with st.spinner("Loading supplier data..."):
            supplier_data = fetch_supplier_data(db_manager, project['project_number'])

        # Handle empty supplier list
        if not supplier_data:
            st.info("📭 No suppliers found for this project. Run `python run_crawler.py` to scan for RFQ data.")
        else:
            # Display each supplier in expandable sections
            for idx, data in enumerate(supplier_data):
                supplier = data['supplier']
                transmissions = data['transmissions']
                receipts = data['receipts']

                # Auto-expand first supplier only
                with st.expander(f"🏢 {supplier['supplier_name']}", expanded=(idx == 0)):
                    # Two-column layout: Sent (left) | Received (right)
                    col_sent, col_received = st.columns(2)

                    # Left column: Sent Transmissions
                    with col_sent:
                        st.subheader("📤 Sent Transmissions")

                        if not transmissions:
                            st.caption("_No transmissions found_")
                        else:
                            for trans_idx, trans in enumerate(transmissions):
                                folder_name = trans.get('folder_name', 'Unknown')
                                st.markdown(f"**📂 {folder_name}**")

                                # Display metadata
                                sent_date = format_timestamp(trans.get('date', 'N/A'))
                                st.caption(f"📅 Date: {sent_date}")

                                files = trans.get('files', [])
                                st.caption(f"📁 Files: {len(files)} total")

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

                                st.divider()

                    # Right column: Received Submissions
                    with col_received:
                        st.subheader("📥 Received Submissions")

                        if not receipts:
                            st.caption("_No submissions received_")
                        else:
                            for receipt_idx, receipt in enumerate(receipts):
                                folder_name = receipt.get('folder_name', 'Unknown')
                                st.markdown(f"**📂 {folder_name}**")

                                # Display metadata
                                received_date = format_timestamp(receipt.get('date', 'N/A'))
                                st.caption(f"📅 Date: {received_date}")

                                received_files = receipt.get('files', [])
                                st.caption(f"📁 Files: {len(received_files)} total")

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

                                st.divider()

                # Add divider between suppliers
                if idx < len(supplier_data) - 1:
                    st.divider()

    else:
        # Default state - no project selected
        st.markdown(
            """
            <div style='text-align: center; padding: 100px 0;'>
                <h2>👈 Select a project from the sidebar to see details.</h2>
            </div>
            """,
            unsafe_allow_html=True
        )


if __name__ == "__main__":
    main()
