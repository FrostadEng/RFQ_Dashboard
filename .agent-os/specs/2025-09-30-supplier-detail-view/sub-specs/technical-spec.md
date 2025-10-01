# Technical Specification

This is the technical specification for the spec detailed in @.agent-os/specs/2025-09-30-supplier-detail-view/spec.md

## Technical Requirements

### Database Queries for Supplier Data

**Supplier Query:**
- Query: `db.suppliers.find({"project_number": selected_project_number})`
- Sort: Alphabetically by `supplier_name`
- Cache: Use `@st.cache_data` with TTL=300 seconds (5 minutes)
- Input: `project_number` from `st.session_state.selected_project`

**Transmission Query:**
- Query: `db.transmissions.find({"project_number": project_number, "supplier_name": supplier_name})`
- Sort: By `sent_date` descending (newest first)
- Fields needed: `zip_name`, `zip_path`, `sent_date`, `source_files` (array)

**Receipt Query:**
- Query: `db.receipts.find({"project_number": project_number, "supplier_name": supplier_name})`
- Sort: By `received_date` descending (newest first)
- Fields needed: `received_folder_path`, `received_date`, `received_files` (array of file paths)

### Supplier Section Display

**Widget:** `st.expander` for each supplier
- Format: `"🏢 {supplier_name}"`
- Default state: First supplier expanded (`expanded=True` if index==0, else `expanded=False`)
- Layout: Use `st.columns(2)` inside each expander for sent/received split

**Empty State:**
- If no suppliers: Display `st.info("No suppliers found for this project. Run the crawler to scan for RFQ data.")`
- If supplier has no data: Display message within expander

### Two-Column Layout Implementation

**Structure:**
```python
col_sent, col_received = st.columns(2)

with col_sent:
    st.subheader("📤 Sent Transmissions")
    # Display transmission data

with col_received:
    st.subheader("📥 Received Submissions")
    # Display receipt data
```

**Column Widths:** Equal (1:1 ratio)

### Transmission Metadata Display

**Format for each transmission:**
```
📦 {zip_name}
├─ 📅 Sent: {formatted_sent_date}
├─ 📁 Source files: {count} files
└─ 🔗 [Open ZIP file]
```

**Date Formatting:**
- Convert ISO 8601 timestamps to human-readable format: `YYYY-MM-DD HH:MM:SS`
- Use existing `format_timestamp()` function from streamlit_dashboard.py

**Source Files Display:**
- Show count of files in `source_files` array
- Option to expand and show file list (use `st.expander` nested within transmission)
- Limit: Show first 20 files, add "... and X more" if count > 20

**File Links:**
- ZIP file: Link to `zip_path` using file access protocol
- Source files: Links to individual files from `source_files` array

### Receipt Metadata with Folder Structure

**Folder Structure Parsing:**
- Input: Array of absolute file paths from `received_files`
- Process: Parse paths to extract folder hierarchy
- Build tree structure programmatically from flat file list

**Tree Structure Algorithm:**
```python
def build_folder_tree(file_paths, base_path):
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
        relative_path = path.replace(base_path, '').lstrip('/')
        parts = relative_path.split('/')

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

    return tree
```

**Display Format:**
- Use indentation and icons to show hierarchy:
  ```
  📁 Drawings
    📁 Mechanical
      📄 Part-A.pdf [Open]
      📄 Part-B.pdf [Open]
    📁 Electrical
      📄 Schematic-1.pdf [Open]
  📁 Specifications
    📄 Spec-Sheet.docx [Open]
  ```

**Rendering:**
- Recursive function to render tree structure
- Use `st.markdown` with proper indentation (2 spaces per level)
- Icons: 📁 for folders, 📄 for files
- File links: `[Open]` clickable link next to file name

**Pagination:**
- If folder tree has > 50 files total, add `st.expander` to collapse/expand large folders
- Show folder summary: "📁 Drawings (15 files)" with expand option

### File Access Integration

**Opening Files in System Default Application:**

**Approach:** Use `file://` protocol links with platform-specific handling

**Implementation:**
```python
import platform
from pathlib import Path
from urllib.parse import quote

def create_file_link(file_path: str, link_text: str = "Open") -> str:
    """
    Create clickable link to open file in system default application.

    Args:
        file_path: Absolute path to file
        link_text: Display text for link

    Returns:
        Markdown link string
    """
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
```

**Browser Compatibility:**
- `file://` protocol works in most browsers when accessing local files
- May require browser permissions or settings adjustment
- Add note in documentation about browser configuration

**Download Button Implementation:**

In addition to `file://` links, provide download functionality using `st.download_button`:

```python
def create_download_button(file_path: str, button_label: str = "⬇️ Download"):
    """
    Create Streamlit download button for a file.

    Args:
        file_path: Absolute path to file
        button_label: Display text for button

    Returns:
        Streamlit download button
    """
    try:
        with open(file_path, 'rb') as f:
            file_data = f.read()

        file_name = Path(file_path).name

        return st.download_button(
            label=button_label,
            data=file_data,
            file_name=file_name,
            mime='application/octet-stream',  # Generic binary
            key=f"download_{file_path}"
        )
    except Exception as e:
        st.error(f"Error preparing download: {e}")
        return None
```

**Display Pattern:**
- Show both options side-by-side: `[Open] | [⬇️ Download]`
- Open link uses `file://` protocol
- Download button uses `st.download_button`

**Security Considerations:**
- Only allow access to files within configured `root_path`
- Validate file paths to prevent directory traversal attacks
- No file upload or modification through UI

### Pagination for Large File Lists

**Threshold:** Paginate if total files in a section > 100

**Implementation:**
```python
# For transmissions or receipts with many files
items_per_page = 50
total_items = len(items)
total_pages = (total_items + items_per_page - 1) // items_per_page

if total_pages > 1:
    page = st.number_input(
        f"Page ({total_pages} total)",
        min_value=1,
        max_value=total_pages,
        value=1,
        key=f"page_{supplier_name}_{section}"
    )
    start_idx = (page - 1) * items_per_page
    end_idx = start_idx + items_per_page
    items_to_display = items[start_idx:end_idx]
else:
    items_to_display = items
```

**UI Elements:**
- Page number input with current/total display
- Unique keys per supplier/section to maintain independent pagination
- Display "Showing X-Y of Z files"

### Empty State Handling

**No Suppliers:**
```python
if not suppliers:
    st.info("📭 No suppliers found for this project. Run `python run_crawler.py` to scan for RFQ data.")
    return
```

**No Transmissions for Supplier:**
```python
if not transmissions:
    st.caption("_No transmissions found_")
```

**No Receipts for Supplier:**
```python
if not receipts:
    st.caption("_No submissions received_")
```

**Missing Fields:**
- Handle missing `source_files`: Show "No source files listed"
- Handle missing `sent_date` or `received_date`: Show "Date not available"
- Gracefully handle corrupted data with try/except blocks

### UI/UX Specifications

**Visual Hierarchy:**
- Supplier names: Large, bold (via expander default)
- Section headers (Sent/Received): Subheader size with icons
- File/folder names: Regular text with appropriate icons
- Metadata: Smaller caption text

**Icons:**
- 🏢 Supplier
- 📤 Sent
- 📥 Received
- 📦 ZIP file
- 📁 Folder
- 📄 File
- 📅 Date
- 🔗 Link

**Spacing:**
- Add `st.divider()` between suppliers
- Use `st.caption()` for secondary information
- Proper indentation (2-4 spaces) for folder hierarchy

**Loading States:**
- Show `st.spinner("Loading supplier data...")` during database queries
- Cache results to minimize loading on re-renders

### Performance Optimization

**Caching Strategy:**
```python
@st.cache_data(ttl=300)
def fetch_supplier_data(_db_manager, project_number):
    """Fetch all supplier data for a project."""
    suppliers = list(_db_manager.db.suppliers.find({"project_number": project_number}))

    supplier_data = []
    for supplier in suppliers:
        transmissions = list(_db_manager.db.transmissions.find({
            "project_number": project_number,
            "supplier_name": supplier['supplier_name']
        }).sort("sent_date", -1))

        receipts = list(_db_manager.db.receipts.find({
            "project_number": project_number,
            "supplier_name": supplier['supplier_name']
        }).sort("received_date", -1))

        supplier_data.append({
            'supplier': supplier,
            'transmissions': transmissions,
            'receipts': receipts
        })

    return supplier_data
```

**Benefits:**
- Single cache key per project
- Reduces database queries on re-renders
- 5-minute TTL ensures reasonable freshness

**Lazy Loading:**
- Only render expanded supplier sections (Streamlit handles this via expander)
- Defer folder tree parsing until expander is opened (future optimization)

### Error Handling

**Database Errors:**
```python
try:
    supplier_data = fetch_supplier_data(db_manager, project_number)
except Exception as e:
    st.error(f"Error loading supplier data: {e}")
    logger.error(f"Supplier data fetch failed: {e}")
    return
```

**File Path Errors:**
- Validate paths exist before creating links
- Show warning icon (⚠️) if file path is invalid or file missing
- Log missing files for admin review

**Folder Tree Parsing Errors:**
- Catch exceptions in tree building
- Fall back to flat file list if tree parsing fails
- Log error and display user-friendly message

## External Dependencies

No new external dependencies required. All functionality can be implemented with existing libraries:
- `streamlit>=1.28` (already in requirements.txt)
- `pymongo[srv]>=4.0` (already in requirements.txt)
- Python standard library: `platform`, `pathlib`, `urllib.parse`

## Implementation Notes

**Integration with Existing Code:**
- Extend `streamlit_dashboard.py` main content area (currently shows placeholder)
- Reuse `DBManager` instance and caching patterns from Spec 1.1
- Reuse `format_timestamp()` function for date formatting

**Code Organization:**
- Keep all supplier display logic in `streamlit_dashboard.py` for now
- Consider refactoring to separate module if file grows > 500 lines
- Use helper functions for folder tree building and file link generation

**Testing Considerations:**
- Test with projects that have many suppliers (5+)
- Test with suppliers that have large file counts (100+)
- Test with deeply nested folder structures (5+ levels)
- Test on Windows and Linux (different file path formats)
- Verify file:// links work in Chrome, Firefox, Edge

**Browser File Access Limitations:**
- Modern browsers restrict `file://` protocol for security
- Document workaround: Add exception for localhost in browser settings
- Alternative: Implement server-side file serving endpoint (future enhancement)
