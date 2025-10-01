# Technical Specification

This is the technical specification for the spec detailed in @.agent-os/specs/2025-09-30-ui-refinements-crawler-simplification/spec.md

## Technical Requirements

### 1. Dark Mode Configuration

**File:** `.streamlit/config.toml`

**Changes:**
```toml
[theme]
primaryColor = "#3498db"
backgroundColor = "#0e1117"           # Dark background
secondaryBackgroundColor = "#262730"  # Slightly lighter dark
textColor = "#fafafa"                 # Light text
base = "dark"                         # Set dark as base theme
```

**Implementation:**
- Update existing `.streamlit/config.toml` theme section
- Set `base = "dark"` to make dark mode default
- Adjust colors for better dark mode contrast

---

### 2. Clickable Project Number

**Current Implementation (streamlit_dashboard.py lines 419-428):**
```python
st.subheader(f"Project {project['project_number']}")
# ... metrics ...
st.info("**Path:** " + project.get('path', 'N/A'))
```

**New Implementation:**
```python
# Make project number clickable to open folder
project_path = project.get('path', '')
project_link = create_file_link(project_path, f"Project {project['project_number']}")
st.markdown(f"## {project_link}")

# Remove the info banner with path
# (Delete lines showing path info)
```

**Technical Details:**
- Reuse existing `create_file_link()` function
- Pass project folder path (not individual file)
- Opens folder in file explorer when clicked
- Remove redundant path display

---

### 3. Simplified Crawler Logic

**Current Files:**
- `rfq_tracker/crawler.py` - Lines 73-98 (process_sent_folder)
- `rfq_tracker/crawler.py` - Lines 100-120 (process_received_folder)

**Refactoring Strategy:**

**New Unified Function:**
```python
def process_submission_folder(self, folder_path: Path, project_number: str,
                              supplier_name: str, folder_type: str) -> List[Dict[str, Any]]:
    """
    Process a submission folder (Sent or Received) to extract metadata.

    Args:
        folder_path: Path to Sent or Received folder
        project_number: Project number
        supplier_name: Supplier name
        folder_type: "sent" or "received"

    Returns:
        List of submission dictionaries
    """
    submissions = []

    if not folder_path.exists():
        return submissions

    # Iterate through submission folders
    for submission_folder in folder_path.iterdir():
        if submission_folder.is_dir():
            # Skip filtered folders
            if self.should_skip_folder(submission_folder.name):
                continue

            submission = {
                "project_number": project_number,
                "supplier_name": supplier_name,
                "type": folder_type,  # "sent" or "received"
                "folder_name": submission_folder.name,
                "folder_path": str(submission_folder),
                "date": self.get_file_creation_time(submission_folder),
                "files": [
                    str(f) for f in submission_folder.rglob("*")
                    if f.is_file() and not self.should_skip_file(f.name)
                ]
            }

            submissions.append(submission)
            logger.debug(f"Found {len(submission['files'])} files in {folder_type} folder {submission_folder.name}")

    logger.info(f"Found {len(submissions)} {folder_type} submissions in {folder_path}")
    return submissions
```

**Updated process_supplier_folder:**
```python
def process_supplier_folder(self, supplier_folder: Path, project_number: str) -> Dict[str, Any]:
    """Process a single supplier folder."""
    supplier_name = supplier_folder.name
    logger.info(f"Processing supplier: {supplier_name} in project {project_number}")

    supplier_doc = {
        "project_number": project_number,
        "supplier_name": supplier_name,
        "path": str(supplier_folder)
    }

    # Process Sent and Received folders identically
    sent_submissions = self.process_submission_folder(
        supplier_folder / "Sent", project_number, supplier_name, "sent"
    )

    received_submissions = self.process_submission_folder(
        supplier_folder / "Received", project_number, supplier_name, "received"
    )

    # Combine into single submissions list
    all_submissions = sent_submissions + received_submissions

    return {
        "supplier": supplier_doc,
        "submissions": all_submissions  # Single list instead of separate transmissions/receipts
    }
```

**Code Removal:**
- Delete `process_sent_folder()` method (lines 73-98)
- Delete `process_received_folder()` method (lines 100-120)
- Replace with single `process_submission_folder()` method

---

### 4. Update Mock Projects

**Current Structure:**
```
mock_projects/12345/RFQ/SupplierA/
  ├─ Sent/
  │   ├─ transmission1.zip
  │   ├─ transmission1/ (source folder)
  │   ├─ transmission2.zip
  │   └─ transmission2/ (source folder)
  └─ Received/
      └─ response1/
```

**New Structure:**
```
mock_projects/12345/RFQ/SupplierA/
  ├─ Sent/
  │   ├─ 2024-01-15-Initial-RFQ/
  │   │   ├─ RFQ-Package.pdf
  │   │   ├─ Specifications.docx
  │   │   └─ Drawings/
  │   │       └─ Assembly-A.pdf
  │   └─ 2024-02-20-Revised-RFQ/
  │       ├─ Revised-Specs.docx
  │       └─ Updated-Drawings/
  │           └─ Assembly-A-Rev2.pdf
  └─ Received/
      ├─ 2024-03-01-Initial-Response/
      │   ├─ Quote.pdf
      │   └─ Technical-Proposal.docx
      └─ 2024-03-15-Revised-Quote/
          ├─ Revised-Quote.pdf
          └─ Clarifications.pdf
```

**Implementation Steps:**
1. Delete all `.zip` files from `mock_projects/*/RFQ/*/Sent/`
2. Rename/restructure source folders to standalone submission folders
3. Create second folder in each Sent directory
4. Add sample files to demonstrate structure

---

### 5. MongoDB Schema Updates

**Current Collections:**
- `transmissions` - Sent data (ZIP-based)
- `receipts` - Received data (folder-based)

**New Unified `submissions` Collection:**

Merge both collections into a single `submissions` collection with a `type` field:

```javascript
{
  project_number: "12345",
  supplier_name: "SupplierA",
  type: "sent",                           // NEW: "sent" or "received"
  folder_name: "2024-01-15-Initial-RFQ",
  folder_path: "/path/to/Sent/2024-01-15-Initial-RFQ",
  date: "2024-01-15T10:00:00Z",
  files: [
    "/path/to/Sent/2024-01-15-Initial-RFQ/RFQ-Package.pdf",
    "/path/to/Sent/2024-01-15-Initial-RFQ/Specifications.docx",
    ...
  ]
}
```

**Schema Benefits:**
- Single collection instead of two
- Identical structure for sent and received
- Type field enables filtering: `{type: "sent"}` or `{type: "received"}`
- Simpler queries and maintenance

**Database Migration:**
- Drop old `transmissions` and `receipts` collections
- Create new `submissions` collection
- Update indexes:
  - Create compound index: `[("project_number", 1), ("supplier_name", 1), ("type", 1)]`
  - Create unique index: `"folder_path"` (ensures no duplicates)

**db_manager.py Changes:**
- Update `_ensure_indexes()` to create submissions indexes
- Update `save_project_data()` to save to `submissions` collection instead of separate collections
- Remove separate transmissions/receipts logic

---

### 6. Dashboard Display Updates

**Current Implementation (streamlit_dashboard.py lines 447-499):**
- Different rendering for transmissions (ZIP-focused) vs receipts (folder-focused)
- Lines 454-499: ZIP name, ZIP download, source files expander

**New Implementation:**
Both columns use identical rendering logic:

```python
# Helper function for rendering submissions (works for both sent/received)
def render_submissions(submissions: List[Dict], submission_type: str, supplier_name: str):
    """Render submission folders (sent or received) with identical logic."""
    if not submissions:
        st.caption(f"_No {submission_type} submissions found_")
        return

    for idx, submission in enumerate(submissions):
        folder_name = submission['folder_name']
        st.markdown(f"**📂 {folder_name}**")

        # Display metadata
        date = format_timestamp(submission.get('date', 'N/A'))
        st.caption(f"📅 Date: {date}")

        files = submission.get('files', [])
        st.caption(f"📁 Files: {len(files)} total")

        # Build and render folder tree (same as receipts currently)
        if files:
            # Pagination for large file lists
            if len(files) > 100:
                # ... pagination logic ...
                files_to_display = files[start_idx:end_idx]
            else:
                files_to_display = files

            # Build folder tree
            try:
                tree = build_folder_tree(files_to_display, submission['folder_path'])

                with st.expander("📁 Folder Structure", expanded=True):
                    render_folder_tree(
                        tree,
                        key_prefix=f"tree_{submission_type}_{supplier_name}_{idx}"
                    )
            except Exception as e:
                logger.error(f"Error rendering folder tree: {e}")
                st.error(f"Error displaying folder structure: {str(e)[:100]}")

                # Fallback: flat file list
                # ... same as current receipts fallback ...

        st.divider()
```

**Usage in main content:**
```python
# Left column: Sent Transmissions
with col_sent:
    st.subheader("📤 Sent Transmissions")
    render_submissions(transmissions, "sent", supplier['supplier_name'])

# Right column: Received Submissions
with col_received:
    st.subheader("📥 Received Submissions")
    render_submissions(receipts, "received", supplier['supplier_name'])
```

**Code Removal:**
- Delete ZIP-specific rendering logic (lines 454-499)
- Extract receipt rendering into reusable `render_submissions()` function
- Use same function for both columns

---

### 7. Testing Requirements

**Unit Tests (Manual):**
1. Run crawler on updated mock_projects
2. Verify MongoDB has correct structure for transmissions
3. Check dashboard displays both columns identically
4. Test file access (open + download) for sent folders
5. Verify pagination works for sent folders with 100+ files
6. Test dark mode appearance
7. Test clickable project number opens correct folder

**Edge Cases:**
- Empty Sent folder (0 submissions)
- Empty Received folder (0 submissions)
- Supplier with only Sent or only Received folders
- Deeply nested folder structures in Sent folders
- Mixed old ZIP data + new folder data (should only show new after re-crawl)

**Validation Checklist:**
- [ ] Dark mode loads by default
- [ ] Project number link opens file explorer to project folder
- [ ] Crawler processes Sent folders without errors
- [ ] MongoDB transmissions collection matches receipts structure
- [ ] Dashboard shows multiple sent/received folders per supplier
- [ ] Both columns render identically with folder trees
- [ ] File access works for sent submission files
- [ ] No references to ZIP files remain in code or UI

---

## Implementation Notes

**Breaking Changes:**
- Existing MongoDB data will be incompatible (requires re-crawl)
- Old mock_projects structure will not work (requires update)

**Migration Path:**
1. Update mock_projects structure first
2. Update crawler.py code
3. Drop/clear MongoDB collections (or run crawler with `--drop-existing` flag if implemented)
4. Run crawler to populate with new structure
5. Update streamlit_dashboard.py display logic
6. Update .streamlit/config.toml for dark mode
7. Test complete workflow

**Code Organization:**
- Keep `transmissions` and `receipts` as separate collections (per user requirement)
- Unified processing logic simplifies maintenance
- Reduces code duplication significantly (estimate ~100 lines removed)

---

## External Dependencies

No new dependencies required. All changes use existing libraries.
