# Technical Specification

This is the technical specification for the spec detailed in @.agent-os/specs/2025-09-30-streamlit-project-list/spec.md

## Technical Requirements

### Streamlit Application Structure

- **Entry Point:** Create `streamlit_dashboard.py` as the main application entry point (parallel to existing `run_dashboard.py`)
- **Layout:** Use `st.sidebar` for project list, `st.container` for main content area
- **Session State:** Initialize `st.session_state.selected_project` to track user's current project selection
- **Page Config:** Set `layout="wide"` for better space utilization, set `page_title="RFQ Dashboard"`

### Network Configuration for Local Access

- **Server Address:** Configure Streamlit to bind to `0.0.0.0` (all network interfaces) instead of `localhost`
  - Command line: `streamlit run streamlit_dashboard.py --server.address=0.0.0.0`
  - Or via config: Create `.streamlit/config.toml` with `[server]` section and `address = "0.0.0.0"`
- **Port:** Use default port 8501 (configurable if needed)
- **Access URL:** Team members access via `http://<server-computer-ip>:8501` where server-computer-ip is the IP of the computer running the app
- **Documentation:** Add README section explaining how to find the server computer's IP address (Windows: `ipconfig`, Linux: `ip addr`)

### MongoDB Integration

- **Connection:** Reuse existing `DBManager` class from `rfq_tracker/db_manager.py`
- **Connection String:** Read from `config.json` (default: `mongodb://localhost:27017`)
- **Environment Variable Support:** Add fallback to `MONGO_URI` environment variable for Docker future-proofing
- **Query:** Fetch all projects using `db.projects.find().sort("project_number", -1)` as default
- **Caching:** Use `@st.cache_data` decorator to cache project list queries (TTL: 5 minutes, configurable)
- **Connection Pooling:** Leverage pymongo's built-in connection pooling for concurrent users

### Search/Filter Functionality

- **Input Widget:** `st.text_input` in sidebar with placeholder "Search Project Number..."
- **Filter Logic:** Case-insensitive substring matching against `project_number` field
- **Real-Time Update:** Filter updates on every keystroke (Streamlit's default behavior)
- **Performance:** Filter on cached data client-side (no re-query to database for each keystroke)
- **Clear Indication:** Show count of filtered results (e.g., "Showing 3 of 150 projects")

### Sort Functionality

- **Sort Widget:** `st.selectbox` with options:
  - "Project Number (Ascending)"
  - "Project Number (Descending)"
  - "Last Scanned (Newest First)"
  - "Last Scanned (Oldest First)"
- **Sort Logic:**
  - Project number: Sort alphabetically/numerically by `project_number` field
  - Last scanned: Sort by `last_scanned` timestamp field (ISO 8601 format)
  - Handle missing `last_scanned` field gracefully (treat as oldest date)
- **Default:** "Project Number (Descending)" to show newest projects first
- **Persistence:** Store sort preference in session state (resets on page reload)

### Project List Display

- **Widget:** Use `st.radio` for project selection (provides visual feedback and state management)
- **Format:** Display as "Project {project_number}"
- **Selection Behavior:**
  - Clicking a project stores full `project_data` dict in `st.session_state.selected_project`
  - Store project_number, path, and last_scanned fields
- **Visual Feedback:** Streamlit radio default highlighting for selected item
- **Scrolling:** Sidebar scrolls automatically for long project lists

### Placeholder Content Area

- **Default State:** Display centered message: "👈 Select a project from the sidebar to see details."
- **Selected State:** Display:
  - "**Project {project_number} selected**"
  - "Path: {project_path}"
  - "Last Scanned: {last_scanned}" (formatted as human-readable date)
  - "(Supplier detail view coming in next spec.)"
- **Layout:** Use `st.empty()` or conditional rendering to swap content based on selection state

### Error Handling

- **Database Connection Failure:**
  - Display `st.error()` message: "Failed to connect to MongoDB. Please check the database is running."
  - Provide troubleshooting hints (check config.json, verify MongoDB is running)
  - Add manual retry button using `st.button("Retry Connection")`
- **Empty Project List:**
  - Show `st.info()` message: "No projects found. Run `python run_crawler.py` to populate data."
- **Invalid Sort Field:** Gracefully handle missing `last_scanned` field (treat as oldest, add warning in logs)
- **Network Access Issues:** Add note in documentation about firewall rules if users can't access

### UI/UX Specifications

- **Theme:** Use Streamlit's default light theme initially (can be customized with `.streamlit/config.toml`)
- **Loading States:**
  - Show `st.spinner("Loading projects from database...")` during initial MongoDB query
  - Show count of loaded projects (e.g., "Loaded 150 projects")
- **Sidebar Width:** Default Streamlit sidebar width (approximately 300px, auto-responsive)
- **Typography:** Use Streamlit default fonts and sizing
- **Icons:** Use emoji for visual elements (📊 for dashboard, 🔍 for search, etc.)
- **Accessibility:** Rely on Streamlit's built-in ARIA labels and semantic HTML

### Performance Criteria

- **Initial Load:** Project list should load within 2 seconds for up to 1000 projects on local network
- **Search Response:** Filter should update within 100ms of keystroke (client-side filtering)
- **Sort Response:** Re-sort should complete within 500ms (in-memory operation)
- **Concurrent Users:** Support 5-10 simultaneous users on local network (typical team size)
- **Cache Invalidation:** Refresh cached data every 5 minutes to show new crawler results

### Configuration Management

- **Config File:** Continue using existing `config.json` for MongoDB connection
- **Streamlit Config:** Create `.streamlit/config.toml` with:
  ```toml
  [server]
  address = "0.0.0.0"
  port = 8501

  [theme]
  primaryColor = "#3498db"
  backgroundColor = "#ffffff"
  secondaryBackgroundColor = "#f0f2f6"
  ```
- **Environment Variables:** Support `MONGO_URI` and `MONGO_DB` env vars for Docker compatibility

### Deployment Instructions

- **Local Network Setup:**
  1. Start MongoDB on server computer
  2. Run crawler to populate data: `python run_crawler.py`
  3. Start Streamlit: `streamlit run streamlit_dashboard.py --server.address=0.0.0.0`
  4. Find server IP: `ipconfig` (Windows) or `ip addr` (Linux)
  5. Share URL with team: `http://<server-ip>:8501`
- **Firewall Configuration:**
  - Ensure port 8501 is open on server computer firewall
  - Windows: Add inbound rule for port 8501
  - Linux: `sudo ufw allow 8501`

## External Dependencies

New dependencies required:

- **streamlit>=1.28** - Web application framework
  - **Justification:** Required for web-based UI to replace PyQt6 desktop application and enable browser access for team
  - **Version:** 1.28+ for latest session state improvements and performance optimizations

- **python-dotenv>=1.0** - Environment variable management
  - **Justification:** Enable `.env` file support for Docker deployment (Phase 1.2) and flexible configuration
  - **Version:** 1.0+ for stable API

Update `requirements.txt`:
```
pymongo[srv]>=4.0
streamlit>=1.28
python-dotenv>=1.0
PyQt6  # Keep for now, remove after full migration confirmed
```

**Note:** PyQt6 can be removed from requirements.txt once the Streamlit migration is complete and validated.
