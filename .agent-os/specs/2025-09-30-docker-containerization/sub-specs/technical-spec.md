# Technical Specification

This is the technical specification for the spec detailed in @.agent-os/specs/2025-09-30-docker-containerization/spec.md

> Created: 2025-09-30
> Version: 1.0.0

## Technical Requirements

### 1. Docker Image Configuration

**Base Image:** `python:3.12-slim`
- Matches current Python version used in development
- Slim variant reduces image size while including necessary libraries
- Debian-based for compatibility with common dependencies

**Image Requirements:**
- All Python dependencies from requirements.txt installed
- Non-root user for security best practices
- Working directory: `/app`
- Health check endpoint configured
- Streamlit port 8501 exposed

### 2. MongoDB Container

**Official Image:** `mongo:7.0`
- Latest stable MongoDB version
- Persistent volume for data storage
- Internal network communication only (not exposed to host)

**Storage Requirements:**
- Named volume `mongodb_data` for database persistence
- Data survives container restarts and removals
- Volume location: Docker managed volume

### 3. Volume Mounts Strategy

**Projects Folder (Read-Only):**
```yaml
volumes:
  - ./Projects:/app/Projects:ro
```
- Read-only mount prevents accidental modifications
- Provides access to .eml files for crawler
- Host path relative to docker-compose.yml location

**Configuration File (Read-Write):**
```yaml
volumes:
  - ./config.json:/app/config.json:rw
```
- Allows hot configuration updates without rebuild
- Changes take effect on application restart
- Single file mount for precise control

**MongoDB Data (Persistent):**
```yaml
volumes:
  - mongodb_data:/data/db
```
- Named volume managed by Docker
- Persists across container lifecycle
- Automatic backup-friendly

### 4. Network Configuration

**Internal Network:**
- Bridge network named `rfq-network`
- App and MongoDB communicate via service names
- MongoDB hostname: `mongodb` (from service name)

**External Access:**
- Port 8501 exposed for dashboard access
- Configurable host binding via environment variable
- Default: `0.0.0.0:8501` for network access

### 5. Startup Crawler Integration

**Implementation Location:** `streamlit_dashboard.py`

**Approach:**
```python
import streamlit as st
import subprocess
import os
from pathlib import Path

# Execute on first load only
if 'startup_crawl_complete' not in st.session_state:
    st.session_state.startup_crawl_complete = False

    with st.spinner('Initializing dashboard... Refreshing RFQ data...'):
        try:
            result = subprocess.run(
                ['python', 'crawler.py'],
                cwd=Path(__file__).parent,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )

            if result.returncode == 0:
                st.session_state.startup_crawl_complete = True
                st.success('Data refresh complete!')
            else:
                st.warning(f'Data refresh completed with warnings. Dashboard will show existing data.')
                st.session_state.startup_crawl_complete = True

        except subprocess.TimeoutExpired:
            st.error('Data refresh timed out. Dashboard will show existing data.')
            st.session_state.startup_crawl_complete = True
        except Exception as e:
            st.error(f'Data refresh failed: {str(e)}. Dashboard will show existing data.')
            st.session_state.startup_crawl_complete = True
```

**Key Design Decisions:**
- Uses `st.session_state` to ensure single execution per session
- Subprocess call maintains isolation from Streamlit event loop
- Timeout prevents indefinite blocking
- Error handling allows dashboard to load even if crawler fails
- User sees progress indicator during refresh

### 6. Manual Refresh Button Implementation

**UI Component Location:** Top of sidebar or main page header

**Implementation:**
```python
import threading
import time

# Initialize refresh state
if 'refresh_in_progress' not in st.session_state:
    st.session_state.refresh_in_progress = False
if 'last_refresh_status' not in st.session_state:
    st.session_state.last_refresh_status = None
if 'last_refresh_time' not in st.session_state:
    st.session_state.last_refresh_time = None

def run_crawler_background():
    """Background thread function to run crawler"""
    try:
        result = subprocess.run(
            ['python', 'crawler.py'],
            cwd=Path(__file__).parent,
            capture_output=True,
            text=True,
            timeout=300
        )

        if result.returncode == 0:
            st.session_state.last_refresh_status = 'success'
        else:
            st.session_state.last_refresh_status = 'warning'

    except subprocess.TimeoutExpired:
        st.session_state.last_refresh_status = 'timeout'
    except Exception as e:
        st.session_state.last_refresh_status = f'error: {str(e)}'
    finally:
        st.session_state.refresh_in_progress = False
        st.session_state.last_refresh_time = time.time()

# Refresh button in sidebar
with st.sidebar:
    st.markdown("### Data Management")

    if st.session_state.refresh_in_progress:
        st.info('🔄 Refresh in progress...')
        st.button('Refresh Data', disabled=True)
    else:
        if st.button('🔄 Refresh Data', use_container_width=True):
            st.session_state.refresh_in_progress = True
            st.session_state.last_refresh_status = None

            # Start background thread
            thread = threading.Thread(target=run_crawler_background, daemon=True)
            thread.start()

            st.rerun()

    # Display last refresh status
    if st.session_state.last_refresh_status:
        if st.session_state.last_refresh_status == 'success':
            st.success('✅ Data refreshed successfully!')
        elif st.session_state.last_refresh_status == 'warning':
            st.warning('⚠️ Refresh completed with warnings')
        elif st.session_state.last_refresh_status == 'timeout':
            st.error('⏱️ Refresh timed out')
        else:
            st.error(f'❌ Refresh failed: {st.session_state.last_refresh_status}')

    # Show last refresh time
    if st.session_state.last_refresh_time:
        time_ago = time.time() - st.session_state.last_refresh_time
        if time_ago < 60:
            st.caption(f'Last refresh: {int(time_ago)} seconds ago')
        elif time_ago < 3600:
            st.caption(f'Last refresh: {int(time_ago/60)} minutes ago')
        else:
            st.caption(f'Last refresh: {int(time_ago/3600)} hours ago')
```

**Key Features:**
- Background threading prevents UI blocking
- Status tracking with session state
- Disabled button during refresh
- Clear status notifications
- Time since last refresh display
- Auto-rerun to show updated data

### 7. Environment Variables

**docker-compose.yml Configuration:**
```yaml
environment:
  - MONGODB_URI=mongodb://mongodb:27017/
  - MONGODB_DATABASE=rfq_dashboard
  - STREAMLIT_SERVER_PORT=8501
  - STREAMLIT_SERVER_ADDRESS=0.0.0.0
  - STREAMLIT_SERVER_HEADLESS=true
  - STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
```

**Application Integration:**
- MongoDB connection string read from environment
- Fallback to localhost for development
- Port configuration for flexibility

**Example Code in Application:**
```python
import os

MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
MONGODB_DATABASE = os.getenv('MONGODB_DATABASE', 'rfq_dashboard')
```

### 8. Dockerfile Structure

```dockerfile
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 streamlit && \
    chown -R streamlit:streamlit /app
USER streamlit

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Expose port
EXPOSE 8501

# Run application
CMD ["streamlit", "run", "streamlit_dashboard.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

**Security Considerations:**
- Non-root user (UID 1000)
- Minimal base image
- No unnecessary packages
- Health check for container orchestration

### 9. docker-compose.yml Structure

```yaml
version: '3.8'

services:
  mongodb:
    image: mongo:7.0
    container_name: rfq-mongodb
    restart: unless-stopped
    volumes:
      - mongodb_data:/data/db
    networks:
      - rfq-network
    environment:
      - MONGO_INITDB_DATABASE=rfq_dashboard
    healthcheck:
      test: echo 'db.runCommand("ping").ok' | mongosh localhost:27017/rfq_dashboard --quiet
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 20s

  app:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: rfq-dashboard
    restart: unless-stopped
    ports:
      - "8501:8501"
    volumes:
      - ./Projects:/app/Projects:ro
      - ./config.json:/app/config.json:rw
    networks:
      - rfq-network
    environment:
      - MONGODB_URI=mongodb://mongodb:27017/
      - MONGODB_DATABASE=rfq_dashboard
      - STREAMLIT_SERVER_PORT=8501
      - STREAMLIT_SERVER_ADDRESS=0.0.0.0
      - STREAMLIT_SERVER_HEADLESS=true
      - STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
    depends_on:
      mongodb:
        condition: service_healthy
    healthcheck:
      test: curl -f http://localhost:8501/_stcore/health || exit 1
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

networks:
  rfq-network:
    driver: bridge

volumes:
  mongodb_data:
    driver: local
```

**Key Features:**
- Health checks ensure MongoDB is ready before app starts
- Restart policy for resilience
- Named volumes for data persistence
- Isolated network for security
- Proper service dependencies

### 10. Windows Task Scheduler Integration

**Approach:** Host-level scheduled task triggers crawler inside container

**PowerShell Script (host):**
```powershell
# refresh-rfq-data.ps1
docker-compose -f "C:\path\to\RFQ_Dashboard\docker-compose.yml" exec -T app python crawler.py

if ($LASTEXITCODE -eq 0) {
    Write-Output "$(Get-Date): RFQ data refresh completed successfully"
} else {
    Write-Output "$(Get-Date): RFQ data refresh failed with exit code $LASTEXITCODE"
}
```

**Task Scheduler Configuration:**
- Trigger: Daily at specified time (e.g., 7:00 AM)
- Action: Execute PowerShell script
- Conditions: Run only when computer is on AC power (optional)
- Settings: Stop task if runs longer than 10 minutes

**Alternative Approach:** Container-level cron
- Install cron in Docker container
- Add crontab entry in Dockerfile
- Run cron alongside Streamlit (requires supervisor)

**Recommendation:** Use host-level Task Scheduler for:
- Easier debugging and logging
- No container modification required
- Better visibility of scheduled task status
- Simpler maintenance

### 11. Network Deployment Configuration

**Host Binding:**
```yaml
ports:
  - "0.0.0.0:8501:8501"  # Bind to all interfaces
```

**Firewall Configuration (Windows):**
```powershell
# Allow inbound traffic on port 8501
New-NetFirewallRule -DisplayName "RFQ Dashboard" -Direction Inbound -LocalPort 8501 -Protocol TCP -Action Allow
```

**Access URL:**
- Internal: `http://<host-ip>:8501`
- Hostname: `http://<hostname>:8501`

**Security Considerations:**
- No authentication in initial implementation (future enhancement)
- Restrict firewall rules to office network subnet if possible
- Consider reverse proxy (nginx) for production deployment

### 12. Deployment Documentation Structure

**README.md Updates:**
1. Docker deployment section
2. Prerequisites (Docker, Docker Compose installed)
3. Quick start commands
4. Volume mount configuration
5. Network access setup
6. Troubleshooting guide

**Separate DEPLOYMENT.md:**
1. Detailed Docker installation instructions
2. Configuration file setup
3. First-time deployment steps
4. Windows Task Scheduler setup
5. Network deployment configuration
6. Backup and restore procedures
7. Updating the application
8. Common issues and solutions

## Approach

### Phase 1: Docker Configuration
1. Create Dockerfile with proper base image and dependencies
2. Create docker-compose.yml with app and MongoDB services
3. Configure volume mounts for Projects, config.json, and MongoDB data
4. Test local deployment with `docker-compose up`

### Phase 2: Application Integration
1. Modify MongoDB connection code to use environment variables
2. Implement startup crawler in streamlit_dashboard.py
3. Test startup refresh functionality
4. Verify data persistence across container restarts

### Phase 3: Manual Refresh Feature
1. Implement refresh button in Streamlit UI
2. Add background threading for non-blocking refresh
3. Implement status notifications and progress indicators
4. Test refresh functionality with multiple concurrent users

### Phase 4: Network Deployment
1. Configure host binding for network access
2. Test access from multiple devices on office network
3. Configure Windows Firewall rules
4. Create PowerShell script for scheduled refresh

### Phase 5: Documentation
1. Update README.md with Docker deployment instructions
2. Create detailed DEPLOYMENT.md guide
3. Document Windows Task Scheduler setup
4. Create troubleshooting guide

### Phase 6: Testing & Validation
1. Test complete deployment from scratch
2. Verify data persistence and volume mounts
3. Test startup and manual refresh functionality
4. Verify network access from multiple devices
5. Test scheduled refresh via Task Scheduler

## External Dependencies

### Required Software
- **Docker Desktop for Windows** (version 4.0+)
  - Includes Docker Engine and Docker Compose
  - WSL2 backend recommended for performance

- **Git** (for version control and deployment)

### Docker Images
- **python:3.12-slim** (official Python image)
  - Base image for application container
  - Size: ~130 MB compressed

- **mongo:7.0** (official MongoDB image)
  - Database container
  - Size: ~180 MB compressed

### Python Dependencies
All existing dependencies from requirements.txt:
- streamlit
- pymongo
- pandas
- Additional packages as required

### Network Requirements
- Office WiFi network access
- Port 8501 available on host
- Docker daemon running on host

### Host System Requirements
- **OS:** Windows 10/11 Pro or Enterprise (for Docker Desktop)
- **RAM:** Minimum 8 GB (16 GB recommended)
- **Disk:** 10 GB free space for images and volumes
- **CPU:** 64-bit processor with virtualization support

### Optional Dependencies
- **nginx** (for reverse proxy in production)
- **Portainer** (for container management UI)
- **Docker Compose V2** (included with Docker Desktop)
