"""
UI component for the center panel of the dashboard.
"""
import logging
import streamlit as st

from rfq_tracker.db_manager import DBManager
from dashboard.data.queries import fetch_supplier_data
from dashboard.logic.processing import (
    calculate_supplier_statistics,
    group_events_by_folder_name,
    calculate_folder_statistics,
    build_folder_tree
)
from dashboard.styles import get_statistics_badge, format_file_size
from dashboard.ui.components.file_widgets import render_folder_tree
from dashboard.utils.helpers import format_timestamp

logger = logging.getLogger(__name__)


def render_center_panel(center_col, db_manager: DBManager):
    """
    Renders the center panel with project details and supplier submissions.

    Args:
        center_col: The Streamlit column to render into.
        db_manager: The database manager instance.
    """
    with center_col:
        # Check if in preview mode (handled in app.py, but good practice to check)
        if st.session_state.get('preview_file'):
            # The file_preview view will be rendered by the main app.py instead
            return

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
                        render_submissions_column(transmissions, "sent", supplier['supplier_name'])

                    # Right column: Received Submissions
                    with col_received:
                        st.subheader("📥 Received Submissions")
                        render_submissions_column(receipts, "received", supplier['supplier_name'])

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


def render_submissions_column(events: list, event_type: str, supplier_name: str):
    """
    Renders a column of submissions (sent or received).

    Args:
        events: A list of submission event dictionaries.
        event_type: The type of event ('sent' or 'received').
        supplier_name: The name of the supplier.
    """
    if not events:
        st.caption(f"_No {event_type} submissions found_")
        return

    grouped_events = group_events_by_folder_name(events)

    for group_idx, (folder_name, versions) in enumerate(grouped_events.items()):
        if len(versions) > 1:
            render_versioned_submission(versions, event_type, supplier_name, group_idx, folder_name)
        else:
            render_single_submission(versions[0], event_type, supplier_name, group_idx)


def render_versioned_submission(versions: list, event_type: str, supplier_name: str, group_idx: int, folder_name: str):
    """Renders a submission with multiple versions."""
    total_files = sum(len(v.get('files', [])) for v in versions)
    total_size = sum(
        calculate_folder_statistics(v.get('files', []))['total_size']
        for v in versions
    )

    with st.expander(f"📂 {folder_name} ({len(versions)} versions)", expanded=False):
        st.caption(f"{total_files} files • {format_file_size(total_size)}")
        st.markdown("---")
        st.caption("**Version History** (newest first)")

        for version_idx, version in enumerate(versions):
            files = version.get('files', [])
            version_date = format_timestamp(version.get('date', 'N/A'))

            st.markdown(f"**Version {len(versions) - version_idx}:** {version_date}")
            st.caption(f"{len(files)} files")

            if files:
                files_to_display = files[:50]  # Limit to first 50 for version history
                try:
                    tree = build_folder_tree(files_to_display, version.get('folder_path', ''))
                    with st.expander("📁 Folder Structure", expanded=False):
                        render_folder_tree(
                            tree,
                            key_prefix=f"tree_{event_type}_{supplier_name}_{group_idx}_{version_idx}"
                        )
                except Exception as e:
                    logger.error(f"Error rendering folder tree for versioned submission: {e}")
                    st.caption("⚠️ Error displaying folder structure")

            if version_idx < len(versions) - 1:
                st.markdown("---")


def render_single_submission(event: dict, event_type: str, supplier_name: str, event_idx: int):
    """Renders a single submission card."""
    with st.container():
        st.markdown('<div class="event-card">', unsafe_allow_html=True)

        folder_name = event.get('folder_name', 'Unknown')
        files = event.get('files', [])

        folder_stats = calculate_folder_statistics(files)
        folder_stats_html = (
            f"{get_statistics_badge('Files', str(folder_stats['file_count']), 'files')} "
            f"{get_statistics_badge('Size', format_file_size(folder_stats['total_size']), 'size')}"
        )

        st.markdown(f'<div class="event-card-header"><strong>📂 {folder_name}</strong></div>', unsafe_allow_html=True)
        st.markdown('<div class="event-card-body">', unsafe_allow_html=True)
        st.markdown(folder_stats_html, unsafe_allow_html=True)

        event_date = format_timestamp(event.get('date', 'N/A'))
        st.caption(f"📅 Date: {event_date}")

        if files:
            render_file_list_with_pagination(files, event_type, supplier_name, event_idx, event.get('folder_path', ''))

        st.markdown('</div></div>', unsafe_allow_html=True)


def render_file_list_with_pagination(files: list, event_type: str, supplier_name: str, event_idx: int, base_path: str):
    """Renders a paginated list of files with a folder tree."""
    if len(files) > 100:
        items_per_page = 50
        total_pages = (len(files) + items_per_page - 1) // items_per_page
        page_key = f"page_{event_type}_{supplier_name}_{event_idx}"
        page = st.number_input("Page", min_value=1, max_value=total_pages, value=1, key=page_key)

        start_idx = (page - 1) * items_per_page
        end_idx = start_idx + items_per_page
        st.caption(f"Showing {start_idx + 1}-{min(end_idx, len(files))} of {len(files)} files")
        files_to_display = files[start_idx:end_idx]
    else:
        files_to_display = files

    try:
        tree = build_folder_tree(files_to_display, base_path)
        with st.expander("📁 Folder Structure", expanded=True):
            render_folder_tree(
                tree,
                key_prefix=f"tree_{event_type}_{supplier_name}_{event_idx}"
            )
    except Exception as e:
        logger.error(f"Error rendering folder tree for single submission: {e}")
        st.error(f"Error displaying folder structure: {str(e)[:100]}")
        # Fallback to flat list can be implemented here if needed