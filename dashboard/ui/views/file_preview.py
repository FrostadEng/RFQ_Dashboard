"""
File preview view for the RFQ Dashboard.
"""
import base64
import logging
from pathlib import Path
import streamlit as st

from dashboard.styles import format_file_size
from dashboard.ui.components.file_widgets import create_download_button

logger = logging.getLogger(__name__)

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