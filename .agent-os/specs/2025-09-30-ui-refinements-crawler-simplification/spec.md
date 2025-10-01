# Spec Requirements Document

> Spec: UI Refinements and Crawler Simplification
> Created: 2025-09-30

## Overview

Simplify the RFQ crawler logic by treating Sent and Received folders identically (folder-based only, removing ZIP file complexity), improve UI with dark mode default and clickable project paths, and update the dashboard to display the simplified data structure. This refactoring reduces code complexity while maintaining the ability to track ongoing negotiations through multiple sent/received exchanges per supplier.

## User Stories

### Project Manager Tracking Ongoing Negotiations

As a project manager, I want to see multiple sent and received folders for each supplier in chronological order, so that I can track the back-and-forth negotiation process and understand the timeline of communications.

**Workflow:** User selects a project, expands a supplier section, sees a chronological list of sent folders (e.g., "2024-01-15-Transmission", "2024-02-20-Revision") and received folders (e.g., "2024-03-01-Response", "2024-03-15-Counter-Offer"), each with file counts and access to the documents inside, allowing them to review the negotiation history.

### User Accessing Project Folder Directly

As a user, I want to click on the project number to open the project folder in my file explorer, so that I can quickly access the entire project directory without navigating through the folder structure manually.

**Workflow:** User sees "Project 80123" at the top of the dashboard, clicks on the project number link, and their file explorer opens directly to the `/Projects/80123/` folder on the server.

### User Preferring Dark Mode

As a user who works in low-light environments, I want the dashboard to start in dark mode by default, so that I don't experience eye strain from a bright white interface.

**Workflow:** User opens the Streamlit dashboard and immediately sees a dark-themed interface without needing to toggle settings.

## Spec Scope

1. **Dark Mode Default** - Configure Streamlit theme to use dark mode as the default color scheme.

2. **Clickable Project Path** - Replace the info banner displaying project path with a clickable project number that opens the project folder in file explorer.

3. **Simplify Crawler Logic** - Refactor crawler to treat Sent and Received folders identically:
   - Remove ZIP file processing logic
   - Process both folders as collections of submission folders
   - Use folder creation timestamp for dates
   - Store all submissions in unified `submissions` collection with `type` field

4. **Update Mock Projects** - Modify mock_projects structure to use folder-based format with 2+ folders in Sent directories.

5. **Update Database Schema** - Unify transmissions and receipts into single `submissions` collection:
   - Merge both collections into one
   - Add `type` field ("sent" or "received")
   - Unified schema: `folder_name`, `folder_path`, `date`, `files`, `type`
   - Update indexes and db_manager.py accordingly

6. **Update Dashboard Display** - Modify Streamlit UI to query unified `submissions` collection and filter by type for display in Sent/Received columns.

7. **Testing & Validation** - Test complete workflow: crawler → MongoDB → dashboard display, verify multiple sent/received folders display correctly.

## Out of Scope

- ZIP file support (explicitly removed)
- Parsing dates from folder names (use timestamps only)
- Date parsing from folder names (use timestamps only)
- Advanced date formatting or sorting beyond chronological
- Email notifications or automation features

## Expected Deliverable

1. Streamlit dashboard opens in dark mode by default.

2. Project number is clickable and opens project folder in file explorer (removing the path info banner).

3. Crawler processes Sent folders as folder collections (not ZIPs), storing data identically to Received folders.

4. Mock projects updated with folder-based Sent structure (2+ folders per supplier).

5. MongoDB uses unified `submissions` collection (replaces separate transmissions/receipts).

6. Dashboard displays both Sent and Received sections with identical folder tree rendering, showing multiple submissions per supplier in chronological order.

7. Complete workflow tested: run crawler → verify MongoDB → view dashboard → access files.
