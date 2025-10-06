# Technical Specification

This is the technical specification for the spec detailed in @.agent-os/specs/2025-10-02-dashboard-refactoring/spec.md

## Technical Requirements

### Directory Structure

Create the following directory hierarchy:

```
.
├── app.py                      # New main entry point (~100-150 lines)
├── dashboard/                  # New main source directory
│   ├── __init__.py
│   ├── config.py              # Configuration loading (load_config function)
│   ├── styles.py              # Existing styles module (move if not already here)
│   ├── ui/                    # All UI-related components and views
│   │   ├── __init__.py
│   │   ├── components/        # Reusable UI parts
│   │   │   ├── __init__.py
│   │   │   ├── left_panel.py   # render_left_panel(left_col, db_manager, all_projects, all_suppliers)
│   │   │   ├── center_panel.py # render_center_panel(center_col, db_manager)
│   │   │   ├── right_panel.py  # render_right_panel(right_col, db_manager)
│   │   │   └── file_widgets.py # create_download_button, create_preview_button, render_folder_tree
│   │   └── views/             # Full-page UI states
│   │       ├── __init__.py
│   │       └── file_preview.py # render_file_preview()
│   ├── data/                  # Database interaction logic
│   │   ├── __init__.py
│   │   └── queries.py         # fetch_all_suppliers, fetch_projects, fetch_supplier_data
│   ├── logic/                 # Business logic and data processing
│   │   ├── __init__.py
│   │   └── processing.py      # filter_projects, sort_projects, calculate_*_statistics, etc.
│   └── utils/                 # Helper/utility functions
│       ├── __init__.py
│       └── helpers.py         # format_timestamp, create_file_link, run_*_crawler functions
└── streamlit_dashboard.py     # Original file (can be archived after verification)
```

### Module Responsibilities

#### app.py (Main Entry Point)
- Set Streamlit page config and inject CSS
- Initialize DBManager and load configuration
- Initialize session state variables
- Handle startup crawler logic
- Check if in file preview mode and route accordingly
- Define three-column layout
- Call render functions for left_panel, center_panel, right_panel
- **No business logic or UI rendering code** - purely orchestration

#### dashboard/config.py
- `load_config()` - Load configuration from config.json and environment variables

#### dashboard/data/queries.py
- `fetch_all_suppliers(db_manager)` - With @st.cache_data decorator
- `fetch_projects(db_manager)` - With @st.cache_data decorator
- `fetch_supplier_data(db_manager, project_number)` - With @st.cache_data decorator
- `initialize_db_manager()` - Database connection initialization with error handling

#### dashboard/logic/processing.py
- `filter_projects(projects, search_term, selected_suppliers, date_range_start, date_range_end, db_manager)`
- `sort_projects(projects, sort_option)`
- `calculate_folder_statistics(files)`
- `calculate_supplier_statistics(transmissions, receipts)`
- `group_events_by_folder_name(events)`
- `build_folder_tree(file_paths, base_path)`

#### dashboard/utils/helpers.py
- `format_timestamp(timestamp_str)`
- `create_file_link(file_path, link_text)`
- `run_startup_crawler()`
- `run_manual_refresh()`

#### dashboard/ui/views/file_preview.py
- `render_file_preview()` - Full-page file preview with back button

#### dashboard/ui/components/file_widgets.py
- `create_download_button(file_path, button_label, key_suffix)`
- `create_preview_button(file_path, key_suffix)`
- `render_folder_tree(tree, indent_level, key_prefix)`

#### dashboard/ui/components/left_panel.py
- `render_left_panel(left_col, db_manager, all_projects, all_suppliers)` - Contains:
  - Manual refresh button logic
  - Collapsible filters section
  - Search input, supplier multiselect, date range inputs
  - Clear filters button
  - Sort options selectbox
  - Pagination setup and controls
  - Project selection radio buttons
  - Updates st.session_state for selected_project

#### dashboard/ui/components/center_panel.py
- `render_center_panel(center_col, db_manager)` - Contains:
  - Check for preview mode (early return)
  - Project header and metadata display
  - Supplier statistics badges
  - Two-column layout for sent/received
  - Versioned transmission and receipt cards
  - Folder tree rendering for each event
  - Default "select a project" message

#### dashboard/ui/components/right_panel.py
- `render_right_panel(right_col, db_manager)` - Contains:
  - Suppliers header
  - Supplier radio button selection
  - Updates st.session_state for selected_supplier
  - Default "select a project" message

### Import Structure

Each module should import only what it needs:

**app.py imports:**
```python
import streamlit as st
from dashboard.config import load_config
from dashboard.data.queries import initialize_db_manager, fetch_projects, fetch_all_suppliers
from dashboard.ui.views.file_preview import render_file_preview
from dashboard.ui.components.left_panel import render_left_panel
from dashboard.ui.components.center_panel import render_center_panel
from dashboard.ui.components.right_panel import render_right_panel
from dashboard.styles import get_custom_css
from dashboard.utils.helpers import run_startup_crawler
```

**dashboard/ui/components/left_panel.py imports:**
```python
import streamlit as st
from datetime import datetime
from dashboard.data.queries import fetch_projects, fetch_all_suppliers
from dashboard.logic.processing import filter_projects, sort_projects
from dashboard.utils.helpers import run_manual_refresh
```

(Similar patterns for other modules - import only what's needed)

### Session State Management

All session state initialization remains in app.py:
- `selected_project`, `data_refreshed`, `last_refresh_time`
- `current_page`, `search_term`, `sort_option`
- `selected_suppliers`, `date_range_start`, `date_range_end`
- `preview_file`, `selected_supplier`

Panel components read and write to `st.session_state` as needed.

### Function Signature Changes

When moving functions to panel components, their signatures will change:

**Before (in main()):**
```python
with left_col:
    # Direct access to variables
    if st.button("🔄 Refresh Data"):
        # ...
```

**After (in render_left_panel()):**
```python
def render_left_panel(left_col, db_manager, all_projects, all_suppliers):
    with left_col:
        if st.button("🔄 Refresh Data"):
            # ...
```

Similarly for center_panel and right_panel - they receive their column and necessary data as parameters.

### CSS and Styling

- Existing dashboard/styles.py remains unchanged
- CSS injection stays in app.py before any rendering

### Logging Configuration

- Logging setup (basicConfig, logger initialization) moves to app.py
- Each module can create its own logger: `logger = logging.getLogger(__name__)`

### Environment Variables

- `load_dotenv()` call remains in app.py (or config.py)
- Configuration loading happens early in app.py

## Migration Strategy

1. Create new directory structure and empty files first
2. Move pure utility functions (no dependencies on Streamlit or other modules) first
3. Move data/database functions (have external dependencies but no internal cross-dependencies)
4. Move business logic functions (may depend on utils but not UI)
5. Extract UI components (depend on logic, data, and utils)
6. Build new app.py orchestrating everything
7. Test thoroughly comparing behavior against original
8. Archive streamlit_dashboard.py once verified

## Testing Approach

Since automated tests are out of scope, manual testing checklist:

- [ ] Dashboard launches with `streamlit run app.py`
- [ ] Initial startup crawler runs when database is empty
- [ ] Project list displays and pagination works
- [ ] Search filter works correctly
- [ ] Supplier filter works correctly
- [ ] Date range filter works correctly
- [ ] Sort options work correctly
- [ ] Clear filters button works
- [ ] Project selection updates center panel
- [ ] Supplier selection updates center panel
- [ ] Sent transmissions display correctly with versioning
- [ ] Received submissions display correctly with versioning
- [ ] Folder tree rendering works
- [ ] File preview button opens preview mode
- [ ] Download buttons work
- [ ] Back button from preview returns to dashboard
- [ ] Manual refresh button works
- [ ] Session state persists correctly across interactions
