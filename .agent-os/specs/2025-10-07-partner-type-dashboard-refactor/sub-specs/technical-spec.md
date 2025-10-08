# Technical Specification

This is the technical specification for the spec detailed in @.agent-os/specs/2025-10-07-partner-type-dashboard-refactor/spec.md

## Technical Requirements

### 1. Data Model Changes

- Add `partner_type` field (String, enum: 'Supplier' | 'Contractor') to both `suppliers` and `submissions` MongoDB collections
- Default value for `partner_type` should be 'Supplier' for backward compatibility
- Update MongoDB indexes if needed for efficient filtering by `partner_type`

### 2. Crawler Logic Updates

- Modify the crawler's path parsing logic to detect the presence of "Contractor RFQ Quotes" directory
- Reference pattern: `mock_projects/12345/1-RFQ/Contractor RFQ Quotes/SupplierA/Received/2024-03-01-Initial-Response`
- When "Contractor RFQ Quotes" is detected in the path, set `partner_type = 'Contractor'`
- When "Supplier RFQ Quotes" (or default RFQ folder) is detected, set `partner_type = 'Supplier'`
- Ensure the partner_type is applied to both the partner document and all associated submission documents

### 3. UI Component Structure

#### 3.1 Left Panel (Filters)
- Add `st.radio` component with options: ["Suppliers", "Contractors"]
- Store selection in Streamlit session state
- Default to "Suppliers" on first load
- This filter drives all data queries across the dashboard

#### 3.2 Center Panel - New Project Header
- Create new top-level header component (persistent, above partner selection)
- Display: Project number (e.g., "Project 67890")
- Display: Aggregate statistics with dynamic label based on partner_type toggle
  - Format: `{X} [Suppliers|Contractors] Contacted | {Y} Responses Received`
  - `{X}` = Count of unique partners with at least one 'sent' submission (filtered by partner_type)
  - `{Y}` = Count of unique partners with at least one 'received' submission (filtered by partner_type)

#### 3.3 Center Panel - Simplified Partner Header
- Remove project number display (now shown in project header)
- Keep only: Partner name + file/size statistics specific to that partner

#### 3.4 Center Panel - Streamlined Event Cards
- Refactor submission card headers to single-line layout:
  - Left-aligned: Folder name
  - Right-aligned: Files count and Size statistics
  - Use Streamlit columns or CSS flexbox for horizontal alignment

#### 3.5 Right Panel - Enhanced Partner List
- Update partner list entries to include inline statistics
- Format: `PartnerName [Sent: {S_count}, Received: {R_count}]`
  - `{S_count}` = Total count of 'sent' submissions for that partner
  - `{R_count}` = Total count of 'received' submissions for that partner
- These counts must be pre-computed or efficiently queried from MongoDB

### 4. Database Query Updates

- All queries for suppliers/submissions must include filter: `{"partner_type": selected_partner_type}`
- Aggregate statistics queries must:
  - Group by partner_type
  - Count unique partners with sent submissions
  - Count unique partners with received submissions
- Partner list queries must include aggregation pipeline to compute sent/received counts per partner

### 5. Performance Considerations

- Pre-compute or cache partner statistics to avoid real-time aggregation on every render
- Consider using MongoDB aggregation pipeline for efficient counting
- Ensure indexes on `partner_type` field for fast filtering

### 6. Backward Compatibility

- Existing data without `partner_type` field should default to 'Supplier'
- Crawler must handle existing folder structures gracefully
- UI must function correctly even if some documents lack `partner_type` field
