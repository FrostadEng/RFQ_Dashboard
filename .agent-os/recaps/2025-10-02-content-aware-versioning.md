# [2025-10-02] Recap: Content-Aware Versioning

This recaps the content-aware versioning system implemented to prevent duplicate submission records.

## Recap

Implemented a content-aware versioning system that only creates new submission versions when folder contents actually change. The system uses SHA-256 hashing to detect changes and displays version history in a compact timeline format.

Key features:
- SHA-256 content hashing for folders based on all file paths and contents
- Database logic to compare hashes before inserting (skips if unchanged)
- Multi-version UI display with timestamp history and collapsible folder structures
- Verified no duplicates created on re-scans of unchanged folders

## Context

Previously, the system created a new submission record on every crawl, regardless of whether folder contents changed. This caused meaningless duplicate versions and wasted database storage. The goal was to implement content-aware versioning where new versions are only recorded if folder contents actually differ, using content hashing to detect changes.

## Implementation Details

### 1. Crawler (rfq_tracker/crawler.py)

Added `compute_content_hash()` method that generates SHA-256 hash of all files in a folder based on sorted file paths and their individual hashes. This ensures consistent hash generation regardless of file system ordering.

Updated `process_submission_folder()` to include `content_hash` in submission data, enabling the database to detect content changes.

### 2. Database (rfq_tracker/db_manager.py)

Replaced the simple `folder_path` unique index with a compound index on `(project_number, supplier_name, folder_name, content_hash)`. This allows multiple versions of the same folder to coexist when content differs.

Modified `save_project_data()` to check if a submission with the same content hash already exists:
- If content hash is found: Only updates the `last_checked` timestamp
- If content hash is new: Inserts as a new version

### 3. UI (streamlit_dashboard.py)

Updated `group_events_by_folder_name()` to group submissions by exact folder name and sort versions chronologically by date.

Implemented compact multi-version display showing:
- Version number for each iteration
- Timestamp of when the version was detected
- File count in that version
- Collapsible folder structure for each version's files

## Testing Results

- First crawl successfully populated database with content hashes for all submissions
- Second crawl with unchanged content created no duplicates, only updated `last_checked` timestamps
- Database verification confirmed no duplicate submissions exist
- UI correctly displays multiple versions when content changes occur

## Files Modified

- `/home/frostadeng/vector/projects/RFQ_Dashboard/rfq_tracker/crawler.py`
- `/home/frostadeng/vector/projects/RFQ_Dashboard/rfq_tracker/db_manager.py`
- `/home/frostadeng/vector/projects/RFQ_Dashboard/streamlit_dashboard.py`
