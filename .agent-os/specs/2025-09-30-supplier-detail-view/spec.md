# Spec Requirements Document

> Spec: Streamlit Supplier Detail View with File Access
> Created: 2025-09-30

## Overview

Implement the supplier detail view in the Streamlit dashboard to display RFQ transmissions and receipts for the selected project, enabling users to browse and open documents directly from the web interface. This feature completes the core Streamlit migration by providing full access to RFQ data with preserved folder structures, replacing the PyQt6 collapsible widgets with Streamlit expanders.

## User Stories

### Project Manager Reviewing Supplier Submissions

As a project manager, I want to see all suppliers for a selected project with their sent transmissions and received submissions organized clearly, so that I can quickly assess the status of the RFQ process and access any document I need.

**Workflow:** User selects a project from the sidebar, sees a list of expandable supplier sections in the main content area, clicks to expand the first supplier (auto-expanded by default), reviews the sent ZIP files and received submission folders with their dates and file counts, and can open any file directly in their default application by clicking a link.

### Engineering Team Accessing Technical Documents

As an engineering team member, I want to navigate through the folder structure of supplier submissions to find specific technical drawings or documents, so that I can review the details without manually browsing the file server.

**Workflow:** User selects a project, expands a supplier section, navigates through the hierarchical folder tree displayed for received submissions, sees the complete folder structure (e.g., `/Drawings/Mechanical/Part-A.pdf`), and clicks to open the file in their PDF viewer.

### Procurement Team Verifying Transmission Dates

As a procurement team member, I want to see when transmissions were sent and when submissions were received with clear timestamps, so that I can verify compliance with RFQ deadlines and track supplier responsiveness.

**Workflow:** User selects a project, views the supplier list with transmission and receipt metadata including formatted dates, sorts or filters based on submission dates (future enhancement), and accesses the source files for each transmission to verify contents.

## Spec Scope

1. **Supplier Section Display** - Fetch and display all suppliers for the selected project using Streamlit expanders, with the first supplier auto-expanded by default.

2. **Two-Column Layout** - Create a side-by-side layout showing "Sent Transmissions" on the left and "Received Submissions" on the right for each supplier.

3. **Transmission Metadata Display** - Show ZIP file names, sent dates, and source file counts for each transmission with formatted timestamps.

4. **Receipt Metadata with Folder Structure** - Display received submission folders with complete hierarchical folder trees, preserving the nested structure (folders within folders).

5. **File Access Integration** - Implement clickable file links that open files in the user's system default application (similar to `file://` protocol or system open command).

6. **File Download to Browser** - Provide download buttons for individual files and ZIP files, allowing users to download documents directly through their web browser as an alternative to opening in system applications.

7. **Pagination for Large File Lists** - Add pagination or scrollable containers when suppliers have many files to prevent UI overload.

8. **Empty State Handling** - Display appropriate messages when a project has no suppliers, or a supplier has no transmissions/receipts.

## Out of Scope

- File preview within Streamlit (inline PDF/image viewing)
- Editing or uploading files through the dashboard
- Advanced filtering/sorting of suppliers (can be added in Phase 2)
- File search within supplier documents (Phase 2 feature)
- User authentication (Phase 3)
- Folder tree collapse/expand state persistence across page refreshes

## Expected Deliverable

1. Opening the Streamlit dashboard, selecting a project displays all suppliers with expandable sections, first supplier auto-expanded.

2. Each supplier section shows a two-column layout with sent transmissions (left) and received submissions (right), including dates and file counts.

3. Received submissions display complete folder hierarchies (e.g., `📁 Drawings > 📁 Mechanical > 📄 Part-A.pdf`) preserving the nested structure.

4. Clicking any file link opens the file in the user's default system application (PDF viewer, CAD software, etc.), with download button as alternative.

5. Users can download individual files or ZIP files directly through the browser using Streamlit download buttons.

6. Large file lists are paginated or contained in scrollable areas to maintain UI performance.

7. Dashboard handles edge cases gracefully (no suppliers, no files, missing data).
