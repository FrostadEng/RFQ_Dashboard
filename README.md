# Project RFQ Tracker

Project RFQ Tracker is a desktop application designed to scan a file system for project-related RFQ (Request for Quotation) documents, extract metadata, and display it in an easy-to-use dashboard. It consists of a Python-based file crawler and a PyQt6 graphical user interface.

![Dashboard Screenshot](image.png)

## Features

- **Automated Metadata Extraction:** The backend crawler scans project directories to find supplier transmissions and submissions.
- **Data Persistence:** All extracted metadata is stored in a local MongoDB database, ensuring data is saved between sessions.
- **Interactive Dashboard:** A clean, modern user interface built with PyQt6 allows for easy visualization and navigation of the project data.
- **Search and Filtering:** Quickly find projects using the built-in search bar in the project list.
- **Direct File Access:** Clickable links within the dashboard open the relevant file or folder directly in your system's file explorer.
- **Configurable:** Key settings, such as the root directory to scan and database connection details, are managed in a simple `config.json` file.
- **Modular Codebase:** The project is organized into separate packages for the backend crawler (`rfq_tracker`) and the frontend UI (`dashboard`), making it easy to maintain and extend.

## Getting Started

Follow these instructions to get the RFQ Tracker running on your local machine.

### 1. Prerequisites

Ensure you have the following system dependencies installed.

**For Debian/Ubuntu-based systems:**
```bash
sudo apt-get update
sudo apt-get install -y python3 python3-pip libxcb-xinerama0 libxcb-cursor0
```

**For other systems (e.g., Windows, macOS):**
- [Python 3.8+](https://www.python.org/downloads/)
- A local or portable version of [MongoDB](https://www.mongodb.com/try/download/community).

### 2. Installation

1.  **Clone the repository** (or download the source code).
2.  **Navigate to the project's root directory** in your terminal.
3.  **Install the required Python packages:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Configure the application:**
    - Rename `config.example.json` to `config.json` (if applicable).
    - Edit `config.json` to set the `root_path` to the directory you want to scan.

### 3. Running the Application

You will need to run two or three processes, ideally in separate terminal windows.

**Terminal 1: Start the MongoDB Database**

If you are using a system-installed version of MongoDB, ensure the service is running:
```bash
sudo systemctl start mongod
```

If you are using a portable version of MongoDB (e.g., in a `vendor/` directory):
```bash
# Create a directory to store database files
mkdir -p data

# Start the server
# (Adjust the path to your mongod executable)
./vendor/mongodb/bin/mongod --dbpath ./data
```

**Terminal 2: Run the Crawler**

This step scans the folders and populates the database. You only need to run this when you want to update the data.
```bash
python3 run_crawler.py
```

**Terminal 3: Launch the Dashboard**

Once the database is running, you can start the user interface.
```bash
python3 run_dashboard.py
```

The application window should now appear on your screen.

## Configuration

All runtime settings are managed in the `config.json` file:

```json
{
  "filter_tags": ["Template", "archive"],
  "file_filter_tags": [".db"],
  "mongo_uri": "mongodb://localhost:27017",
  "mongo_db": "rfq_tracker",
  "root_path": "mock_projects"
}
```

- `filter_tags`: A list of case-insensitive strings. Any folder containing one of these strings will be skipped by the crawler.
- `file_filter_tags`: A list of file extensions. Any file with one of these extensions will be ignored.
- `mongo_uri`: The connection string for your MongoDB instance.
- `mongo_db`: The name of the database to use.
- `root_path`: The absolute or relative path to the root directory containing your project folders. The included `mock_projects` can be used for testing.