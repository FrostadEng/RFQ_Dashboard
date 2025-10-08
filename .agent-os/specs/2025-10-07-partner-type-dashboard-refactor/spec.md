# Spec Requirements Document

> Spec: Partner Type Dashboard Refactor
> Created: 2025-10-07

## Overview

Refactor the RFQ Dashboard's information hierarchy to better separate project-level and partner-level statistics, and introduce a new "Contractor" partner type based on a specific folder structure. This enhancement will enable users to toggle between Supplier and Contractor views, providing clearer context and more actionable insights at both the project and partner levels.

## User Stories

### Project Manager Viewing Contractor RFQs

As a project manager, I want to view Contractor RFQs separately from Supplier RFQs, so that I can track subcontractor bidding processes independently from material supplier quotes.

The user selects the "Contractors" toggle in the left panel. The dashboard immediately updates to show only contractors in the partner list (right panel), displays contractor-specific project statistics in the new project header (e.g., "5 Contractors Contacted | 3 Responses Received"), and filters the center panel to show only the selected contractor's submission details. This allows the user to focus exclusively on contractor-related RFQ activity without supplier data creating visual noise.

### Procurement Team Member Scanning Partner Response Rates

As a procurement team member, I want to see sent/received counts directly in the partner list, so that I can quickly identify which partners are responsive without clicking through each one.

When viewing the right-side panel, each partner entry displays inline statistics (e.g., "SupplierA [Sent: 4, Received: 2]"). The user can immediately scan the list to identify partners with zero responses or low response rates, enabling faster follow-up actions without the need to select each partner individually to view their submission history.

### Engineer Reviewing Project-Wide RFQ Activity

As an engineer, I want to see project-level statistics at the top of the dashboard, so that I understand the overall RFQ context before diving into individual partner details.

Upon selecting a project, the user sees a persistent header displaying the project number and aggregate statistics for the currently active partner type (Suppliers or Contractors). This provides immediate context about total engagement (how many partners contacted vs. responded) before the user explores individual partner submissions in the center panel.

## Spec Scope

1. **New Partner Type Field** - Add a `partner_type` field to MongoDB collections (`suppliers` and `submissions`) with values 'Supplier' or 'Contractor'
2. **Crawler Logic Enhancement** - Update crawler to detect "Contractor RFQ Quotes" folder structure and assign partner_type accordingly
3. **Project-Level Header** - Add persistent project header with project number and aggregate partner statistics
4. **Partner List Enhancement** - Display sent/received counts inline for each partner in the right-side panel
5. **UI Toggle for Partner Type** - Add radio button filter in left panel to switch between "Suppliers" and "Contractors" views
6. **Simplified Partner Header** - Streamline the selected partner's header by removing redundant project number
7. **Compact Event Card Layout** - Move file/size statistics to same line as folder name in submission cards

## Out of Scope

- Mixed views showing both Suppliers and Contractors simultaneously
- Historical migration of existing partner_type data (crawler will populate on next scan)
- Additional partner types beyond Supplier and Contractor
- Filtering by multiple partner types at once
- Export or reporting functionality for partner statistics

## Expected Deliverable

1. Dashboard correctly displays two distinct views (Suppliers/Contractors) when toggling the radio button, with all panels updating accordingly
2. Project-level statistics accurately reflect counts of contacted and responding partners for the selected partner type
3. Partner list shows inline sent/received counts without requiring selection
4. Crawler correctly identifies and tags Contractor partners based on "Contractor RFQ Quotes" folder path
5. All existing Supplier data continues to function correctly with the new partner_type field defaulting to 'Supplier'
