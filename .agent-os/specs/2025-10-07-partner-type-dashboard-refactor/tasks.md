# Spec Tasks

These are the tasks to be completed for the spec detailed in @.agent-os/specs/2025-10-07-partner-type-dashboard-refactor/spec.md

> Created: 2025-10-07
> Status: Ready for Implementation

## Tasks

- [ ] 1. Database Schema and Data Model Implementation
  - [ ] 1.1 Write unit tests for `partner_type` field validation on suppliers collection (enum constraint, default value)
  - [ ] 1.2 Write unit tests for `partner_type` field validation on submissions collection (enum constraint, default value)
  - [ ] 1.3 Add `partner_type` field to suppliers MongoDB collection schema with enum ['Supplier', 'Contractor'] and default 'Supplier'
  - [ ] 1.4 Add `partner_type` field to submissions MongoDB collection schema with enum ['Supplier', 'Contractor'] and default 'Supplier'
  - [ ] 1.5 Create MongoDB indexes: `partner_type` single-field index on both collections
  - [ ] 1.6 Create MongoDB compound indexes: `project_id` + `partner_type` on both collections
  - [ ] 1.7 Create MongoDB compound index: `project_id` + `partner_type` + `direction` on submissions collection
  - [ ] 1.8 Verify all schema tests pass and indexes are created successfully

- [ ] 2. Crawler Logic Enhancement for Partner Type Detection
  - [ ] 2.1 Write unit tests for path parsing logic to detect "Contractor RFQ Quotes" folder structure
  - [ ] 2.2 Write unit tests for path parsing logic to detect "Supplier RFQ Quotes" (default) folder structure
  - [ ] 2.3 Write unit tests to verify partner_type is correctly assigned to supplier documents based on folder path
  - [ ] 2.4 Write unit tests to verify partner_type is correctly assigned to submission documents based on folder path
  - [ ] 2.5 Update crawler path parsing logic to detect "Contractor RFQ Quotes" pattern and set partner_type='Contractor'
  - [ ] 2.6 Update crawler path parsing logic to detect "Supplier RFQ Quotes" (or default RFQ) pattern and set partner_type='Supplier'
  - [ ] 2.7 Ensure partner_type is applied to both supplier documents and all associated submission documents
  - [ ] 2.8 Verify all crawler tests pass and partner_type is correctly populated during test scans

- [ ] 3. Backend Query Layer and Aggregation Logic
  - [ ] 3.1 Write unit tests for filtering suppliers by partner_type
  - [ ] 3.2 Write unit tests for filtering submissions by partner_type
  - [ ] 3.3 Write unit tests for aggregation query computing unique partners contacted (sent count) by partner_type
  - [ ] 3.4 Write unit tests for aggregation query computing unique partners with responses (received count) by partner_type
  - [ ] 3.5 Write unit tests for partner statistics aggregation (sent/received counts per partner filtered by partner_type)
  - [ ] 3.6 Update database query functions to include partner_type filter parameter
  - [ ] 3.7 Implement aggregation pipeline for project-level statistics (contacted count and response count by partner_type)
  - [ ] 3.8 Implement aggregation pipeline for partner-level statistics (sent/received counts per partner)
  - [ ] 3.9 Add backward compatibility logic to handle documents without partner_type field (treat as 'Supplier')
  - [ ] 3.10 Verify all backend query tests pass with correct filtered results

- [ ] 4. UI Component Implementation and Dashboard Refactoring
  - [ ] 4.1 Write UI tests for partner type toggle (radio button) in left panel with session state persistence
  - [ ] 4.2 Write UI tests for project header displaying project number and aggregate statistics
  - [ ] 4.3 Write UI tests for enhanced partner list showing inline sent/received counts
  - [ ] 4.4 Write UI tests for simplified partner header (project number removed)
  - [ ] 4.5 Write UI tests for streamlined event card layout (single-line folder/stats)
  - [ ] 4.6 Implement partner type radio button filter in left panel (Suppliers/Contractors toggle) with session state
  - [ ] 4.7 Implement persistent project header component in center panel (project number + aggregate statistics)
  - [ ] 4.8 Update partner list component in right panel to display inline sent/received counts per partner
  - [ ] 4.9 Simplify partner header in center panel by removing redundant project number display
  - [ ] 4.10 Refactor event card layout to single-line format (folder name left-aligned, file/size stats right-aligned)
  - [ ] 4.11 Connect UI components to backend queries with partner_type filtering
  - [ ] 4.12 Verify all UI tests pass and components render correctly with filtered data

- [ ] 5. Integration Testing and End-to-End Validation
  - [ ] 5.1 Write integration test for full crawler-to-UI flow with Contractor RFQ Quotes folder structure
  - [ ] 5.2 Write integration test for full crawler-to-UI flow with Supplier RFQ Quotes folder structure
  - [ ] 5.3 Write integration test for partner type toggle switching between Suppliers and Contractors views
  - [ ] 5.4 Write integration test verifying project-level statistics update correctly when toggle changes
  - [ ] 5.5 Write integration test verifying partner list updates correctly when toggle changes
  - [ ] 5.6 Perform manual testing with mock_projects data to verify Contractor partners are detected and displayed
  - [ ] 5.7 Perform manual testing to verify backward compatibility with existing Supplier data
  - [ ] 5.8 Verify all integration tests pass and dashboard behavior is correct for both partner types
