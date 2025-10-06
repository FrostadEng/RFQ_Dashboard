"""
Left panel component for RFQ Dashboard.
Contains project list, filters, search, pagination, and project selection.
"""

import streamlit as st
from datetime import datetime
from typing import List, Dict, Any

from rfq_tracker.db_manager import DBManager
from dashboard.data.queries import fetch_projects, fetch_all_suppliers
from dashboard.logic.processing import filter_projects, sort_projects
from dashboard.utils.helpers import run_manual_refresh


def render_left_panel(left_col, db_manager: DBManager, all_projects: List[Dict[str, Any]], all_suppliers: List[str]):
    """
    Render left panel with filters, search, pagination, and project selection.

    Args:
        left_col: Streamlit column object
        db_manager: Database manager instance
        all_projects: List of all project dictionaries
        all_suppliers: List of all supplier names
    """
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


# Import fetch_supplier_data to clear cache
from dashboard.data.queries import fetch_supplier_data
