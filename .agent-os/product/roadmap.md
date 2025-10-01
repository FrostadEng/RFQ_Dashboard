# Project RFQ Tracker - Development Roadmap

---

## Phase 0: Already Completed ✅

**Status:** Production-ready desktop application

The following features have been fully implemented and tested in the PyQt6 desktop version:

### Core Backend
- [x] **File System Crawler** - Recursive directory scanning with `pathlib`
  - Pattern matching for RFQ folder structures
  - Project number extraction from folder names
  - Supplier discovery and metadata extraction
  - File timestamp collection (creation dates)

- [x] **MongoDB Integration** - Robust database layer
  - Schema design: projects, suppliers, transmissions, receipts
  - Unique indexes for efficient queries and upserts
  - Bulk write operations for performance
  - Connection management with error handling

- [x] **Configuration System** - JSON-based settings
  - Configurable root path for scanning
  - Folder filter tags (e.g., "Template", "archive")
  - File filter tags (e.g., ".db")
  - Database connection parameters

### Desktop UI (PyQt6)
- [x] **Main Dashboard** - Modern dark-themed interface
  - Project list sidebar with search functionality
  - Content area for supplier details
  - Responsive layout design

- [x] **Custom Widgets**
  - Collapsible supplier sections
  - Clickable file/folder links (opens in system file explorer)
  - Link labels for direct file access

- [x] **Search & Filtering**
  - Real-time project search
  - Case-insensitive filtering
  - Pagination controls (UI framework)

### Data Processing
- [x] **Transmission Processing** - Sent folder handling
  - ZIP file discovery
  - Source folder mapping
  - File inventory collection

- [x] **Receipt Processing** - Received folder handling
  - Submission folder discovery
  - Recursive file listing
  - Filtered file collection (excludes .db, etc.)

### Operational Features
- [x] **Logging Framework** - Comprehensive debug/error tracking
- [x] **Dry Run Mode** - Test crawler without database writes
- [x] **Upsert Strategy** - Graceful handling of re-scans and updates

---

## Phase 1: Web Migration & Containerization 🚀

**Priority:** IMMEDIATE
**Timeline:** 2-3 weeks
**Effort:** Large (L)

**Goal:** Replace desktop application with web-based Streamlit dashboard and containerize entire stack for easy deployment.

### 1.1 Streamlit Migration (Effort: M)

- [x] **Project List View** ✅ Completed 2025-09-30
  - [x] Sidebar with project listing
  - [x] Search/filter functionality
  - [x] Sort by project number, date, or last scanned
  - [x] Project selection state management

- [x] **Supplier Detail View** ✅ Completed 2025-09-30
  - [x] Expandable/collapsible supplier sections (st.expander)
  - [x] Two-column layout for Sent vs Received
  - [x] Display transmission metadata (ZIP name, date, file count)
  - [x] Display receipt metadata (folder name, date, file list)
  - [x] Folder structure preservation with hierarchical tree display

- [x] **File Access Integration** ✅ Completed 2025-09-30
  - [x] Generate file:// URLs for clickable links
  - [x] Download buttons for individual files
  - [x] Platform-aware file path handling (Windows/Linux)
  - [x] Dual access method (open + download)

- [ ] **UI/UX Enhancements**
  - [x] Custom CSS for dark theme (match PyQt6 aesthetic) ✅ Completed 2025-09-30
  - [ ] Responsive design for various screen sizes
  - [x] Loading indicators for database queries (via @st.cache_data)
  - [x] Error handling with user-friendly messages

### 1.2 Docker Containerization (Effort: M)

- [ ] **Dockerfile for Streamlit App**
  - [ ] Base image: `python:3.12-slim`
  - [ ] Copy application code and requirements
  - [ ] Install dependencies (`pymongo`, `streamlit`, etc.)
  - [ ] Expose port 8501
  - [ ] Health check endpoint
  - [ ] Non-root user for security

- [ ] **Docker Compose Configuration**
  - [ ] Service definition for Streamlit app
  - [ ] Service definition for MongoDB
  - [ ] Network configuration (app ↔ database)
  - [ ] Volume mapping for MongoDB data persistence
  - [ ] Volume mapping for config.json and logs
  - [ ] Environment variable injection
  - [ ] Restart policies

- [ ] **MongoDB Container Setup**
  - [ ] Official MongoDB image
  - [ ] Data volume for /data/db
  - [ ] Health checks
  - [ ] Initial database setup script (optional)
  - [ ] Backup/restore documentation

- [ ] **Deployment Documentation**
  - [ ] README update with Docker instructions
  - [ ] docker-compose.yml usage guide
  - [ ] Environment variable documentation
  - [ ] Troubleshooting guide

### 1.3 Configuration Enhancement (Effort: S)

- [ ] **Configurable Folder Structure**
  - [ ] Define RFQ folder name patterns in config.json
  - [ ] Support multiple folder name variations (e.g., "RFQ", "Supplier RFQ", "Contractor")
  - [ ] Configurable project folder pattern (currently numeric only)
  - [ ] Depth limit for recursive scanning
  - [ ] Custom sent/received folder names

- [ ] **Environment Variables**
  - [ ] Create `.env.example` template
  - [ ] Support for `MONGO_URI`, `MONGO_DB`, `ROOT_PATH`
  - [ ] Override config.json with environment variables
  - [ ] Docker-friendly configuration

- [ ] **Validation & Error Handling**
  - [ ] Validate config.json schema on startup
  - [ ] Provide clear error messages for missing/invalid config
  - [ ] Default values for optional settings

### 1.4 Testing & Validation (Effort: S)

- [ ] **Local Docker Testing**
  - [ ] Test `docker-compose up` from scratch
  - [ ] Verify database persistence across restarts
  - [ ] Test crawler execution within container
  - [ ] Validate Streamlit UI accessibility

- [ ] **Mock Data Testing**
  - [ ] Use `mock_projects/` directory for validation
  - [ ] Verify all metadata extraction works
  - [ ] Test edge cases (empty folders, missing files)

- [ ] **Documentation Testing**
  - [ ] Follow deployment guide step-by-step
  - [ ] Verify all instructions are clear and complete

---

## Phase 2: Enhanced Usability & Features 📊

**Priority:** High
**Timeline:** 3-4 weeks
**Effort:** Medium (M)

**Goal:** Improve user experience with advanced filtering, export capabilities, and interactive features.

### 2.1 Advanced Filtering & Sorting (Effort: S)

- [ ] **Project Filtering**
  - [ ] Multi-criteria search (project number, supplier name, date range)
  - [ ] Filter by document count (e.g., "projects with >5 suppliers")
  - [ ] Filter by last scanned date
  - [ ] Saved filter presets

- [ ] **Supplier Filtering**
  - [ ] Filter by transmission count
  - [ ] Filter by receipt count
  - [ ] Filter by date range (sent/received)
  - [ ] Search within supplier names

- [ ] **Sorting Options**
  - [ ] Sort projects by number, date, or name
  - [ ] Sort suppliers alphabetically or by activity
  - [ ] Customizable default sort order

### 2.2 Export Functionality (Effort: M)

- [ ] **CSV Export**
  - [ ] Export project list to CSV
  - [ ] Export supplier details for selected project
  - [ ] Export all transmissions/receipts with metadata
  - [ ] Configurable column selection

- [ ] **Excel Export**
  - [ ] Multi-sheet workbooks (projects, suppliers, transmissions)
  - [ ] Formatted headers and styling
  - [ ] Hyperlinks to file paths
  - [ ] Summary statistics sheet

- [ ] **PDF Reports**
  - [ ] Project summary report (cover page, supplier list, file inventory)
  - [ ] Custom report templates
  - [ ] Logo and branding options
  - [ ] Export as ZIP with embedded files (optional)

- [ ] **Batch Export**
  - [ ] Select multiple projects for export
  - [ ] ZIP download with all reports
  - [ ] Scheduled exports (future: email delivery)

### 2.3 Enhanced Interactivity (Effort: S)

- [ ] **File Preview**
  - [ ] In-browser PDF preview
  - [ ] Image preview (PNG, JPG, etc.)
  - [ ] Text file preview (plain text, logs)
  - [ ] Fallback to download for unsupported types

- [x] **Folder Tree View** ✅ Completed 2025-09-30
  - [x] Expandable folder hierarchy for complex projects
  - [x] Visual indication of file types (folder/file icons)
  - [x] Hierarchical navigation with proper indentation

- [ ] **Batch File Operations**
  - [ ] Download multiple files as ZIP
  - [ ] Copy file paths to clipboard (batch)
  - [ ] Generate shareable links (if web-accessible storage)

### 2.4 Performance Optimization (Effort: S)

- [x] **Pagination** ✅ Completed 2025-09-30
  - [x] Paginate large file lists (100+ files)
  - [x] Configurable page size (50 items per page)
  - [x] Page navigation controls

- [x] **Caching** ✅ Completed 2025-09-30
  - [x] Cache database queries with Streamlit's @st.cache_data
  - [x] TTL configuration (300s for supplier data)
  - [x] Efficient data loading

---

## Phase 3: Multi-User & Collaboration 👥

**Priority:** Medium
**Timeline:** 4-6 weeks
**Effort:** Large (L)

**Goal:** Enable multi-user access with authentication, activity tracking, and notifications.

### 3.1 User Authentication (Effort: M)

- [ ] **Login System**
  - [ ] Username/password authentication
  - [ ] Integration with Streamlit authentication libraries
  - [ ] Session management
  - [ ] Password reset functionality

- [ ] **Role-Based Access Control**
  - [ ] Admin role (full access, user management)
  - [ ] User role (view-only access)
  - [ ] Project Manager role (view + export)
  - [ ] Configurable role permissions

- [ ] **User Management**
  - [ ] Admin panel for user creation/deletion
  - [ ] User profile page
  - [ ] Activity log (who accessed what, when)

### 3.2 Email Notifications (Effort: M)

- [ ] **Event-Based Alerts**
  - [ ] New supplier submission detected
  - [ ] Project deadline reminder
  - [ ] Weekly digest of activity

- [ ] **Configurable Notifications**
  - [ ] User preference settings (opt-in/opt-out)
  - [ ] Email templates
  - [ ] SMTP configuration

- [ ] **Scheduled Reports**
  - [ ] Daily/weekly/monthly project status reports
  - [ ] Custom recipient lists
  - [ ] PDF attachments

### 3.3 Collaboration Features (Effort: S)

- [ ] **Comments & Notes**
  - [ ] Add comments to projects or suppliers
  - [ ] Tag team members (@mentions)
  - [ ] Comment history and threading

- [ ] **Task Management**
  - [ ] Create tasks related to RFQs
  - [ ] Assign tasks to users
  - [ ] Task status tracking

---

## Phase 4: Analytics & Quality Tracking 📈

**Priority:** Medium
**Timeline:** 6-8 weeks
**Effort:** Extra Large (XL)

**Goal:** Provide insights into supplier performance and RFQ trends.

### 4.1 Supplier Quality Dashboard (Effort: L)

- [ ] **Performance Metrics**
  - [ ] Average response time (sent → received)
  - [ ] Submission completeness score
  - [ ] Historical win rate (if bid results tracked)
  - [ ] On-time submission rate

- [ ] **Quality Ratings**
  - [ ] Project manager rating system (1-5 stars)
  - [ ] Criteria: quality, responsiveness, pricing, etc.
  - [ ] Comments/feedback field
  - [ ] Historical rating trends

- [ ] **Supplier Profiles**
  - [ ] Aggregated metrics per supplier
  - [ ] Project history and document counts
  - [ ] Contact information and notes
  - [ ] Recommendation score

### 4.2 Analytics & Reporting (Effort: L)

- [ ] **Project Timeline Visualization**
  - [ ] Gantt chart for RFQ timelines
  - [ ] Milestones: sent, received, awarded
  - [ ] Critical path analysis

- [ ] **Supplier Comparison**
  - [ ] Side-by-side comparison charts
  - [ ] Radar charts for quality dimensions
  - [ ] Ranking tables

- [ ] **RFQ Volume Trends**
  - [ ] Time-series charts (monthly, quarterly, yearly)
  - [ ] Breakdown by project type or department
  - [ ] Forecasting (trend analysis)

- [ ] **Custom Report Builder**
  - [ ] Drag-and-drop interface for custom reports
  - [ ] Filter, group, and aggregate data
  - [ ] Save and share report templates

### 4.3 Feedback Loop (Effort: M)

- [ ] **Project Closure Workflow**
  - [ ] Mark project as complete
  - [ ] Record winning supplier
  - [ ] Collect feedback from project manager

- [ ] **Supplier Recommendation System**
  - [ ] ML model for supplier suggestion based on project type
  - [ ] Historical performance weighting
  - [ ] Bias detection and fairness checks

---

## Phase 5: Cloud & Scalability ☁️

**Priority:** Low
**Timeline:** 2-3 weeks
**Effort:** Medium (M)

**Goal:** Deploy to cloud platforms and optimize for scale.

### 5.1 Cloud Deployment (Effort: M)

- [ ] **AWS Deployment**
  - [ ] ECS/Fargate for container hosting
  - [ ] RDS or DocumentDB for MongoDB
  - [ ] S3 for document storage (optional)
  - [ ] CloudFront for CDN
  - [ ] IAM roles and security groups

- [ ] **Azure Deployment**
  - [ ] Azure Container Instances or App Service
  - [ ] Cosmos DB (MongoDB API)
  - [ ] Azure Blob Storage
  - [ ] Azure Front Door

- [ ] **Google Cloud Deployment**
  - [ ] Cloud Run for containers
  - [ ] Cloud Firestore or MongoDB Atlas
  - [ ] Cloud Storage
  - [ ] Load Balancer

### 5.2 Performance Optimization (Effort: S)

- [ ] **Incremental Scanning**
  - [ ] Track last scan timestamp per folder
  - [ ] Only scan changed/new files
  - [ ] Differential updates to database

- [ ] **Background Job Scheduling**
  - [ ] Celery or similar task queue
  - [ ] Scheduled crawls (cron-style)
  - [ ] Priority queue for on-demand scans

- [ ] **Database Optimization**
  - [ ] Query profiling and optimization
  - [ ] Additional indexes for common queries
  - [ ] Archival strategy for old data

### 5.3 Scalability Features (Effort: S)

- [ ] **Auto-Scaling**
  - [ ] Horizontal scaling for app containers
  - [ ] Load balancing across instances
  - [ ] Health checks and auto-recovery

- [ ] **Caching Layer**
  - [ ] Redis for session storage
  - [ ] Cache frequently accessed data
  - [ ] CDN for static assets

---

## Effort Legend

- **XS (Extra Small):** 1-2 days
- **S (Small):** 3-5 days
- **M (Medium):** 1-2 weeks
- **L (Large):** 3-4 weeks
- **XL (Extra Large):** 5-8 weeks

---

## Dependency Map

```
Phase 0 (Complete) → Phase 1 (Immediate) → Phase 2 (High Priority)
                                        ↘
                                          Phase 3 (Multi-user) → Phase 4 (Analytics)
                                        ↗
Phase 1 (Immediate) ────────────────────→ Phase 5 (Cloud)
```

**Critical Path:** Phase 1 must be completed before any other phases. Phases 2-5 can be developed in parallel once Phase 1 is done, but Phase 3 should precede Phase 4 for full functionality.

---

*This roadmap is a living document and will be updated as priorities shift and new requirements emerge.*
