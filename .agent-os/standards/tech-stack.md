# RFQ Tracker: Technology Stack

This document outlines the technology stack for the Project RFQ Tracker application.

## 1. Backend

- **Language:** Python 3.12
- **Core Logic:** The backend consists of a crawler script responsible for scanning the file system, extracting metadata from project folders, and storing it in the database. The main logic is contained within the `rfq_tracker` package.
- **Database Connector:** `pymongo[srv]` is used as the client library to interact with the MongoDB database.
- **Virtual Environment:** `.venv/` for dependency isolation

## 2. Frontend

- **Current:** PyQt6 (desktop application)
- **Target:** Streamlit (web-based dashboard)
- **Description:** The user interface is transitioning from PyQt6 desktop to a web-based dashboard built using Streamlit. This will provide browser-based access for the entire team, solving deployment challenges and enabling remote access.

## 3. Database

- **System:** MongoDB
- **Current Setup:** Local MongoDB instance (`mongodb://localhost:27017`)
- **Target Setup:** Dockerized MongoDB container for portability
- **Schema:** Collections for projects, suppliers, transmissions, and receipts with proper indexing
- **Description:** A NoSQL database used to persist all metadata extracted by the crawler. The database will be configured to run in a Docker container, making the entire application portable and easy to deploy.

## 4. Deployment

- **Current:** Manual Python script execution with local MongoDB
- **Target:** Docker + Docker Compose for containerized deployment
- **Components:**
  - Streamlit app container
  - MongoDB container
  - Volume persistence for database
  - Network configuration for inter-container communication

## 5. Configuration & Execution

- **Configuration:** Application settings, such as database URI, file paths to scan, and directory/file filters, are managed in a `config.json` file.
- **Planned:** Environment variable support via `.env` files for Docker deployments
- **Execution:** The application will have two main entry points:
    - `run_crawler.py`: To execute the file system scan and populate the database.
    - `run_dashboard.py`: To launch the user interface (currently PyQt6, migrating to Streamlit).

## 6. Dependencies

**Current (`requirements.txt`):**
- **`pymongo[srv]`**: For MongoDB connectivity
- **`PyQt6`**: For desktop GUI (to be replaced)

**Planned:**
- **`streamlit`**: For web application GUI
- **`python-dotenv`**: For environment variable management
- **`pandas`**: For data export functionality
- **`openpyxl`**: For Excel export

## 7. Code Structure

- `rfq_tracker/` - Backend package
  - `crawler.py` - File system scanning and metadata extraction
  - `db_manager.py` - MongoDB operations and schema management
- `dashboard/` - Frontend package
  - `main_window.py` - PyQt6 main window (current)
  - `widgets/` - Custom UI components
- `run_crawler.py` - Crawler entry point
- `run_dashboard.py` - Dashboard entry point
- `config.json` - Application configuration

For detailed technology information, see `.agent-os/product/tech-stack.md`.