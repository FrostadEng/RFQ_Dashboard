"""
Right panel component for RFQ Dashboard.
Contains supplier selection list.
"""

import streamlit as st

from rfq_tracker.db_manager import DBManager
from dashboard.data.queries import (
    fetch_suppliers_by_partner_type,
    get_partner_statistics
)


def render_right_panel(right_col, db_manager: DBManager):
    """
    Render right panel with supplier selection.

    Args:
        right_col: Streamlit column object
        db_manager: Database manager instance
    """
    with right_col:
        if st.session_state.selected_project:
            # Get partner type from session state
            partner_type_display = st.session_state.get('partner_type', 'Suppliers')
            partner_type_backend = 'Supplier' if partner_type_display == 'Suppliers' else 'Contractor'

            # Display header with current partner type
            st.markdown(f"### 🏢 {partner_type_display}")

            # Fetch supplier data filtered by partner type
            with st.spinner("Loading..."):
                suppliers = fetch_suppliers_by_partner_type(
                    db_manager,
                    st.session_state.selected_project['project_number'],
                    partner_type_backend
                )

                # Get partner statistics for inline counts
                partner_stats = get_partner_statistics(
                    db_manager,
                    st.session_state.selected_project['project_number'],
                    partner_type_backend
                )

            if suppliers:
                # Create a dictionary for quick stats lookup
                stats_dict = {
                    stat['supplier_name']: stat
                    for stat in partner_stats
                }

                # Create formatted radio options with inline sent/received counts
                supplier_options = []
                supplier_names = []
                for supplier in suppliers:
                    name = supplier['supplier_name']
                    supplier_names.append(name)

                    # Get stats for this supplier
                    stats = stats_dict.get(name, {'sent_count': 0, 'received_count': 0})
                    sent_count = stats['sent_count']
                    received_count = stats['received_count']

                    # Format: SupplierName [Sent: X, Received: Y]
                    formatted_option = f"{name} [Sent: {sent_count}, Received: {received_count}]"
                    supplier_options.append(formatted_option)

                # Find index of currently selected supplier
                try:
                    default_index = supplier_names.index(st.session_state.selected_supplier)
                except (ValueError, AttributeError):
                    default_index = 0

                # Display radio buttons with formatted options
                selected_option = st.radio(
                    "Select Partner",
                    supplier_options,
                    index=default_index,
                    label_visibility="collapsed",
                    key="supplier_radio"
                )

                # Extract supplier name from selected option
                selected_supplier_name = supplier_names[supplier_options.index(selected_option)]

                # Update session state if selection changed
                if selected_supplier_name != st.session_state.selected_supplier:
                    st.session_state.selected_supplier = selected_supplier_name
                    st.rerun()
            else:
                st.caption(f"_No {partner_type_display.lower()} found_")
        else:
            st.markdown(
                """
                <div style='text-align: center; padding-top: 50px;'>
                    <p style='color: #9CA3AF;'>Select a project to view suppliers</p>
                </div>
                """,
                unsafe_allow_html=True
            )
