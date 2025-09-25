# Project RFQ Tracker

Project RFQ Tracker is a desktop application designed to scan a file system for project-related RFQ (Request for Quotation) documents, extract metadata, and display it in an easy-to-use dashboard. It is a self-contained application that manages its own database and dependencies.

## Features

- **Automated Metadata Extraction:** The backend crawler scans project directories to find supplier transmissions and submissions.
- **Data Persistence:** All extracted metadata is stored in a local, portable MongoDB database, ensuring data is saved between sessions.
- **Interactive Dashboard:** A clean, modern user interface built with PyQt6 allows for easy visualization and navigation of the project data.
- **One-Click Scanning:** A "Scan Files" button in the UI triggers the crawler, eliminating the need for separate command-line operations.
- **Search and Filtering:** Quickly find projects using the built-in search bar in the project list.
- **Direct File Access:** Clickable links within the dashboard open the relevant file or folder directly in your system's file explorer.
- **Configurable:** Key settings, such as the root directory to scan and database connection details, are managed in a simple `config.json` file.
- **Standalone Application:** The application can be run with a single click, and it will automatically download and manage its own database engine (MongoDB).

## Getting Started

Follow these instructions to get the RFQ Tracker running on your local machine.

### Prerequisites

- **Python:** Install [Python 3.8+](https://www.python.org/downloads/windows/) from the official website. Make sure to check the box that says "Add Python to PATH" during installation.
- **Git:** Install [Git for Windows](https://git-scm.com/download/win) to clone the repository.

### Installation

1.  **Clone the repository** (or download the source code).
2.  **Navigate to the project's root directory** in your terminal.
3.  **Install the required Python packages:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Configure the application:**
    - Edit `config.json` to set the `root_path` to the directory you want to scan. The included `mock_projects` can be used for testing.

### Running the Application

Once the dependencies are installed, you can run the application with a single command:

```bash
python main.py
```

The first time you run the application, it will download a portable version of MongoDB, which may take a few minutes. This is a one-time setup. The application window should then appear on your screen.

## Building a Distributable Version

You can create a standalone, distributable version of the application that can be run on other Windows machines without needing to install Python or any dependencies.

1.  **Install PyInstaller:**
    ```bash
    pip install pyinstaller
    ```
2.  **Run the build script:**
    ```bash
    python build.py
    ```
3.  **Find the application:**
    - The bundled application will be located in the `dist/RFQ-Tracker` directory. You can zip this directory and share it with others.

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
- `mongo_uri`: The connection string for your MongoDB instance. This should be left as the default unless you are using your own MongoDB server.
- `mongo_db`: The name of the database to use.
- `root_path`: The absolute or relative path to the root directory containing your project folders.