# Project RFQ Tracker

Project RFQ Tracker is a desktop application designed to scan a file system for project-related RFQ (Request for Quotation) documents, extract metadata, and display it in an easy-to-use dashboard. It consists of a Python-based file crawler and a PyQt6 graphical user interface.

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

#### For Windows 11

1.  **Python:** Install [Python 3.8+](https://www.python.org/downloads/windows/) from the official website. Make sure to check the box that says "Add Python to PATH" during installation.
2.  **MongoDB:** Download and install [MongoDB Community Server](https://www.mongodb.com/try/download/community) using the MSI installer. Alternatively, you can use a [portable .zip version](https://www.mongodb.com/try/download/community) if you prefer not to install it system-wide.
3.  **Git:** Install [Git for Windows](https://git-scm.com/download/win) to clone the repository.

#### For Linux (Debian/Ubuntu)

1.  **Python & System Libraries:**
    ```bash
    sudo apt-get update
    sudo apt-get install -y python3 python3-pip libxcb-xinerama0 libxcb-cursor0
    ```
2.  **MongoDB:** Follow the official guide to [install MongoDB on Ubuntu](httpshttps://www.mongodb.com/docs/manual/tutorial/install-mongodb-on-ubuntu/).

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

You will need to run two or three processes, ideally in separate **Command Prompt** or **PowerShell** windows.

**Window 1: Start the MongoDB Database**

If you installed MongoDB using the MSI installer, the database server should be running automatically as a Windows service. You can verify this by opening the "Services" app and looking for "MongoDB Server".

If you are using a portable version (e.g., in a `vendor/` directory):
```powershell
# Create a directory to store database files
mkdir data -Force

# Start the server
# (Adjust the path to your mongod.exe executable)
.\vendor\mongodb\bin\mongod.exe --dbpath .\data
```

**Window 2: Run the Crawler**

This step scans the folders and populates the database. You only need to run this when you want to update the data.
```powershell
python run_crawler.py
```

**Window 3: Launch the Dashboard**

Once the database is running, you can start the user interface.
```powershell
python run_dashboard.py
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

## Application Flow

The following diagram illustrates the general workflow of the application, from running the crawler to interacting with the dashboard.

<img width="1078" height="998" alt="image" src="https://github.com/user-attachments/assets/724ae04d-9115-4677-9568-b3d546192736" />
