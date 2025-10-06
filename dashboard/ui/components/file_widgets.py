"""
File-related UI widgets for RFQ Dashboard.
"""

import logging
import streamlit as st
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)


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
