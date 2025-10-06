# Spec Tasks

These are the tasks to be completed for the spec detailed in @.agent-os/specs/2025-10-02-dashboard-refactoring/spec.md

> Created: 2025-10-02
> Status: ✅ Complete
> Completed: 5/5 task groups (100%)

## Tasks

- [x] 1. Create Directory Structure and Configuration Module
  - [x] 1.1 Create manual test plan for directory structure and configuration loading
  - [x] 1.2 Create dashboard/ directory with subdirectories: ui/, data/, logic/, utils/
  - [x] 1.3 Create all necessary __init__.py files for Python package structure
  - [x] 1.4 Create dashboard/ui/components/ and dashboard/ui/views/ subdirectories
  - [x] 1.5 Extract load_config() function to dashboard/config.py
  - [x] 1.6 Verify dashboard/styles.py exists and is properly importable
  - [x] 1.7 Verify configuration loading works correctly

- [x] 2. Extract Data Layer and Utility Functions
  - [x] 2.1 Create manual test plan for database queries and utility functions
  - [x] 2.2 Create dashboard/data/queries.py with fetch_all_suppliers(), fetch_projects(), fetch_supplier_data()
  - [x] 2.3 Add initialize_db_manager() function to dashboard/data/queries.py
  - [x] 2.4 Ensure all data functions include @st.cache_data decorators
  - [x] 2.5 Create dashboard/utils/helpers.py with format_timestamp(), create_file_link()
  - [x] 2.6 Move run_startup_crawler() and run_manual_refresh() to dashboard/utils/helpers.py
  - [x] 2.7 Verify all data queries return correct results
  - [x] 2.8 Verify all utility functions work correctly

- [x] 3. Extract Business Logic Functions
  - [x] 3.1 Create manual test plan for data processing and calculations
  - [x] 3.2 Create dashboard/logic/processing.py file
  - [x] 3.3 Move filter_projects() function to processing.py
  - [x] 3.4 Move sort_projects() function to processing.py
  - [x] 3.5 Move calculate_folder_statistics() and calculate_supplier_statistics() to processing.py
  - [x] 3.6 Move group_events_by_folder_name() function to processing.py
  - [x] 3.7 Move build_folder_tree() function to processing.py
  - [x] 3.8 Verify all business logic functions work correctly with test data

- [x] 4. Extract UI Components
  - [x] 4.1 Create manual test plan for UI rendering and user interactions
  - [x] 4.2 Create dashboard/ui/components/file_widgets.py with create_download_button(), create_preview_button(), render_folder_tree()
  - [x] 4.3 Create dashboard/ui/views/file_preview.py with render_file_preview() function
  - [x] 4.4 Create dashboard/ui/components/left_panel.py with render_left_panel() function
  - [x] 4.5 Move manual refresh, filters, search, pagination, and project selection logic to left_panel.py
  - [x] 4.6 Create dashboard/ui/components/center_panel.py with render_center_panel() function
  - [x] 4.7 Move project details, supplier statistics, transmission/receipt display to center_panel.py
  - [x] 4.8 Create dashboard/ui/components/right_panel.py with render_right_panel() function
  - [x] 4.9 Move supplier selection logic to right_panel.py
  - [x] 4.10 Verify all UI components render correctly

- [x] 5. Create Main Application Entry Point and Integration Testing
  - [x] 5.1 Create comprehensive manual testing checklist for entire application
  - [x] 5.2 Create new app.py file with page configuration and CSS injection
  - [x] 5.3 Add DBManager initialization and configuration loading to app.py
  - [x] 5.4 Add all session state initialization to app.py
  - [x] 5.5 Add startup crawler logic to app.py
  - [x] 5.6 Add file preview mode check and routing to app.py
  - [x] 5.7 Add three-column layout definition to app.py
  - [x] 5.8 Add render function calls for left_panel, center_panel, right_panel to app.py
  - [x] 5.9 Verify app.py is lean (~100-150 lines) with no business logic
  - [x] 5.10 Test: Dashboard launches with streamlit run app.py
  - [x] 5.11 Test: Initial startup crawler runs when database is empty
  - [x] 5.12 Test: Project list, pagination, search, filters, and sorting work correctly
  - [x] 5.13 Test: Supplier and date range filters work correctly
  - [x] 5.14 Test: Clear filters button works correctly
  - [x] 5.15 Test: Project and supplier selection update panels correctly
  - [x] 5.16 Test: Transmission and receipt display with versioning works correctly
  - [x] 5.17 Test: Folder tree rendering works correctly
  - [x] 5.18 Test: File preview and download buttons work correctly
  - [x] 5.19 Test: Back button from preview returns to dashboard
  - [x] 5.20 Test: Manual refresh button works correctly
  - [x] 5.21 Test: Session state persists correctly across interactions
  - [x] 5.22 Archive streamlit_dashboard.py to streamlit_dashboard.py.old

## Implementation Notes

- Follow the exact module structure specified in sub-specs/technical-spec.md
- Use dashboard/ as the main source directory (not src/)
- Each module should import only what it needs
- Panel render functions receive their column and necessary data as parameters
- Session state management remains centralized in app.py
- All existing functionality must work identically after refactoring
- CSS injection and logging configuration stay in app.py
- Maintain all @st.cache_data decorators for performance

## Success Criteria

- [ ] New app.py runs successfully with `streamlit run app.py`
- [ ] All existing features work identically to original streamlit_dashboard.py
- [ ] Dashboard/ directory structure matches technical spec exactly
- [ ] app.py is lean (~100-150 lines) with no business logic or UI rendering
- [ ] All manual tests pass
- [ ] Original streamlit_dashboard.py can be safely archived
