# Project RFQ Tracker - Product Mission

## The Pitch

Project RFQ Tracker is a **web-based document tracking and management system** that centralizes scattered Request for Quotation (RFQ) documents across complex server folder structures. It automates the manual process of locating and verifying supplier transmissions and receipts, transforming hours of folder hunting into instant searchable access. By providing a clean, modern dashboard accessible from any browser, it reduces errors, saves significant time, and improves project management efficiency for engineering and procurement teams.

**Why it matters:** In large organizations, RFQ documents are often buried in nested folder structures on shared drives. Finding the right supplier quote or verifying receipt dates requires manual navigation through dozens of folders. This tool eliminates that friction by automatically crawling the file system, extracting metadata, and presenting everything in an intuitive, searchable interface.

---

## Target Users

### Primary Users

1. **Project Managers**
   - **Pain Points:** Spend hours manually searching folder structures to verify supplier submissions, track RFQ timelines, and ensure all required documents are present.
   - **Goals:** Quick access to all RFQ documents for a given project, ability to verify submission status at a glance, generate reports for stakeholders.
   - **How This Helps:** Centralized dashboard shows all suppliers, transmissions, and receipts for each project with instant search and filtering.

2. **Procurement Teams**
   - **Pain Points:** Need to track multiple RFQs across different projects simultaneously, verify receipt dates for compliance, and coordinate with suppliers.
   - **Goals:** Monitor RFQ status across all active projects, export data for reporting, quickly locate specific supplier documents.
   - **How This Helps:** Cross-project search, filtering by supplier or date, clickable links to open files directly from the dashboard.

3. **Engineering Teams**
   - **Pain Points:** Frequently need to access technical specifications and supplier proposals but don't know the exact folder locations.
   - **Goals:** Quick access to technical documents without navigating complex folder structures.
   - **How This Helps:** Search by project number or supplier name, direct file access from the web interface.

---

## Problems We Solve

### Problem 1: Manual Document Location
**Current State:** Engineers and project managers manually navigate through complex nested folder structures (e.g., `/Projects/80123/RFQ/Supplier Name/Sent/` and `/Received/`) to find specific documents. This can take 10-30 minutes per search.

**Our Solution:** Automated crawler scans the entire folder structure, extracts metadata (project numbers, supplier names, file paths, dates), and stores it in MongoDB. Users search by project number or supplier name and get instant results.

**Impact:** Reduces document location time from minutes to seconds, eliminating navigation errors and missed documents.

---

### Problem 2: Scattered Information
**Current State:** RFQ data exists only as files in folders. There's no central view of which suppliers have been contacted, what has been sent, or what has been received for a given project.

**Our Solution:** Dashboard provides a unified view showing all suppliers for a project, with collapsible sections for sent transmissions and received submissions, including dates and file counts.

**Impact:** Project managers can see the complete RFQ status for any project in a single view, improving oversight and decision-making.

---

### Problem 3: Limited Accessibility
**Current State:** Teams need direct access to the file server and must navigate using Windows Explorer or file managers. Remote workers or those without VPN access cannot easily access documents.

**Our Solution:** Web-based Streamlit dashboard accessible from any browser. Users interact through a clean interface with search, filtering, and clickable file links.

**Impact:** Improves accessibility for remote teams, reduces dependency on specific desktop configurations, enables broader team collaboration.

---

### Problem 4: No Historical Tracking
**Current State:** No easy way to track when documents were sent or received, verify compliance with timelines, or generate reports for audits.

**Our Solution:** Database stores timestamps for all transmissions and receipts. Future analytics features will track supplier quality and performance over time.

**Impact:** Enables compliance reporting, quality tracking, and data-driven supplier selection.

---

## What Makes Us Different

1. **Purpose-Built for RFQ Workflows:** Unlike generic document management systems, this tool is specifically designed for the RFQ folder structure pattern (projects → suppliers → sent/received).

2. **Zero Configuration for Users:** Crawler automatically discovers projects and suppliers based on folder naming conventions. Users don't need to manually tag or organize anything.

3. **Hybrid Approach:** Combines automated file system scanning with database persistence, providing the speed of a database with the simplicity of file-based storage.

4. **Direct File Access:** Clickable links open files in the user's native file explorer or application, bridging the web interface with the existing file server infrastructure.

5. **Docker-Native Deployment:** Entire stack (app + database) runs in containers, making deployment and updates trivial even for non-technical IT staff.

---

## Key Features

### Phase 0: Already Implemented (Desktop Version)

- [x] **File System Crawler:** Python-based scanner that recursively searches project folders for RFQ documents
- [x] **Metadata Extraction:** Automatically extracts project numbers, supplier names, file paths, and creation dates
- [x] **MongoDB Integration:** Robust database schema with proper indexing for projects, suppliers, transmissions, and receipts
- [x] **PyQt6 Desktop Dashboard:** Modern dark-themed GUI with search, filtering, and collapsible supplier sections
- [x] **Clickable File Links:** Direct file/folder access from the dashboard
- [x] **Configurable Filtering:** JSON-based configuration for folder exclusions and file type filters
- [x] **Upsert Strategy:** Database updates handle new and modified files gracefully
- [x] **Comprehensive Logging:** Debug and error tracking throughout the application

---

### Phase 1: Web Migration & Containerization (Immediate Priority)

**Effort: L** | **Timeline: 2-3 weeks**

- [ ] **Streamlit Migration:** Replace PyQt6 desktop UI with web-based Streamlit dashboard
  - [ ] Project list sidebar with search
  - [ ] Supplier detail view with collapsible sections
  - [ ] Clickable links to open files via web interface
  - [ ] Responsive design for various screen sizes

- [ ] **Docker Containerization:** Package entire application for easy deployment
  - [ ] Dockerfile for Python/Streamlit app
  - [ ] MongoDB container configuration
  - [ ] Docker Compose orchestration for multi-container setup
  - [ ] Volume mapping for persistent database storage
  - [ ] Network configuration for app-database communication

- [ ] **Configuration Enhancement:** Make folder structure fully configurable
  - [ ] Define RFQ folder patterns in config.json
  - [ ] Support for custom project folder naming conventions
  - [ ] Configurable depth limits for scanning

---

### Phase 2: Enhanced Usability & Features (Post-Deployment)

**Effort: M** | **Timeline: 3-4 weeks**

- [ ] **Advanced Filtering & Sorting:**
  - [ ] Sort projects by date, number, or last scanned time
  - [ ] Filter suppliers by status or document count
  - [ ] Search within specific document types

- [ ] **Export Functionality:**
  - [ ] Export project data to CSV/Excel
  - [ ] Generate PDF reports for project summaries
  - [ ] Batch export for multiple projects

- [ ] **Enhanced Interactivity:**
  - [ ] File preview in browser (for PDFs, images)
  - [ ] Folder tree view for complex project structures
  - [ ] Batch file download via ZIP

---

### Phase 3: Multi-User & Collaboration (Future)

**Effort: L** | **Timeline: 4-6 weeks**

- [ ] **User Authentication:**
  - [ ] Login system with role-based access
  - [ ] Track user activity (who accessed what)
  - [ ] Permission levels (view-only vs. admin)

- [ ] **Email Notifications:**
  - [ ] Alert when new supplier submissions are detected
  - [ ] Scheduled reports for project status
  - [ ] Deadline reminders for pending RFQs

---

### Phase 4: Analytics & Quality Tracking (Advanced)

**Effort: XL** | **Timeline: 6-8 weeks**

- [ ] **Supplier Quality Dashboard:**
  - [ ] Track supplier response times
  - [ ] Record quality ratings from project managers
  - [ ] Historical performance metrics
  - [ ] Recommendation system for supplier selection

- [ ] **Analytics & Reporting:**
  - [ ] Project timeline visualization
  - [ ] Supplier comparison charts
  - [ ] RFQ volume trends over time
  - [ ] Custom report builder

---

### Phase 5: Cloud & Scalability (Long-Term)

**Effort: M** | **Timeline: 2-3 weeks**

- [ ] **Cloud Deployment:**
  - [ ] AWS/Azure/GCP deployment options
  - [ ] Auto-scaling for crawler jobs
  - [ ] Cloud storage integration (S3/Azure Blob)

- [ ] **Performance Optimization:**
  - [ ] Incremental scanning (only changed files)
  - [ ] Background job scheduling for large crawls
  - [ ] Database optimization and indexing improvements

---

## Success Metrics

1. **Time Savings:** Reduce average document location time from 15 minutes to under 30 seconds (97% reduction)
2. **User Adoption:** 80% of project managers and procurement staff using the tool within 3 months of web deployment
3. **Data Coverage:** Successfully index 95%+ of all RFQ documents in the file system
4. **System Reliability:** 99% uptime for the web dashboard
5. **User Satisfaction:** Average rating of 4+ stars (out of 5) in user feedback surveys

---

## Technology Foundation

- **Backend:** Python with `pymongo` for database operations
- **Crawler:** File system scanning with metadata extraction
- **Database:** MongoDB for flexible document storage
- **Frontend:** Streamlit for rapid web UI development
- **Deployment:** Docker + Docker Compose for containerization
- **Configuration:** JSON-based settings for flexibility

---

*This document serves as the north star for the Project RFQ Tracker product development and Agent OS integration.*
