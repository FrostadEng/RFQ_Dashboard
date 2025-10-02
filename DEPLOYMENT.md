# Docker Deployment Guide for RFQ Dashboard

This guide provides detailed instructions for deploying the RFQ Dashboard using Docker on Windows, with network access and automated scheduling.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Initial Setup](#initial-setup)
3. [Network Deployment](#network-deployment)
4. [Automated Data Refresh with Task Scheduler](#automated-data-refresh-with-task-scheduler)
5. [Container Management](#container-management)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Install Docker Desktop for Windows

1. **Download Docker Desktop:**
   - Visit [https://www.docker.com/products/docker-desktop/](https://www.docker.com/products/docker-desktop/)
   - Click "Download for Windows"

2. **Run the Installer:**
   - Double-click the downloaded `Docker Desktop Installer.exe`
   - Follow the installation wizard
   - **Important:** Enable WSL 2 (Windows Subsystem for Linux) when prompted

3. **Start Docker Desktop:**
   - Launch Docker Desktop from the Start menu
   - Wait for Docker to fully start (icon in system tray will stop animating)
   - You may need to restart your computer

4. **Verify Installation:**
   ```powershell
   docker --version
   docker compose version
   ```

   You should see version numbers for both commands.

### System Requirements

- **Operating System:** Windows 10 64-bit (Pro, Enterprise, or Education) Build 19041 or higher, or Windows 11
- **Hardware:** 4 GB RAM minimum (8 GB recommended)
- **Virtualization:** Must be enabled in BIOS
- **Disk Space:** At least 10 GB free space

---

## Initial Setup

### 1. Clone or Download the Repository

```powershell
git clone <repository-url>
cd RFQ_Dashboard
```

Or download the ZIP file and extract it to a folder.

### 2. Configure the Application

Edit `config.json` to point to your project directory:

```json
{
  "filter_tags": ["Template", "archive"],
  "file_filter_tags": [".db"],
  "mongo_uri": "mongodb://root:example@mongodb:27017/",
  "mongo_db": "rfq_tracker",
  "root_path": "C:\\path\\to\\your\\projects"
}
```

**Important:** Update `root_path` to the actual folder containing your RFQ project directories.

### 3. Update docker-compose.yml Volume Mounts

Open `docker-compose.yml` and update the volume mount to match your project directory:

```yaml
volumes:
  - C:/path/to/your/projects:/app/projects:ro  # Update this path
  - ./config.json:/app/config.json
```

**Note:**
- Use forward slashes `/` instead of backslashes `\` in the path
- Add `:ro` to make the projects folder read-only (recommended)
- The path before the `:` is the host path, after the `:` is the container path

### 4. Build and Start the Containers

```powershell
# Build the Docker images
docker compose build

# Start the containers in detached mode
docker compose up -d
```

### 5. Verify Deployment

```powershell
# Check container status
docker compose ps

# Check logs
docker compose logs app
docker compose logs mongodb
```

Both containers should show status as "Up" and "(healthy)".

### 6. Access the Dashboard

Open your browser to:
```
http://localhost:8501
```

The dashboard will automatically refresh data on first load.

---

## Network Deployment

To make the dashboard accessible to other computers on your office network:

### Step 1: Find Your Computer's IP Address

```powershell
ipconfig
```

Look for "IPv4 Address" under your active network adapter. It typically looks like:
- `192.168.x.x` (most common for home/office networks)
- `10.x.x.x` (some corporate networks)

**Example:** `192.168.1.100`

### Step 2: Configure Windows Firewall

The Docker deployment already binds to `0.0.0.0` (all network interfaces), but Windows Firewall may block incoming connections.

#### Option A: Windows Defender Firewall GUI

1. Open **Windows Defender Firewall with Advanced Security**
   - Press `Win + R`
   - Type `wf.msc` and press Enter

2. **Create Inbound Rule:**
   - Click "Inbound Rules" in the left pane
   - Click "New Rule..." in the right pane
   - Select "Port" → Click Next
   - Select "TCP" and enter `8501` → Click Next
   - Select "Allow the connection" → Click Next
   - Check Domain, Private, and Public → Click Next
   - Name: `Streamlit RFQ Dashboard` → Click Finish

#### Option B: PowerShell (Run as Administrator)

```powershell
New-NetFirewallRule -DisplayName "Streamlit RFQ Dashboard" `
  -Direction Inbound `
  -Action Allow `
  -Protocol TCP `
  -LocalPort 8501
```

### Step 3: Share the URL with Your Team

Team members can access the dashboard by navigating to:
```
http://<your-ip>:8501
```

**Example:** If your IP is `192.168.1.100`, share:
```
http://192.168.1.100:8501
```

### Step 4: Test from Another Computer

- Ensure both computers are on the same network
- Open a browser on a different computer
- Navigate to `http://<your-ip>:8501`
- The dashboard should load normally

---

## Automated Data Refresh with Task Scheduler

Set up automatic data refresh to run daily (e.g., every morning before work).

### Step 1: Locate the PowerShell Script

The repository includes `refresh-rfq-data.ps1` which runs the crawler inside the Docker container.

### Step 2: Test the Script

```powershell
# Navigate to project directory
cd C:\path\to\RFQ_Dashboard

# Run the script
.\refresh-rfq-data.ps1
```

Check the `logs` directory for log files to verify it ran successfully.

### Step 3: Create a Scheduled Task

#### Option A: Task Scheduler GUI

1. **Open Task Scheduler:**
   - Press `Win + R`
   - Type `taskschd.msc` and press Enter

2. **Create a New Task:**
   - Click "Create Task..." (not "Create Basic Task")
   - **General Tab:**
     - Name: `RFQ Dashboard Data Refresh`
     - Description: `Automatically refresh RFQ project data daily`
     - Select "Run whether user is logged on or not"
     - Check "Run with highest privileges"

3. **Triggers Tab:**
   - Click "New..."
   - Begin the task: `On a schedule`
   - Settings: `Daily`
   - Start time: `7:00:00 AM` (adjust to your preference)
   - Click OK

4. **Actions Tab:**
   - Click "New..."
   - Action: `Start a program`
   - Program/script: `powershell.exe`
   - Add arguments: `-ExecutionPolicy Bypass -File "C:\path\to\RFQ_Dashboard\refresh-rfq-data.ps1"`
   - Start in: `C:\path\to\RFQ_Dashboard`
   - Click OK

5. **Conditions Tab:**
   - Uncheck "Start the task only if the computer is on AC power" (optional)
   - Check "Wake the computer to run this task" (optional)

6. **Settings Tab:**
   - Check "Allow task to be run on demand"
   - Check "Run task as soon as possible after a scheduled start is missed"
   - If task is already running: `Do not start a new instance`

7. **Click OK**
   - Enter your Windows password when prompted

#### Option B: PowerShell (Run as Administrator)

```powershell
# Create scheduled task
$action = New-ScheduledTaskAction -Execute "powershell.exe" `
  -Argument "-ExecutionPolicy Bypass -File `"C:\path\to\RFQ_Dashboard\refresh-rfq-data.ps1`"" `
  -WorkingDirectory "C:\path\to\RFQ_Dashboard"

$trigger = New-ScheduledTaskTrigger -Daily -At 7:00AM

$principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" `
  -LogonType S4U -RunLevel Highest

$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries `
  -DontStopIfGoingOnBatteries -StartWhenAvailable

Register-ScheduledTask -TaskName "RFQ Dashboard Data Refresh" `
  -Action $action -Trigger $trigger -Principal $principal -Settings $settings
```

### Step 4: Test the Scheduled Task

1. Open Task Scheduler
2. Find "RFQ Dashboard Data Refresh" in the task list
3. Right-click → "Run"
4. Check the `logs` directory for a new log file

---

## Container Management

### Common Commands

```powershell
# View running containers
docker compose ps

# View logs (all services)
docker compose logs

# View logs (specific service)
docker compose logs app
docker compose logs mongodb

# Follow logs in real-time
docker compose logs -f app

# Stop containers
docker compose down

# Stop and remove volumes (deletes all data!)
docker compose down -v

# Restart containers
docker compose restart

# Rebuild and restart after code changes
docker compose down
docker compose build
docker compose up -d

# Execute command inside running container
docker compose exec app python run_crawler.py

# Access container shell
docker compose exec app /bin/bash
```

### Updating config.json

The `config.json` file is mounted as a volume, so you can edit it without rebuilding:

1. Stop the containers:
   ```powershell
   docker compose down
   ```

2. Edit `config.json`

3. Start the containers:
   ```powershell
   docker compose up -d
   ```

### Updating Application Code

If you modify Python code in `streamlit_dashboard.py`, `run_crawler.py`, or the `rfq_tracker` module:

```powershell
docker compose down
docker compose build app
docker compose up -d
```

### Data Backup

MongoDB data is stored in a Docker volume named `rfq_dashboard_mongodb_data`.

**Backup:**
```powershell
docker compose exec mongodb mongodump --out /data/backup
docker compose cp mongodb:/data/backup ./backup
```

**Restore:**
```powershell
docker compose cp ./backup mongodb:/data/backup
docker compose exec mongodb mongorestore /data/backup
```

---

## Troubleshooting

### Containers Won't Start

**Check Docker Desktop is Running:**
- Look for the Docker icon in your system tray
- If not running, start Docker Desktop and wait for it to fully initialize

**Check Container Logs:**
```powershell
docker compose logs
```

**Common Issues:**
- Port 8501 already in use: Stop other applications using this port
- MongoDB failed to start: Check if MongoDB port 27017 is available

### Dashboard Not Accessible from Network

1. **Verify Firewall Rule Exists:**
   ```powershell
   Get-NetFirewallRule -DisplayName "Streamlit RFQ Dashboard"
   ```

2. **Check Container is Listening on All Interfaces:**
   ```powershell
   docker compose logs app | Select-String "0.0.0.0"
   ```
   Should show: `URL: http://0.0.0.0:8501`

3. **Verify Network Connectivity:**
   - From another computer, ping your server: `ping <your-ip>`
   - If ping fails, check network settings and ensure both computers are on the same network

4. **Test Locally First:**
   - On the server computer, try `http://localhost:8501`
   - If this works but network access doesn't, it's a firewall/network issue

### Data Not Refreshing

**Check Crawler Logs:**
```powershell
docker compose exec app python run_crawler.py
```

**Verify Volume Mount:**
```powershell
docker compose exec app ls -la /app/projects
```

Should show your project files. If empty, check volume mount in `docker-compose.yml`.

**Check config.json:**
```powershell
docker compose exec app cat /app/config.json
```

Verify `root_path` is set correctly.

### Scheduled Task Not Running

1. **Open Task Scheduler**
2. **Find your task** in the list
3. **Check "Last Run Result"**
   - `0x0`: Success
   - Other codes: Error occurred

4. **View Task History:**
   - Right-click task → "Properties"
   - "History" tab → Check for errors

5. **Check Log Files:**
   ```powershell
   Get-Content .\logs\refresh-*.log | Select-Object -Last 50
   ```

6. **Common Issues:**
   - Docker not running: Ensure Docker Desktop starts with Windows
   - Wrong path: Verify paths in Task Scheduler action
   - Permissions: Task must run with highest privileges

### Reset Everything

If you need to start fresh:

```powershell
# Stop and remove all containers and volumes
docker compose down -v

# Remove images
docker compose down --rmi all

# Rebuild from scratch
docker compose build --no-cache
docker compose up -d
```

**Warning:** This deletes all MongoDB data!

---

## Additional Resources

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Docker Desktop for Windows](https://docs.docker.com/desktop/install/windows-install/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [MongoDB Docker Image](https://hub.docker.com/_/mongo)

For more help, check the main [README.md](README.md) or the [Troubleshooting Guide](TROUBLESHOOTING.md).
