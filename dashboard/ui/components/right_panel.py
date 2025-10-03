"""
UI component for the right panel of the dashboard.
"""
import streamlit as st

from rfq_tracker.db_manager import DBManager
from dashboard.data.queries import fetch_supplier_data


def render_right_panel(right_col, db_manager: DBManager):
    """
    Renders the right panel with the supplier selection list.

    Args:
        right_col: The Streamlit column to render into.
        db_manager: The database manager instance.
    """
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