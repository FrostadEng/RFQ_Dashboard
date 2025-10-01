# Spec Tasks

These are the tasks to be completed for the spec detailed in @.agent-os/specs/2025-09-30-streamlit-project-list/spec.md

> Created: 2025-09-30
> Status: ✅ Completed

## Tasks

- [x] 1. Set up Streamlit application structure and dependencies
  - [x] 1.1 Update requirements.txt with streamlit>=1.28 and python-dotenv>=1.0
  - [x] 1.2 Create streamlit_dashboard.py entry point file
  - [x] 1.3 Create .streamlit/config.toml with network configuration (server.address=0.0.0.0)
  - [x] 1.4 Add environment variable support for MongoDB connection (MONGO_URI fallback)
  - [x] 1.5 Test that Streamlit starts and is accessible on local network (0.0.0.0:8501)

- [x] 2. Implement MongoDB integration and data loading
  - [x] 2.1 Import and configure DBManager from rfq_tracker/db_manager.py
  - [x] 2.2 Implement cached database query function using @st.cache_data (5-minute TTL)
  - [x] 2.3 Add error handling for database connection failures with retry button
  - [x] 2.4 Add empty project list handling with informative message
  - [x] 2.5 Verify projects load correctly from MongoDB and cache properly

- [x] 3. Build sidebar project list with search and sort
  - [x] 3.1 Create st.sidebar layout with search text input (placeholder: "Search Project Number...")
  - [x] 3.2 Implement case-insensitive search filter on project_number field
  - [x] 3.3 Add sort selectbox with 4 options (number asc/desc, last scanned newest/oldest)
  - [x] 3.4 Implement sort logic for project_number and last_scanned fields
  - [x] 3.5 Display filtered project count (e.g., "Showing X of Y projects")
  - [x] 3.6 Test search filters instantly and sort reorders correctly

- [x] 4. Implement project selection and state management
  - [x] 4.1 Create st.radio widget for project list display (format: "Project {number}")
  - [x] 4.2 Initialize st.session_state.selected_project for tracking selection
  - [x] 4.3 Store full project data (project_number, path, last_scanned) in session state on selection
  - [x] 4.4 Verify selection persists across sidebar interactions (search, sort)

- [x] 5. Create placeholder content area and documentation
  - [x] 5.1 Add default message "👈 Select a project from the sidebar to see details."
  - [x] 5.2 Display selected project details (number, path, last_scanned) when project is selected
  - [x] 5.3 Add note "(Supplier detail view coming in next spec.)"
  - [x] 5.4 Update README.md with local network deployment instructions (find IP, firewall setup, team access URL)
  - [x] 5.5 Test complete workflow: start app, access from another computer on network, search, sort, select project

## Implementation Summary

**Completed:** 2025-09-30

**Files Created:**
- `streamlit_dashboard.py` - Main Streamlit application (237 lines)
- `.streamlit/config.toml` - Network configuration for 0.0.0.0 binding

**Files Modified:**
- `requirements.txt` - Added streamlit>=1.28, python-dotenv>=1.0
- `README.md` - Added comprehensive network deployment guide

**Testing Results:**
- ✅ Dashboard accessible on local PC at http://localhost:8501
- ✅ Project list displays correctly from MongoDB
- ✅ Search functionality works (case-insensitive filtering)
- ✅ Sort functionality works (4 options)
- ✅ Project selection and state management working
- ✅ Placeholder content area displays correctly
- ⏳ Network access from other computers - awaiting team testing

**Next Steps:**
- Create Spec 1.2: Streamlit Supplier Detail View to display sent/received files and complete the migration
