# Spec Requirements Document

> Spec: UI/UX and Folder Structure Redesign
> Created: 2025-10-01

## Overview

Redesign the RFQ Dashboard with an improved two-panel layout featuring intuitive navigation, hierarchical supplier dropdowns, in-browser file preview, and comprehensive statistics at each folder level. This spec begins with updating the folder structure crawler to match the real network path pattern including the "1-RFQ" prefix and "Supplier RFQ Quotes" intermediate directory layer as a critical first step before implementing UI changes.

## User Stories

### Efficient Project Navigation

As a project manager, I want to quickly filter and navigate through projects using a dedicated left panel with search, filters, and pagination, so that I can find relevant RFQ information without scrolling through long lists or toggling confusing radio buttons.

Users will see a clean left panel containing a refresh button, search bar (for project numbers and suppliers), filters (supplier name, project number, date range), and a paginated list showing 15 projects per page. The panel remains fixed while the right panel updates based on selection.

### Intuitive Supplier Document Access

As a procurement team member, I want to explore supplier documents through expandable dropdowns organized by Received/Sent folders with date-based organization, so that I can quickly understand what documents exist and access them without navigating complex folder structures.

Users will select a project from the left panel, then see all suppliers for that project displayed as collapsible dropdown sections in the right panel. When expanded, each supplier shows two columns (Received and Sent), with date folders as nested dropdowns. Each level displays statistics (file count, total size) providing visibility into document volume before drilling down.

### In-Browser Document Preview

As an engineering staff member, I want to preview PDF and other documents directly in my browser without downloading them first, so that I can quickly verify document contents and only download what I need.

Users will click on a file in the folder tree, which navigates to a new preview screen showing the document content with a back button to return to the folder view and a download button to save the file locally. This eliminates the need to download every file just to check its contents.

## Spec Scope

**Implementation Order:** Items 6-7 (Folder Structure Update and Mock Data Migration) must be completed first before beginning UI work (items 1-5). This ensures the crawler and data layer properly support the new folder structure before building UI components that depend on it.

1. **Two-Panel Layout** - Implement a split-screen interface with fixed left panel (project list) and dynamic right panel (supplier details).

2. **Left Panel Components** - Add manual refresh button, search bar (project/supplier search), filter controls (supplier, project, date range), and paginated project list (15 items per page).

3. **Right Panel Hierarchical Dropdowns** - Display suppliers as expandable dropdowns with Received/Sent columns, date folders as nested dropdowns, and full folder tree navigation at the date level.

4. **File Statistics Display** - Show file count, total size, and relevant statistics at each dropdown level (supplier, Received/Sent, date folder).

5. **In-Browser File Preview** - Create document preview screen with back navigation, download button, and embedded PDF/file viewer.

6. **Folder Structure Update** - Update crawler to handle new path pattern: `Projects/{project}/1-RFQ/Supplier RFQ Quotes/{supplier}/{Received|Sent}/{date}/file.pdf`.

7. **Mock Data Migration** - Update mock_projects to reflect new folder structure with "1-RFQ" and "Supplier RFQ Quotes" layers.

## Out of Scope

- Excel integration for project status tracking (planned for future phase)
- Multi-file bulk download/export functionality
- Document versioning or comparison features
- Authentication and user permissions (Phase 3 roadmap item)
- Advanced search with full-text document content indexing

## Expected Deliverable

1. **Redesigned Dashboard UI** - Two-panel layout with left panel (search, filters, pagination) and right panel (supplier dropdowns with statistics) loads successfully at http://localhost:8501.

2. **Document Preview Functionality** - Clicking any file in the folder tree navigates to a preview screen showing the document with working back and download buttons.

3. **Updated Crawler** - Crawler successfully indexes the new folder structure pattern and populates MongoDB with correct project, supplier, and document metadata from updated mock_projects directory.
