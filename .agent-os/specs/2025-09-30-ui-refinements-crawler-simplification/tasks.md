# Spec Tasks

These are the tasks to be completed for the spec detailed in @.agent-os/specs/2025-09-30-ui-refinements-crawler-simplification/spec.md

> Created: 2025-09-30
> Status: ✅ Completed

## Tasks

- [x] 1. Configure dark mode as default theme
  - [x] 1.1 Update .streamlit/config.toml with dark theme settings
  - [x] 1.2 Set base = "dark" in theme configuration
  - [x] 1.3 Adjust backgroundColor, secondaryBackgroundColor, and textColor for dark mode
  - [x] 1.4 Test dashboard loads in dark mode by default

- [x] 2. Make project number clickable to open folder
  - [x] 2.1 Update streamlit_dashboard.py to use create_file_link() for project number
  - [x] 2.2 Replace st.subheader with markdown header containing clickable link
  - [x] 2.3 Remove info banner displaying project path
  - [x] 2.4 Test clicking project number opens file explorer to project folder

- [x] 3. Update mock_projects structure to folder-based format
  - [x] 3.1 Delete all ZIP files from mock_projects/*/RFQ/*/Sent/ directories
  - [x] 3.2 Rename/restructure existing source folders in Sent directories
  - [x] 3.3 Create second folder in each Sent directory (2+ folders per supplier)
  - [x] 3.4 Add sample files to demonstrate structure with nested folders
  - [x] 3.5 Verify mock_projects follows new structure: Sent and Received both contain folders only

- [x] 4. Refactor crawler logic to unified submission processing
  - [x] 4.1 Create process_submission_folder() method to handle both Sent and Received
  - [x] 4.2 Add "type" field to submission dictionaries ("sent" or "received")
  - [x] 4.3 Update process_supplier_folder() to return single "submissions" list
  - [x] 4.4 Delete process_sent_folder() method (old ZIP logic)
  - [x] 4.5 Delete process_received_folder() method (replace with unified method)
  - [x] 4.6 Test crawler processes both Sent and Received folders identically

- [x] 5. Update MongoDB schema and db_manager
  - [x] 5.1 Update db_manager.py _ensure_indexes() to create submissions collection indexes
  - [x] 5.2 Create compound index: [("project_number", 1), ("supplier_name", 1), ("type", 1)]
  - [x] 5.3 Create unique index on "folder_path"
  - [x] 5.4 Update save_project_data() to save to submissions collection
  - [x] 5.5 Remove separate transmissions/receipts collection logic
  - [x] 5.6 Drop old transmissions and receipts collections (manual or via script)

- [x] 6. Update Streamlit dashboard to use unified submissions
  - [x] 6.1 Update fetch_supplier_data() to query submissions collection
  - [x] 6.2 Filter submissions by type: {type: "sent"} and {type: "received"}
  - [x] 6.3 Create render_submissions() helper function for both columns
  - [x] 6.4 Remove ZIP-specific rendering logic from sent column
  - [x] 6.5 Update both columns to use identical folder tree rendering
  - [x] 6.6 Verify both sent and received display with same structure

- [x] 7. Test complete workflow and verify functionality
  - [x] 7.1 Run crawler on updated mock_projects structure
  - [x] 7.2 Verify MongoDB submissions collection has correct data with type field
  - [x] 7.3 Verify dashboard displays dark mode by default
  - [x] 7.4 Test project number link opens correct folder
  - [x] 7.5 Verify both sent and received columns display multiple folders per supplier
  - [x] 7.6 Test file access (open + download) works for both sent and received
  - [x] 7.7 Verify folder trees render correctly for deeply nested structures
  - [x] 7.8 Check pagination works if any supplier has 100+ files
