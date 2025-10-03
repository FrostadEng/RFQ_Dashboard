"""
RFQ Dashboard - Main Application Entry Point
Web interface for viewing and searching RFQ project data
"""

import logging
import streamlit as st
from dotenv import load_dotenv

from dashboard.config import load_config
from dashboard.data.queries import initialize_db_manager, fetch_projects, fetch_all_suppliers
from dashboard.ui.views.file_preview import render_file_preview
from dashboard.ui.components.left_panel import render_left_panel
from dashboard.ui.components.center_panel import render_center_panel
from dashboard.ui.components.right_panel import render_right_panel
from dashboard.styles import get_custom_css
from dashboard.utils.helpers import run_startup_crawler

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

    # Render panels
    render_left_panel(left_col, db_manager, all_projects, all_suppliers)
    render_center_panel(center_col, db_manager)
    render_right_panel(right_col, db_manager)


if __name__ == "__main__":
    main()
