# Project RFQ Tracker - Technology Stack

## Overview

This document defines the complete technology stack for the Project RFQ Tracker application, including both the current implementation and the planned migration to a containerized web-based architecture.

---

## 1. Programming Language & Runtime

### Primary Language: **Python 3.8+**
- **Rationale:** Python provides excellent libraries for file system operations (`pathlib`), database connectivity (`pymongo`), and rapid web development (`Streamlit`).
- **Current Version:** Python 3.12 (detected in virtual environment)
- **Virtual Environment:** `.venv/` for dependency isolation

---

## 2. Backend Architecture

### Core Application Logic
- **Package Structure:**
  - `rfq_tracker/` - Backend crawler and database operations
    - `crawler.py` - File system scanning and metadata extraction
    - `db_manager.py` - MongoDB connection and data persistence
  - `dashboard/` - Frontend UI components (transitioning from PyQt6 to Streamlit)

### Key Backend Features
- **File System Crawler:**
  - Recursive directory scanning using `pathlib`
  - Configurable folder/file filtering via `config.json`
  - Metadata extraction (project numbers, supplier names, file paths, timestamps)
  - Efficient pattern matching for RFQ folder structures

- **Database Layer:**
  - MongoDB connection management
  - Upsert strategy for incremental updates
  - Index creation for optimized queries
  - Bulk write operations for performance

---

## 3. Database

### Primary Database: **MongoDB**

**Current Setup:**
- **Version:** MongoDB Community Server (local installation)
- **Connection:** `mongodb://localhost:27017`
- **Database Name:** `rfq_tracker`
- **Driver:** `pymongo[srv]` (Python MongoDB driver)

**Schema Design:**
- **Collections:**
  - `projects` - Project-level metadata (project_number, path, last_scanned)
  - `suppliers` - Supplier information per project
  - `transmissions` - Sent RFQ packages (ZIP files, source files, dates)
  - `receipts` - Received supplier submissions (folders, files, dates)

**Indexing Strategy:**
- Unique index on `projects.project_number`
- Compound unique index on `suppliers.[project_number, supplier_name]`
- Unique index on `transmissions.zip_path`
- Unique index on `receipts.received_folder_path`

**Planned Migration:**
- **Deployment:** MongoDB container via Docker Compose
- **Volume Persistence:** Docker volume for database files
- **Configuration:** Environment-based connection strings

---

## 4. Frontend UI

### Current: **PyQt6 Desktop Application**
- **Status:** Fully functional desktop GUI
- **Key Components:**
  - `main_window.py` - Main application window with sidebar and content area
  - `widgets/collapsible_widget.py` - Collapsible supplier sections
  - `widgets/link_label.py` - Clickable file/folder links
- **Styling:** Dark theme with custom CSS-like stylesheets
- **Features:** Search, filtering, project list, supplier details

### Target: **Streamlit Web Application**
- **Framework:** Streamlit (Python web framework)
- **Rationale:**
  - Browser-based access (no desktop installation required)
  - Rapid development with Python-native syntax
  - Built-in responsive design
  - Easy deployment with Docker
  - Real-time updates and interactivity

**Planned Streamlit Features:**
- Project search and filtering
- Sidebar navigation
- Expandable supplier sections
- File download links
- Export functionality (CSV, Excel, PDF)
- Future: File preview for PDFs and images

---

## 5. Deployment & Infrastructure

### Current: **Local Desktop Deployment**
- Python script execution (`run_crawler.py`, `run_dashboard.py`)
- Manual MongoDB service management
- Windows/Linux compatible

### Target: **Docker Containerization**

**Architecture:**
```
┌─────────────────────────────────────┐
│         Docker Compose              │
│                                     │
│  ┌─────────────┐  ┌──────────────┐ │
│  │  Streamlit  │  │   MongoDB    │ │
│  │     App     │←→│  Container   │ │
│  │  Container  │  │              │ │
│  └─────────────┘  └──────────────┘ │
│        ↓                 ↓          │
│  ┌─────────────┐  ┌──────────────┐ │
│  │  App Port   │  │ Data Volume  │ │
│  │   :8501     │  │  /data/db    │ │
│  └─────────────┘  └──────────────┘ │
└─────────────────────────────────────┘
```

**Docker Components:**
1. **Streamlit App Container:**
   - Base image: `python:3.12-slim`
   - Install dependencies from `requirements.txt`
   - Expose port 8501 for web access
   - Mount configuration and log directories

2. **MongoDB Container:**
   - Official MongoDB image
   - Data persistence via Docker volume
   - Health checks for reliability
   - Network isolation with app container

3. **Docker Compose:**
   - Service orchestration
   - Network configuration
   - Volume management
   - Environment variable injection

**Benefits:**
- One-command deployment (`docker-compose up`)
- Consistent environment across machines
- Easy updates and rollbacks
- Scalable architecture (can add Redis cache, background workers, etc.)

---

## 6. Configuration Management

### Current: **config.json**
```json
{
  "filter_tags": ["Template", "archive"],
  "file_filter_tags": [".db"],
  "mongo_uri": "mongodb://localhost:27017",
  "mongo_db": "rfq_tracker",
  "root_path": "mock_projects"
}
```

### Planned Enhancements:
- **Environment Variables:** Use `.env` files for Docker deployments
- **Configurable Folder Patterns:** Define RFQ folder structure in config
- **Multi-Environment Support:** Separate configs for dev/staging/production
- **Validation:** Schema validation for configuration files

---

## 7. Dependencies

### Current Dependencies (`requirements.txt`)
```
pymongo[srv]  # MongoDB driver
PyQt6         # Desktop GUI (to be replaced)
```

### Planned Dependencies
```
pymongo[srv]>=4.0        # MongoDB driver
streamlit>=1.28          # Web UI framework
python-dotenv>=1.0       # Environment variable management
pandas>=2.0              # Data export (CSV/Excel)
openpyxl>=3.1           # Excel file generation
plotly>=5.0             # Future analytics/charts
```

### Development Dependencies (Future)
```
pytest>=7.4             # Testing framework
black>=23.0             # Code formatting
flake8>=6.0            # Linting
mypy>=1.5              # Type checking
```

---

## 8. Development & Testing

### Current Setup:
- Manual testing via desktop application
- Mock project data in `mock_projects/` directory
- Logging framework for debugging

### Planned Testing Strategy:
- **Unit Tests:** `pytest` for crawler and database logic
- **Integration Tests:** End-to-end tests for full crawl → display workflow
- **UI Tests:** Streamlit testing framework for dashboard interactions
- **Test Data:** Fixture-based mock project structures

---

## 9. Logging & Monitoring

### Current:
- Python `logging` module
- Console output for crawler and dashboard
- Configurable log levels

### Planned:
- **Structured Logging:** JSON-formatted logs for parsing
- **Log Aggregation:** Centralized logging in Docker (stdout/stderr → log files)
- **Monitoring:** Health check endpoints for container orchestration
- **Metrics:** Track crawl duration, document counts, error rates

---

## 10. Security Considerations

### Current:
- Local-only access (no network exposure)
- No authentication required

### Planned:
- **Network Isolation:** Docker network for app ↔ database communication
- **Authentication:** Streamlit authentication for web access (Phase 3)
- **Environment Variables:** Secure credential management (no hardcoded passwords)
- **File Access:** Read-only mounting of project directories

---

## 11. Future Enhancements

### Phase 3+: Cloud Migration
- **Cloud Platforms:** AWS, Azure, or Google Cloud deployment
- **Cloud Storage:** S3/Azure Blob for long-term document archival
- **Managed Database:** MongoDB Atlas for cloud-hosted database
- **Auto-Scaling:** Elastic container instances for high load
- **CDN:** CloudFront/Azure CDN for static asset delivery

### Phase 4: Analytics
- **Visualization:** Plotly/Dash for interactive charts
- **Data Warehouse:** Future integration with BigQuery/Redshift for historical analysis
- **ML Models:** Supplier recommendation system using scikit-learn

---

## Technology Decision Log

| Decision | Rationale | Date |
|----------|-----------|------|
| Python as primary language | Strong ecosystem for file I/O, databases, and web frameworks | Initial |
| MongoDB over SQL | Flexible schema for varying RFQ structures, fast document queries | Initial |
| PyQt6 for prototype | Rapid desktop GUI development to validate concept | Initial |
| Streamlit for production | Browser-based access, easier deployment, broader user reach | Current |
| Docker for deployment | Solve deployment issues, ensure consistency, enable cloud migration | Current |

---

## Tech Stack Summary

| Layer | Current | Target |
|-------|---------|--------|
| **Language** | Python 3.12 | Python 3.12 |
| **Backend** | Custom crawler + pymongo | Custom crawler + pymongo |
| **Database** | MongoDB (local) | MongoDB (Docker) |
| **Frontend** | PyQt6 Desktop | Streamlit Web |
| **Deployment** | Manual scripts | Docker Compose |
| **Config** | config.json | config.json + .env |
| **Testing** | Manual | pytest + fixtures |

---

*This technology stack is designed to balance rapid development, ease of deployment, and future scalability while solving the immediate business need for accessible RFQ document tracking.*
