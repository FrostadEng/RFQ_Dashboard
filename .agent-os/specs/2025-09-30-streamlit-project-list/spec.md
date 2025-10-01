# Spec Requirements Document

> Spec: Streamlit Project List View
> Created: 2025-09-30

## Overview

Implement a web-based project list view using Streamlit to replace the existing PyQt6 desktop sidebar, enabling browser-based access for all team members on the local work network. This feature serves as the first step in migrating the RFQ Dashboard from a desktop application to a web application that runs on one work computer and is accessible by the entire team through their browsers.

## User Stories

### Project Manager Accessing Dashboard from Any Workstation

As a project manager, I want to view a searchable list of all projects from any computer on the work network, so that I can quickly find and access RFQ information without installing software or using a specific workstation.

**Workflow:** User opens `http://<server-computer-ip>:8501` in their browser from any workstation, sees a sidebar with all projects listed by project number, uses the search bar to filter by project number, and clicks on a project to view its details. No installation or configuration needed on their workstation.

### Procurement Team Member Sorting Projects

As a procurement team member, I want to sort projects by number, date, or last scanned time, so that I can prioritize my review of recently updated or high-priority projects.

**Workflow:** User views the project list sidebar, selects a sort option from a dropdown (e.g., "Sort by: Last Scanned"), and sees the project list reorder immediately to show the most recently scanned projects first.

### Engineering Team Accessing Via Browser

As an engineering team member, I want to access the RFQ dashboard through my web browser on the local network, so that I can view project data without installing PyQt6 or MongoDB on my workstation.

**Workflow:** User navigates to the dashboard URL from their workstation browser, sees the project list load from the centralized MongoDB instance running on the server computer, and interacts with the interface without any local software dependencies.

## Spec Scope

1. **Streamlit Sidebar Layout** - Create a sidebar component that displays the list of projects retrieved from MongoDB.
2. **Search/Filter Functionality** - Implement real-time search that filters projects by project number as the user types.
3. **Sort Options** - Add dropdown to sort projects by project number (ascending/descending), date, or last scanned timestamp.
4. **Project Selection State** - Maintain selected project state using Streamlit session state to enable detail view integration.
5. **Network Accessibility** - Configure Streamlit to listen on all network interfaces (0.0.0.0) so team members can access from their browsers.

## Out of Scope

- Supplier detail view (will be addressed in subsequent spec)
- Docker containerization (separate spec, Phase 1.2)
- User authentication (Phase 3 feature)
- Export functionality (Phase 2 feature)
- File preview or download (Phase 2 feature)
- Migration of custom widgets (collapsible sections, link labels - handled in detail view spec)
- Internet/external network access (local network only)
- HTTPS/SSL configuration (can be added later if needed)

## Expected Deliverable

1. Running `streamlit run streamlit_dashboard.py --server.address=0.0.0.0` on the server computer makes the dashboard accessible to all team members at `http://<server-ip>:8501`.
2. Opening the dashboard displays a sidebar with all projects from MongoDB, searchable and sortable in real-time.
3. Selecting a project from the sidebar updates the session state and displays a placeholder message indicating which project is selected.
4. Search functionality filters the project list instantly as the user types, showing only matching project numbers.
