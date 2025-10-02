# Project RFQ Tracker

Project RFQ Tracker is a web-based application designed to scan a file system for project-related RFQ (Request for Quotation) documents, extract metadata, and display it in an easy-to-use dashboard accessible from any browser on your local network. It consists of a Python-based file crawler and a Streamlit web interface.

> **Note:** The legacy PyQt6 desktop version is still available via `run_dashboard.py`, but the recommended interface is the new Streamlit web dashboard.

## Features

- **Automated Metadata Extraction:** The backend crawler scans project directories to find supplier transmissions and submissions.
- **Data Persistence:** All extracted metadata is stored in a local MongoDB database, ensuring data is saved between sessions.
- **Web-Based Dashboard:** A clean, modern user interface built with Streamlit, accessible from any browser on your local network.
- **Network Accessibility:** Install on one work computer and access from any workstation via `http://<server-ip>:8501`.
- **Real-Time Search and Filtering:** Instantly find projects using the built-in search bar.
- **Flexible Sorting:** Sort projects by number or last scanned date.
- **Configurable:** Key settings, such as the root directory to scan and database connection details, are managed in a simple `config.json` file.
- **Modular Codebase:** The project is organized into separate packages for the backend crawler (`rfq_tracker`) and the frontend UI, making it easy to maintain and extend.

## Getting Started

There are two deployment methods: **Docker (Recommended)** and **Manual Installation**. Docker provides the easiest setup with zero MongoDB configuration.

### Quick Start with Docker (Recommended)

#### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) for Windows/Mac/Linux

#### Deployment Steps

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd RFQ_Dashboard
   ```

2. **Configure the application:**
   - Edit `config.json` to set `root_path` to your project directory

3. **Start the application:**
   ```bash
   docker compose up -d
   ```

4. **Access the dashboard:**
   - Open your browser to `http://localhost:8501`
   - Data is automatically refreshed on first load
   - Use the refresh button in the sidebar to manually update data

5. **Stop the application:**
   ```bash
   docker compose down
   ```

**Network Access:** The Docker deployment is automatically configured for network access. Team members can access the dashboard at `http://<your-ip>:8501`.

**Data Persistence:** MongoDB data persists in a Docker volume. To reset data, run `docker compose down -v`.

For detailed Docker deployment instructions, Windows firewall configuration, and Task Scheduler setup, see [DEPLOYMENT.md](DEPLOYMENT.md).

---

### Manual Installation (Alternative)

#### 1. Prerequisites

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

#### 2. Installation

1.  **Clone the repository** (or download the source code).
2.  **Navigate to the project's root directory** in your terminal.
3.  **Install the required Python packages:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Configure the application:**
    - Rename `config.example.json` to `config.json` (if applicable).
    - Edit `config.json` to set the `root_path` to the directory you want to scan.

#### 3. Running the Application

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

**Window 3: Launch the Web Dashboard**

Once the database is running, you can start the web interface.
```powershell
streamlit run streamlit_dashboard.py
```

The dashboard will start and display a URL. By default, it's accessible at `http://localhost:8501` on the server computer.

#### 4. Network Access (Team Collaboration)

To make the dashboard accessible to your entire team on the local network:

**Step 1: Find Your Server Computer's IP Address**

On the computer running the dashboard:

- **Windows:** Open Command Prompt and run:
  ```cmd
  ipconfig
  ```
  Look for "IPv4 Address" under your active network adapter (usually starts with `192.168.x.x` or `10.x.x.x`)

- **Linux:** Open Terminal and run:
  ```bash
  ip addr show
  ```
  Look for `inet` address under your active network interface

**Step 2: Configure Firewall (Windows)**

Allow incoming connections on port 8501:

1. Open Windows Defender Firewall with Advanced Security
2. Click "Inbound Rules" → "New Rule"
3. Select "Port" → Click Next
4. Select "TCP" and enter port `8501` → Click Next
5. Select "Allow the connection" → Click Next
6. Apply to Domain, Private, and Public → Click Next
7. Name it "Streamlit RFQ Dashboard" → Click Finish

**Linux (UFW):**
```bash
sudo ufw allow 8501
```

**Step 3: Start Dashboard with Network Access**

The dashboard is already configured to bind to all network interfaces (see `.streamlit/config.toml`). Simply run:

```powershell
streamlit run streamlit_dashboard.py
```

**Step 4: Share the URL with Your Team**

Team members can access the dashboard by navigating to:
```
http://<server-ip>:8501
```

Replace `<server-ip>` with the IP address you found in Step 1 (e.g., `http://192.168.1.100:8501`).

**Example:**
- Server computer IP: `192.168.1.100`
- Team access URL: `http://192.168.1.100:8501`

**Troubleshooting Network Access:**
- Verify both computers are on the same network
- Check firewall settings on the server computer
- Ensure MongoDB and Streamlit are both running on the server
- Try accessing `http://localhost:8501` from the server computer first to verify it works locally

#### 5. Legacy Desktop Application

The original PyQt6 desktop application is still available:
```powershell
python run_dashboard.py
```

This runs locally on your machine and does not require network configuration.

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

<img width="1078" height="998" alt="image" src="https://github.com/user-attachments/assets/6fae186e-cf37-4cd6-9802-255d1bdddf1f" />
