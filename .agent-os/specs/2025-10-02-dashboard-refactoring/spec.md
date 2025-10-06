# Spec Requirements Document

> Spec: Dashboard Refactoring
> Created: 2025-10-02

## Overview

Refactor the monolithic streamlit_dashboard.py file into a modular, scalable project structure with clear separation of concerns (UI, data, logic) while maintaining exact current behavior. This refactoring will improve code maintainability, enable easier future development, and establish a clean architecture that supports long-term growth.

## User Stories

### Developer Maintainability Story

As a developer, I want the dashboard code organized into logical modules with clear separation of concerns, so that I can quickly locate, understand, and modify specific functionality without navigating through a 1200+ line file.

The current streamlit_dashboard.py contains all UI rendering, database queries, business logic, and utility functions in a single file. This makes it difficult to maintain, test, and extend. By separating these concerns into dedicated modules (ui/, data/, logic/, utils/), developers can work on individual components independently, reducing cognitive load and the risk of unintended side effects when making changes.

### Future Feature Development Story

As a product team member, I want a modular codebase structure that makes it easy to add new features and UI components, so that we can iterate quickly on user feedback and deliver new functionality faster.

With the new structure, adding a new UI panel or widget only requires creating a new file in dashboard/ui/components/ without touching unrelated code. Similarly, new data queries go in dashboard/data/queries.py, and new business logic functions go in dashboard/logic/processing.py. This clear organization accelerates feature development and reduces integration conflicts.

### Code Quality and Testing Story

As a software engineer, I want each module to have a single, well-defined responsibility, so that I can write focused unit tests, catch bugs early, and ensure code reliability.

The refactored structure enables targeted testing: database queries can be tested independently from UI rendering, business logic can be validated with pure function tests, and UI components can be tested in isolation. This improves overall code quality and makes the codebase more robust.

## Spec Scope

1. **New Directory Structure** - Create dashboard/ source directory with ui/, data/, logic/, utils/ subdirectories and app.py as the new main entry point.

2. **UI Component Extraction** - Move all UI rendering logic into dashboard/ui/components/ (left_panel.py, center_panel.py, right_panel.py, file_widgets.py) and dashboard/ui/views/ (file_preview.py).

3. **Data Layer Separation** - Extract all database interaction functions (fetch_all_suppliers, fetch_projects, fetch_supplier_data) into dashboard/data/queries.py.

4. **Business Logic Isolation** - Move all data processing and calculation functions (filter_projects, sort_projects, calculate_*_statistics, group_events_by_folder_name, build_folder_tree) into dashboard/logic/processing.py.

5. **Utility Function Consolidation** - Relocate helper functions (format_timestamp, create_file_link, run_startup_crawler, run_manual_refresh) into dashboard/utils/helpers.py and configuration loading into dashboard/config.py.

6. **Main Application Refactoring** - Create lean app.py that orchestrates initialization, session state management, and calls the modular components without containing business logic or UI rendering code.

7. **Behavior Preservation** - Ensure all existing functionality works identically after refactoring (no changes to UI, features, or user experience).

## Out of Scope

- Adding new features or changing existing functionality
- Modifying the UI design, layout, or user experience
- Changing database schema or query logic beyond relocating code
- Performance optimization or code improvements beyond reorganization
- Adding automated tests (can be done in future spec)
- Refactoring the rfq_tracker crawler module or DBManager class
- Documentation updates or README changes

## Expected Deliverable

1. The new app.py runs successfully with `streamlit run app.py` and displays the dashboard with identical behavior to the original streamlit_dashboard.py.

2. All existing features work correctly: project list, filters, pagination, sorting, supplier selection, file preview, download buttons, manual refresh, and startup crawler.

3. The dashboard/ directory structure exists with all modules properly organized, and the old streamlit_dashboard.py can be safely archived or removed.
