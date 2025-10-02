# Technical Specification

This is the technical specification for the spec detailed in @.agent-os/specs/2025-10-01-ui-ux-folder-structure-redesign/spec.md

## Technical Requirements

### UI/UX Architecture

**Two-Panel Layout**
- Use Streamlit columns with custom CSS for fixed left panel (30% width) and scrollable right panel (70% width)
- Left panel: `st.container()` with fixed position containing refresh button, search input, filter controls, and pagination
- Right panel: `st.container()` with dynamic content based on selected project
- Implement responsive design ensuring panels stack on mobile devices (<768px)

**Left Panel Components**
- Manual refresh: `st.button("Refresh")` triggering `st.rerun()` and crawler execution
- Search bar: `st.text_input()` with debounced search (500ms) filtering projects by number or supplier name
- Filters: `st.multiselect()` for supplier names, `st.text_input()` for project number, `st.date_input()` for date range
- Pagination: Display 15 projects per page using `st.session_state` for current page, with Previous/Next buttons

**Right Panel Hierarchical Dropdowns**
- Use `st.expander()` for each supplier dropdown with custom styling for visual hierarchy
- Two-column layout within each supplier expander: Received (left) | Sent (right) using `st.columns(2)`
- Nested `st.expander()` for each date folder (e.g., "10.01.2025") under Received/Sent
- Display folder tree using recursive component showing file names, sizes, and icons
- Statistics display: Show badge-style counters above each dropdown level (e.g., "📄 15 files • 23.4 MB")

**File Preview Screen**
- Create new Streamlit page using `st.session_state` navigation state to track current view (list vs preview)
- Preview screen components:
  - Back button: `st.button("← Back to Folder")` updating session state to return to folder view
  - Download button: `st.download_button()` with file bytes and original filename
  - PDF viewer: Use `st.components.v1.iframe()` or `base64` encoding with HTML embed for in-browser preview
  - Support for PDF, images (PNG, JPG), and text files with appropriate renderers

### Crawler Updates

**Folder Structure Pattern**
- Update `crawler.py` path matching regex to recognize new pattern:
  - Old: `Projects/{project}/RFQ/{supplier}/{Received|Sent}/{date}`
  - New: `Projects/{project}/1-RFQ/Supplier RFQ Quotes/{supplier}/{Received|Sent}/{date}`
- Maintain backward compatibility by checking for both patterns (try new first, fall back to old)
- Update MongoDB schema to store folder structure version for future migration tracking

**Path Parsing Logic**
- Modify `extract_metadata()` function to handle "1-RFQ" prefix and "Supplier RFQ Quotes" intermediate layer
- Update path splitting logic: `parts = path.split(os.sep)` and identify markers ("1-RFQ", "Supplier RFQ Quotes")
- Ensure case-insensitive matching for "Received"/"Recieved" variations (note spelling inconsistency in real data)

### Mock Data Migration

**Directory Structure Update**
- Update `mock_projects/` to include new layers:
  ```
  mock_projects/
    ├── 24038/
    │   └── 1-RFQ/
    │       └── Supplier RFQ Quotes/
    │           ├── LEWA/
    │           │   ├── Received/
    │           │   │   └── 10.01.2025/
    │           │   └── Sent/
    │           └── SupplierB/
  ```
- Create migration script to reorganize existing mock data into new structure
- Update test fixtures to use new path patterns

### Statistics Calculation

**Aggregation Logic**
- Implement MongoDB aggregation pipeline to calculate statistics at each level:
  - Supplier level: Total files and size across all Received/Sent folders
  - Received/Sent level: Total files and size across all date folders
  - Date folder level: File count and total size for that specific folder
- Cache statistics in `st.session_state` to avoid recalculation on every interaction
- Update statistics on manual refresh or when crawler detects changes

**Display Format**
- File count: Format with commas for thousands (e.g., "1,234 files")
- File size: Use human-readable format (B, KB, MB, GB) with 1 decimal place (e.g., "23.4 MB")
- Additional stats: Latest file date, oldest file date, file type breakdown (e.g., "12 PDF, 3 ZIP")

### Performance Optimization

**Lazy Loading**
- Load supplier dropdowns on-demand: Only fetch folder data when supplier expander is opened
- Implement virtual scrolling for project list if performance degrades with large datasets
- Use `st.cache_data()` for expensive aggregation queries with 5-minute TTL

**Session State Management**
- Track expanded/collapsed state of each dropdown to maintain UI state across reruns
- Store current page, active filters, and search query in `st.session_state`
- Implement debouncing for search input to reduce unnecessary database queries

### Styling and User Experience

**Custom CSS**
- Add custom CSS via `st.markdown()` with `unsafe_allow_html=True` for:
  - Fixed left panel with `position: fixed` and scrollable right panel
  - Hover effects on dropdown headers and file items
  - Badge styling for statistics counters
  - Consistent spacing and typography
- Ensure accessibility: Proper ARIA labels, keyboard navigation support, color contrast compliance

**Loading States**
- Display `st.spinner()` during crawler execution, file preview loading, and statistics calculation
- Show placeholder skeletons for dropdowns while data is loading
- Implement error boundaries with user-friendly error messages for file preview failures

## External Dependencies

No new external dependencies required. All functionality can be implemented using existing Streamlit, pymongo, and Python standard library features. Custom CSS and HTML components will use Streamlit's built-in `st.markdown()` and `st.components.v1.html()` capabilities.
