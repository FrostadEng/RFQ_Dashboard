# Project RFQ Tracker - Mission (Lite)

> **Condensed product mission optimized for AI context efficiency**

---

## Product Essence

**Project RFQ Tracker** automates the tracking and management of Request for Quotation (RFQ) documents scattered across complex server folder structures. It crawls file systems to extract metadata (projects, suppliers, transmissions, receipts) into MongoDB, then presents it via a web dashboard for instant searchable access.

**Target Users:** Project managers, procurement teams, and engineering staff who need quick access to RFQ documents without manual folder navigation.

**Core Value:** Reduces document location time from 10-30 minutes to <30 seconds, improves project oversight, and enables web-based access for remote teams.

---

## Key Problems Solved

1. **Manual Document Location** - Automated crawler replaces manual folder navigation
2. **Scattered Information** - Unified dashboard shows all suppliers and documents per project
3. **Limited Accessibility** - Web interface (Streamlit) replaces desktop-only access
4. **No Historical Tracking** - Database stores timestamps for compliance and quality tracking

---

## Current State

**Phase 0: Desktop Version (Complete)**
- ✅ File system crawler with metadata extraction
- ✅ MongoDB with proper schema and indexing
- ✅ PyQt6 desktop GUI with search, filtering, clickable file links
- ✅ Configurable folder/file filtering via JSON

**Deployment Challenge:** Desktop app requires local MongoDB and doesn't support browser access.

---

## Immediate Priority: Web Migration

**Phase 1: Containerization & Streamlit (In Progress)**
- Migrate PyQt6 → Streamlit web UI
- Dockerize entire stack (app + MongoDB)
- Make folder structure fully configurable
- Deploy for browser-based team access

---

## Future Roadmap

- **Phase 2:** Advanced filtering/sorting, export (CSV/Excel), file preview
- **Phase 3:** Multi-user authentication, email notifications
- **Phase 4:** Supplier quality analytics, performance tracking dashboard
- **Phase 5:** Cloud deployment (AWS/Azure), auto-scaling

---

## Tech Stack

| Layer | Current | Target |
|-------|---------|--------|
| Language | Python 3.12 | Python 3.12 |
| Backend | Custom crawler + pymongo | Same |
| Database | MongoDB (local) | MongoDB (Docker) |
| Frontend | PyQt6 Desktop | **Streamlit Web** |
| Deployment | Manual scripts | **Docker Compose** |

---

## Differentiators

1. **Purpose-built for RFQ workflows** (projects → suppliers → sent/received pattern)
2. **Zero user configuration** (auto-discovery via folder naming)
3. **Hybrid approach** (file system + database)
4. **Direct file access** (clickable links to native applications)
5. **Docker-native** (trivial deployment for IT staff)

---

## Folder Structure Pattern

```
/Projects/
  ├─ 80123/                  # Project folder (numeric)
  │   ├─ RFQ/                # RFQ folder
  │   │   ├─ Supplier A/     # Supplier folder
  │   │   │   ├─ Sent/       # Transmissions (ZIP files)
  │   │   │   └─ Received/   # Receipts (submission folders)
  │   │   └─ Supplier B/
  │   └─ ...
  └─ 80124/
```

Crawler extracts:
- Project numbers (folder names)
- Supplier names
- Sent ZIP files with creation dates
- Received folders with file inventories

---

## Configuration

**config.json:**
```json
{
  "root_path": "/path/to/Projects",
  "filter_tags": ["Template", "archive"],
  "file_filter_tags": [".db"],
  "mongo_uri": "mongodb://localhost:27017",
  "mongo_db": "rfq_tracker"
}
```

**Planned:** Environment variables for Docker, configurable RFQ folder patterns.

---

*This condensed mission provides AI agents with essential product context while minimizing token usage.*
