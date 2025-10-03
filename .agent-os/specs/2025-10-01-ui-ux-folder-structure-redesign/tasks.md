# Spec Tasks

These are the tasks to be completed for the spec detailed in @.agent-os/specs/2025-10-01-ui-ux-folder-structure-redesign/spec.md

> Created: 2025-10-01
> Status: ✅ Complete
> Completed: 6/6 task groups (100%)

## Tasks

- [x] 1. Update Folder Structure and Mock Data (Foundation)
  - [x] 1.1 Write tests for new folder structure pattern parsing
  - [x] 1.2 Update crawler.py path regex to recognize "1-RFQ/Supplier RFQ Quotes/" pattern
  - [x] 1.3 Modify extract_metadata() to handle new intermediate layers
  - [x] 1.4 Add backward compatibility for old folder structure
  - [x] 1.5 Update mock_projects directory structure with new layers
  - [x] 1.6 Create migration script for reorganizing mock data
  - [x] 1.7 Test crawler with updated mock_projects
  - [x] 1.8 Verify all tests pass and MongoDB is populated correctly

- [x] 2. Implement Two-Panel Layout Foundation
  - [x] 2.1 Write tests for layout components and state management
  - [x] 2.2 Create custom CSS for fixed left panel (30%) and scrollable right panel (70%)
  - [x] 2.3 Implement session state management for panel navigation
  - [x] 2.4 Add responsive design for mobile (<768px)
  - [x] 2.5 Verify layout renders correctly and panels behave as expected

- [x] 3. Build Left Panel Components
  - [x] 3.1 Write tests for search, filter, and pagination functionality
  - [x] 3.2 Implement manual refresh button with crawler trigger
  - [x] 3.3 Add search bar with debounced filtering (500ms)
  - [x] 3.4 Create filter controls (supplier multiselect, project input, date range)
  - [x] 3.5 Implement pagination with 15 projects per page
  - [x] 3.6 Add Previous/Next navigation buttons
  - [x] 3.7 Verify all filters and search work correctly with tests

- [x] 4. Implement Right Panel Hierarchical Dropdowns
  - [x] 4.1 Write tests for dropdown hierarchy and statistics calculation
  - [x] 4.2 Create supplier expander components with custom styling
  - [x] 4.3 Implement two-column layout (Received | Sent) within each supplier
  - [x] 4.4 Add nested date folder expanders
  - [x] 4.5 Build recursive folder tree component for file display
  - [x] 4.6 Implement MongoDB aggregation for statistics (file count, sizes)
  - [x] 4.7 Add statistics badges at each dropdown level
  - [x] 4.8 Implement lazy loading for supplier data
  - [x] 4.9 Verify dropdowns, statistics, and folder trees work correctly

- [x] 5. Add File Preview and Download Functionality
  - [x] 5.1 Write tests for file preview navigation and rendering
  - [x] 5.2 Implement session state for preview/list view navigation
  - [x] 5.3 Create back button to return to folder view
  - [x] 5.4 Add download button with file bytes handling
  - [x] 5.5 Implement PDF viewer using iframe or base64 encoding
  - [x] 5.6 Add support for image and text file preview
  - [x] 5.7 Implement error handling for preview failures
  - [x] 5.8 Verify preview, navigation, and download work for all file types

- [x] 6. Performance Optimization and Polish
  - [x] 6.1 Implement caching for statistics and aggregation queries
  - [x] 6.2 Add loading spinners for crawler, preview, and data fetching
  - [x] 6.3 Optimize session state management for dropdown states
  - [x] 6.4 Add accessibility features (ARIA labels, keyboard navigation)
  - [x] 6.5 Test end-to-end user workflows
  - [x] 6.6 Verify all performance optimizations and accessibility features work
