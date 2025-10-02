# Troubleshooting Guide

This guide covers common issues and their solutions for the RFQ Dashboard Docker deployment.

## Table of Contents

1. [Docker Issues](#docker-issues)
2. [Container Issues](#container-issues)
3. [Network Access Issues](#network-access-issues)
4. [Database Issues](#database-issues)
5. [Volume Mount Issues](#volume-mount-issues)
6. [Performance Issues](#performance-issues)
7. [Crawler Issues](#crawler-issues)
8. [Scheduled Task Issues](#scheduled-task-issues)

---

## Docker Issues

### Docker Desktop Not Starting

**Symptoms:**
- Docker icon in system tray shows error
- Commands hang or show "Docker daemon not running"

**Solutions:**

1. **Restart Docker Desktop:**
   - Right-click Docker icon → "Quit Docker Desktop"
   - Start Docker Desktop again from Start menu
   - Wait 1-2 minutes for full startup

2. **Check WSL 2:**
   ```powershell
   wsl --status
   ```
   If WSL is not installed:
   ```powershell
   wsl --install
   ```

3. **Reset Docker to Factory Defaults:**
   - Open Docker Desktop Settings
   - Troubleshoot → "Reset to factory defaults"
   - **Warning:** This removes all containers and images

4. **Check System Requirements:**
   - Virtualization must be enabled in BIOS
   - Windows 10 Pro/Enterprise or Windows 11
   - At least 4 GB RAM

### "docker compose: command not found"

**Solutions:**

1. **Use `docker compose` (with space):**
   ```powershell
   docker compose up -d
   ```
   Not `docker-compose` (with hyphen)

2. **Verify Docker Desktop includes Compose:**
   ```powershell
   docker compose version
   ```

---

## Container Issues

### Containers Won't Start

**Check Status:**
```powershell
docker compose ps
docker compose logs
```

**Common Issues:**

#### Port Already in Use

**Symptoms:**
```
Error: bind 0.0.0.0:8501 failed: port is already allocated
```

**Solutions:**

1. **Find what's using the port:**
   ```powershell
   netstat -ano | findstr :8501
   ```

2. **Stop the conflicting process:**
   - Note the PID from netstat output
   - Open Task Manager → Details tab
   - Find process by PID and end it

3. **Change the port in docker-compose.yml:**
   ```yaml
   ports:
     - "8502:8501"  # Use port 8502 on host
   ```

#### MongoDB Won't Start

**Symptoms:**
```
mongodb container exited with code 1
```

**Solutions:**

1. **Check MongoDB logs:**
   ```powershell
   docker compose logs mongodb
   ```

2. **Reset MongoDB data:**
   ```powershell
   docker compose down -v
   docker compose up -d
   ```
   **Warning:** This deletes all data!

3. **Check disk space:**
   ```powershell
   docker system df
   ```

### Container Keeps Restarting

**Check logs:**
```powershell
docker compose logs --tail=100 app
```

**Common Causes:**

1. **Application Error:**
   - Look for Python tracebacks in logs
   - Check config.json syntax

2. **Missing Dependencies:**
   ```powershell
   docker compose build --no-cache app
   docker compose up -d
   ```

3. **Health Check Failing:**
   - Check if Streamlit is starting correctly
   - Temporarily disable health check in docker-compose.yml for testing

---

## Network Access Issues

### Dashboard Works Locally But Not on Network

**Step-by-Step Diagnosis:**

1. **Verify Local Access Works:**
   ```
   http://localhost:8501
   ```

2. **Find Your IP Address:**
   ```powershell
   ipconfig
   ```

3. **Test from Server Computer:**
   ```
   http://<your-ip>:8501
   ```

4. **Check Firewall Rule:**
   ```powershell
   Get-NetFirewallRule -DisplayName "Streamlit RFQ Dashboard"
   ```

   If not found, create it:
   ```powershell
   New-NetFirewallRule -DisplayName "Streamlit RFQ Dashboard" `
     -Direction Inbound `
     -Action Allow `
     -Protocol TCP `
     -LocalPort 8501
   ```

5. **Verify Container Binds to 0.0.0.0:**
   ```powershell
   docker compose logs app | Select-String "0.0.0.0"
   ```

   Should show:
   ```
   URL: http://0.0.0.0:8501
   ```

6. **Test Network Connectivity:**
   From another computer:
   ```powershell
   ping <server-ip>
   telnet <server-ip> 8501
   ```

7. **Check Network Profile:**
   - Windows Settings → Network & Internet
   - Ensure network is set to "Private" not "Public"

### Firewall Keeps Blocking Connection

**Symptoms:**
- Firewall rule exists but still can't connect
- Windows Security shows repeated blocks

**Solutions:**

1. **Check All Firewall Profiles:**
   ```powershell
   Get-NetFirewallRule -DisplayName "Streamlit RFQ Dashboard" | Format-List *
   ```

2. **Create Rule for All Profiles:**
   ```powershell
   New-NetFirewallRule -DisplayName "Streamlit RFQ Dashboard" `
     -Direction Inbound `
     -Action Allow `
     -Protocol TCP `
     -LocalPort 8501 `
     -Profile Domain,Private,Public
   ```

3. **Check Windows Defender Settings:**
   - Windows Security → Firewall & network protection
   - Allow an app through firewall
   - Verify rule is enabled for all network types

---

## Database Issues

### MongoDB Connection Failed

**Symptoms:**
```
Failed to connect to MongoDB
ConnectionFailure
```

**Solutions:**

1. **Check MongoDB Container:**
   ```powershell
   docker compose ps mongodb
   ```

   Should show "Up" and "(healthy)"

2. **Check MongoDB Logs:**
   ```powershell
   docker compose logs mongodb
   ```

3. **Verify Network:**
   ```powershell
   docker compose exec app ping mongodb
   ```

4. **Check Environment Variables:**
   ```powershell
   docker compose exec app env | findstr MONGO
   ```

   Should show:
   ```
   MONGO_URI=mongodb://root:example@mongodb:27017/
   MONGO_DB=rfq_tracker
   ```

5. **Restart Containers:**
   ```powershell
   docker compose restart
   ```

### Data Not Persisting

**Symptoms:**
- Projects disappear after restart
- Need to re-run crawler each time

**Solutions:**

1. **Check Volume Exists:**
   ```powershell
   docker volume ls | findstr mongodb
   ```

2. **Verify Volume Mount:**
   ```powershell
   docker compose ps --format json | ConvertFrom-Json | Select-Object -ExpandProperty Mounts
   ```

3. **Don't Use `-v` Flag:**
   - `docker compose down` - Good (keeps data)
   - `docker compose down -v` - Bad (deletes data!)

---

## Volume Mount Issues

### Project Files Not Visible

**Symptoms:**
- Crawler finds no projects
- Dashboard shows "No projects found"

**Diagnosis:**

1. **Check Volume Mount in Container:**
   ```powershell
   docker compose exec app ls -la /app/projects
   ```

   or (if using different mount path):
   ```powershell
   docker compose exec app ls -la /app/mock_projects
   ```

2. **Verify docker-compose.yml:**
   ```yaml
   volumes:
     - C:/path/to/your/projects:/app/projects:ro
   ```

3. **Check config.json:**
   ```json
   {
     "root_path": "projects"
   }
   ```

**Solutions:**

1. **Use Absolute Windows Paths:**
   - Good: `C:/Users/YourName/Documents/Projects`
   - Bad: `./Projects` or `Projects`

2. **Use Forward Slashes:**
   - Good: `C:/path/to/projects`
   - Bad: `C:\path\to\projects`

3. **Rebuild After Changes:**
   ```powershell
   docker compose down
   docker compose up -d
   ```

### Permission Denied

**Symptoms:**
```
Permission denied: '/app/projects/...'
```

**Solutions:**

1. **Mount as Read-Only:**
   ```yaml
   volumes:
     - C:/path/to/projects:/app/projects:ro
   ```

2. **Check Docker Desktop File Sharing:**
   - Docker Desktop Settings → Resources → File sharing
   - Add the drive/folder containing your projects

3. **Check Windows Permissions:**
   - Right-click folder → Properties → Security
   - Ensure your user has Read permissions

---

## Performance Issues

### Dashboard Loads Slowly

**Common Causes:**

1. **Large Project Folders:**
   - Thousands of files slow down crawler
   - Use `filter_tags` in config.json to skip unnecessary folders

2. **Network Latency:**
   - If projects are on network drive, performance may be slow
   - Consider copying to local drive or using SSD

3. **Container Resources:**
   - Docker Desktop Settings → Resources
   - Increase CPU and Memory allocation

**Solutions:**

1. **Optimize config.json:**
   ```json
   {
     "filter_tags": ["Template", "archive", "Old", "Backup"],
     "file_filter_tags": [".db", ".tmp", ".log"]
   }
   ```

2. **Index MongoDB:**
   - Already done automatically on startup
   - Check with:
   ```powershell
   docker compose exec mongodb mongosh rfq_tracker --eval "db.projects.getIndexes()"
   ```

3. **Clear Browser Cache:**
   - Hard refresh: Ctrl + Shift + R

---

## Crawler Issues

### Crawler Times Out

**Symptoms:**
```
Refresh timed out after 5 minutes
```

**Solutions:**

1. **Run Manually to See Full Output:**
   ```powershell
   docker compose exec app python run_crawler.py
   ```

2. **Reduce Scope:**
   - Add more filters to config.json
   - Process fewer projects initially

3. **Increase Timeout:**
   Edit `streamlit_dashboard.py`:
   ```python
   timeout=600  # 10 minutes instead of 5
   ```

### Crawler Completes with Warnings

**Check Logs:**
```powershell
docker compose logs app | Select-String "error" -Context 5
```

**Common Warnings:**

1. **File Not Found:**
   - Normal if files were moved/deleted
   - No action needed

2. **Permission Denied:**
   - Check volume mount is read-only
   - Verify Windows permissions

3. **Encoding Errors:**
   - Some filenames may have special characters
   - Usually safe to ignore

---

## Scheduled Task Issues

### Task Doesn't Run

**Check Task Status:**
1. Open Task Scheduler
2. Find "RFQ Dashboard Data Refresh"
3. View "Last Run Result"
   - `0x0`: Success
   - `0x1`: General error
   - Other: Specific error code

**Common Issues:**

#### Docker Not Running

**Solution:**
Ensure Docker Desktop starts with Windows:
- Docker Desktop Settings → General
- Check "Start Docker Desktop when you log in"

#### Wrong Paths

**Verify Task Action:**
- Program: `powershell.exe`
- Arguments: `-ExecutionPolicy Bypass -File "C:\full\path\to\refresh-rfq-data.ps1"`
- Start in: `C:\full\path\to\RFQ_Dashboard`

**Use Absolute Paths:**
- Don't use relative paths like `.\refresh-rfq-data.ps1`

#### Permissions

**Requirements:**
- Run with highest privileges: Checked
- User account must have Docker access

**Test Manually:**
```powershell
.\refresh-rfq-data.ps1
```

If this works but scheduled task doesn't, it's a permissions issue.

### Task Runs But Doesn't Refresh Data

**Check Log Files:**
```powershell
Get-Content .\logs\refresh-*.log -Tail 50
```

**Common Issues:**

1. **Containers Not Running:**
   ```
   ERROR: No containers are running
   ```

   Start containers first:
   ```powershell
   docker compose up -d
   ```

2. **Wrong Container Name:**
   Script expects container named `rfq-tracker-app`

   Check actual name:
   ```powershell
   docker compose ps
   ```

3. **Crawler Error:**
   Check for Python errors in logs

---

## Getting Help

If you've tried these solutions and still have issues:

1. **Collect Information:**
   ```powershell
   # Docker version
   docker --version
   docker compose version

   # Container status
   docker compose ps

   # Recent logs
   docker compose logs --tail=100 > logs.txt

   # System info
   systeminfo > systeminfo.txt
   ```

2. **Check Documentation:**
   - [README.md](README.md) - Basic usage
   - [DEPLOYMENT.md](DEPLOYMENT.md) - Deployment details
   - This guide - Troubleshooting

3. **Common Log Locations:**
   - Application logs: `docker compose logs app`
   - Crawler logs: In `logs/` directory (if using scheduled task)
   - Docker logs: Docker Desktop → Troubleshoot → View logs

4. **Reset to Known State:**
   ```powershell
   # Stop everything
   docker compose down

   # Start fresh (keeps data)
   docker compose up -d

   # OR start completely fresh (deletes data)
   docker compose down -v
   docker compose up -d
   ```

---

## Quick Reference

### Essential Commands

```powershell
# Check if Docker is running
docker info

# View container status
docker compose ps

# View logs
docker compose logs app

# Restart containers
docker compose restart

# Stop containers
docker compose down

# Start containers
docker compose up -d

# Rebuild after code changes
docker compose build app
docker compose up -d

# Run crawler manually
docker compose exec app python run_crawler.py

# Access container shell
docker compose exec app /bin/bash

# Check volumes
docker volume ls

# Check networks
docker network ls

# Clean up unused resources
docker system prune
```

### Diagnostic Commands

```powershell
# Check port usage
netstat -ano | findstr :8501

# Check firewall rules
Get-NetFirewallRule -DisplayName "*Streamlit*"

# Check IP address
ipconfig

# Test network connectivity
ping <server-ip>
telnet <server-ip> 8501

# Check disk space
docker system df

# View all Docker resources
docker ps -a
docker images
docker volume ls
docker network ls
```

---

For more information, see [README.md](README.md) and [DEPLOYMENT.md](DEPLOYMENT.md).
