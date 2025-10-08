"""
Center panel component for RFQ Dashboard.
Main content area displaying project details, supplier statistics, and transmissions/receipts.
"""

import logging
import streamlit as st
from pathlib import Path

from rfq_tracker.db_manager import DBManager
from dashboard.data.queries import (
    fetch_supplier_data,
    fetch_suppliers_by_partner_type,
    get_project_statistics
)
from dashboard.logic.processing import calculate_supplier_statistics, calculate_folder_statistics, group_events_by_folder_name, build_folder_tree
from dashboard.styles import get_statistics_badge, format_file_size
from dashboard.utils.helpers import format_timestamp, create_file_link
from dashboard.ui.components.file_widgets import create_download_button, render_folder_tree
from dashboard.ui.views.file_preview import render_file_preview

logger = logging.getLogger(__name__)


def render_center_panel(center_col, db_manager: DBManager):
    """
    Render center panel with project details, supplier statistics, and transmission/receipt display.

    Args:
        center_col: Streamlit column object
        db_manager: Database manager instance
    """
    with center_col:
        # Check if in preview mode
        if st.session_state.preview_file:
            render_file_preview()
            return  # Exit early, don't render project details

        if st.session_state.selected_project:
            project = st.session_state.selected_project

            # Get partner type from session state (convert to singular form for backend queries)
            partner_type_display = st.session_state.get('partner_type', 'Suppliers')
            partner_type_backend = 'Supplier' if partner_type_display == 'Suppliers' else 'Contractor'

            # Project Header with Aggregate Statistics (Persistent)
            st.markdown(f"## Project {project['project_number']}")

            # Fetch and display aggregate statistics based on partner type
            project_stats = get_project_statistics(db_manager, project['project_number'], partner_type_backend)
            contacted_count = project_stats.get('contacted_count', 0)
            response_count = project_stats.get('response_count', 0)

            stats_html = (
                f"{get_statistics_badge(f'{contacted_count} {partner_type_display} Contacted', '', 'info')} "
                f"{get_statistics_badge(f'{response_count} Responses Received', '', 'success')}"
            )
            st.markdown(stats_html, unsafe_allow_html=True)

            # Display last scanned date
            if 'last_scanned' in project and project['last_scanned']:
                formatted_date = format_timestamp(project['last_scanned'])
                st.caption(f"📅 Last Scanned: {formatted_date}")

            st.divider()

            # Fetch supplier data for the project (filtered by partner type)
            with st.spinner("Loading supplier data..."):
                supplier_data_filtered = fetch_suppliers_by_partner_type(
                    db_manager,
                    project['project_number'],
                    partner_type_backend
                )

            # Get full supplier data with submissions for filtered suppliers
            supplier_data = []
            for supplier_info in supplier_data_filtered:
                supplier_name = supplier_info['supplier_name']
                # Fetch submissions for this supplier
                submissions = list(db_manager.db.submissions.find({
                    "project_number": project['project_number'],
                    "supplier_name": supplier_name
                }).sort("date", -1))

                transmissions = [s for s in submissions if s.get('type') == 'sent']
                receipts = [s for s in submissions if s.get('type') == 'received']

                supplier_data.append({
                    'supplier': supplier_info,
                    'transmissions': transmissions,
                    'receipts': receipts
                })

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

                    # Simplified Header: Supplier Name Only (project number removed - now in persistent header)
                    st.markdown(f"### {supplier['supplier_name']}")

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

                                            # Single-line header: folder name (left) + stats (right)
                                            col_folder, col_stats = st.columns([3, 2])
                                            with col_folder:
                                                st.markdown(f'<strong>📂 {folder_name}</strong>', unsafe_allow_html=True)
                                            with col_stats:
                                                st.markdown(f'<div style="text-align: right;">{folder_stats_html}</div>', unsafe_allow_html=True)

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

                                        # Single-line header: folder name (left) + stats (right)
                                        col_folder, col_stats = st.columns([3, 2])
                                        with col_folder:
                                            st.markdown(f'<strong>📂 {folder_name}</strong>', unsafe_allow_html=True)
                                        with col_stats:
                                            st.markdown(f'<div style="text-align: right;">{folder_stats_html}</div>', unsafe_allow_html=True)

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
