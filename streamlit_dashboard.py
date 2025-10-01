"""
Streamlit-based RFQ Dashboard
Web interface for viewing and searching RFQ project data
"""

import os
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
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


def main():
    """Main application logic."""

    # Title
    st.title("📊 RFQ Dashboard")

    # Initialize session state
    if 'selected_project' not in st.session_state:
        st.session_state.selected_project = None

    # Initialize database connection
    db_manager = initialize_db_manager()

    if db_manager is None:
        return  # Exit if database connection failed

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

        st.subheader(f"Project {project['project_number']}")

        col1, col2 = st.columns(2)

        with col1:
            st.metric("Project Number", project['project_number'])

        with col2:
            if 'last_scanned' in project and project['last_scanned']:
                formatted_date = format_timestamp(project['last_scanned'])
                st.metric("Last Scanned", formatted_date)
            else:
                st.metric("Last Scanned", "Not available")

        st.divider()

        st.info("**Path:** " + project.get('path', 'N/A'))

        st.divider()

        st.markdown("### 📋 Supplier Details")
        st.info("_(Supplier detail view coming in next spec.)_")

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
