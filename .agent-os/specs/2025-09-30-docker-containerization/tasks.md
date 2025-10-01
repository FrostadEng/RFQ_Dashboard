# Spec Tasks

These are the tasks to be completed for the spec detailed in @.agent-os/specs/2025-09-30-docker-containerization/spec.md

> Created: 2025-09-30
> Status: Ready for Implementation

## Tasks

### Phase 1: Docker Configuration (Priority: High)

- [ ] **Task 1.1:** Create Dockerfile
  - Base image: python:3.12-slim
  - Install system dependencies (curl for health check)
  - Copy requirements.txt and install Python dependencies
  - Copy application code
  - Create non-root user (streamlit, UID 1000)
  - Configure health check endpoint
  - Set CMD to run Streamlit application
  - **Estimated Time:** 2 hours

- [ ] **Task 1.2:** Create docker-compose.yml
  - Define `mongodb` service with mongo:7.0 image
  - Define `app` service building from Dockerfile
  - Configure `rfq-network` bridge network
  - Create `mongodb_data` named volume
  - Set up service dependencies with health check conditions
  - Configure environment variables for both services
  - **Estimated Time:** 2 hours

- [ ] **Task 1.3:** Configure Volume Mounts
  - Projects folder: read-only mount
  - config.json: read-write mount
  - MongoDB data: persistent named volume
  - Test volume permissions and accessibility
  - **Estimated Time:** 1 hour

- [ ] **Task 1.4:** Test Local Deployment
  - Run `docker-compose build`
  - Run `docker-compose up -d`
  - Verify both containers start successfully
  - Check health check status
  - Access dashboard at localhost:8501
  - Verify MongoDB connection
  - **Estimated Time:** 2 hours

### Phase 2: Application Integration (Priority: High)

- [ ] **Task 2.1:** Update MongoDB Connection Configuration
  - Modify database connection code to read from environment variables
  - Implement fallback to localhost for development
  - Update MongoDB URI to use service name `mongodb`
  - Test connection with both containerized and local MongoDB
  - **Estimated Time:** 1 hour

- [ ] **Task 2.2:** Implement Startup Crawler
  - Add session state check for first load
  - Implement subprocess call to crawler.py
  - Add timeout (5 minutes) and error handling
  - Display spinner with "Initializing dashboard" message
  - Show success/warning/error notifications
  - Ensure dashboard loads even if crawler fails
  - **Estimated Time:** 3 hours

- [ ] **Task 2.3:** Test Startup Refresh
  - Test container startup with crawler execution
  - Verify data is refreshed before UI loads
  - Test timeout and error scenarios
  - Check crawler logs in container
  - Verify proper session state management
  - **Estimated Time:** 2 hours

- [ ] **Task 2.4:** Verify Data Persistence
  - Restart containers and verify MongoDB data persists
  - Stop and remove containers, then restart
  - Verify volume data remains intact
  - Test config.json changes without rebuild
  - **Estimated Time:** 1 hour

### Phase 3: Manual Refresh Feature (Priority: Medium)

- [ ] **Task 3.1:** Implement Refresh Button UI
  - Add refresh button to sidebar or header
  - Initialize session state variables for refresh tracking
  - Implement disabled state during refresh
  - Add visual indicator (icon, styling)
  - **Estimated Time:** 2 hours

- [ ] **Task 3.2:** Implement Background Refresh
  - Create background thread function for crawler execution
  - Implement thread start on button click
  - Add timeout and error handling in background thread
  - Update session state from background thread
  - **Estimated Time:** 3 hours

- [ ] **Task 3.3:** Implement Status Notifications
  - Success notification with checkmark
  - Warning notification for completed with warnings
  - Error notification with error message
  - Timeout notification
  - Display time since last refresh
  - **Estimated Time:** 2 hours

- [ ] **Task 3.4:** Test Refresh Functionality
  - Test successful refresh scenario
  - Test error and timeout scenarios
  - Test multiple rapid button clicks
  - Test concurrent users refreshing simultaneously
  - Verify UI remains responsive during refresh
  - **Estimated Time:** 2 hours

### Phase 4: Network Deployment (Priority: Medium)

- [ ] **Task 4.1:** Configure Network Access
  - Update docker-compose.yml to bind to 0.0.0.0
  - Configure Streamlit server address environment variable
  - Test access from host machine
  - **Estimated Time:** 1 hour

- [ ] **Task 4.2:** Configure Windows Firewall
  - Create inbound rule for port 8501
  - Test access from another device on network
  - Document firewall configuration steps
  - **Estimated Time:** 1 hour

- [ ] **Task 4.3:** Create PowerShell Script for Scheduled Refresh
  - Write refresh-rfq-data.ps1 script
  - Implement docker-compose exec command
  - Add logging and error handling
  - Test script execution manually
  - **Estimated Time:** 2 hours

- [ ] **Task 4.4:** Test Network Access
  - Access dashboard from multiple devices
  - Test concurrent user access
  - Verify performance with multiple connections
  - Test refresh from different clients
  - **Estimated Time:** 2 hours

### Phase 5: Documentation (Priority: Medium)

- [ ] **Task 5.1:** Update README.md
  - Add Docker deployment section
  - Document prerequisites (Docker Desktop)
  - Add quick start commands
  - Include basic troubleshooting tips
  - **Estimated Time:** 2 hours

- [ ] **Task 5.2:** Create DEPLOYMENT.md
  - Docker Desktop installation instructions for Windows
  - Step-by-step deployment guide
  - Volume mount configuration details
  - Network deployment setup
  - **Estimated Time:** 3 hours

- [ ] **Task 5.3:** Document Task Scheduler Setup
  - PowerShell script creation steps
  - Task Scheduler configuration walkthrough
  - Screenshots for key steps
  - Testing scheduled task execution
  - **Estimated Time:** 2 hours

- [ ] **Task 5.4:** Create Troubleshooting Guide
  - Common issues and solutions
  - Container logs access
  - Volume mount issues
  - Network connectivity problems
  - MongoDB connection errors
  - **Estimated Time:** 2 hours

### Phase 6: Testing & Validation (Priority: High)

- [ ] **Task 6.1:** End-to-End Deployment Test
  - Fresh clone of repository
  - Build and start containers from scratch
  - Verify all functionality works
  - Test on clean Windows machine
  - **Estimated Time:** 3 hours

- [ ] **Task 6.2:** Data Persistence Testing
  - Test volume data across restarts
  - Test config.json updates
  - Test MongoDB data integrity
  - Verify backup/restore procedures
  - **Estimated Time:** 2 hours

- [ ] **Task 6.3:** Network Deployment Validation
  - Test from multiple office devices
  - Verify concurrent access
  - Test scheduled refresh execution
  - Monitor performance under load
  - **Estimated Time:** 2 hours

- [ ] **Task 6.4:** Documentation Review
  - Follow all documentation steps
  - Verify accuracy of instructions
  - Test all commands and scripts
  - Update based on findings
  - **Estimated Time:** 2 hours

## Task Dependencies

```
Phase 1 (Docker Configuration)
  ├─→ Task 1.1 (Dockerfile) ──┐
  ├─→ Task 1.2 (docker-compose.yml) ──┤
  ├─→ Task 1.3 (Volume Mounts) ──┤
  └─→ Task 1.4 (Test Deployment) ←─────┘
       │
       ↓
Phase 2 (Application Integration)
  ├─→ Task 2.1 (MongoDB Config) ──┐
  ├─→ Task 2.2 (Startup Crawler) ──┤
  ├─→ Task 2.3 (Test Startup) ←────┤
  └─→ Task 2.4 (Data Persistence) ←┘
       │
       ↓
Phase 3 (Manual Refresh)
  ├─→ Task 3.1 (Refresh Button) ──┐
  ├─→ Task 3.2 (Background Refresh) ──┤
  ├─→ Task 3.3 (Status Notifications) ──┤
  └─→ Task 3.4 (Test Refresh) ←─────────┘
       │
       ↓
Phase 4 (Network Deployment)
  ├─→ Task 4.1 (Network Config) ──┐
  ├─→ Task 4.2 (Firewall) ──┤
  ├─→ Task 4.3 (PowerShell Script) ──┤
  └─→ Task 4.4 (Test Network Access) ←┘
       │
       ↓
Phase 5 (Documentation) ──┐
  ├─→ Task 5.1 (README)    │
  ├─→ Task 5.2 (DEPLOYMENT)│
  ├─→ Task 5.3 (Task Scheduler) │
  └─→ Task 5.4 (Troubleshooting)│
       │                   │
       ↓                   │
Phase 6 (Testing & Validation) ←┘
  ├─→ Task 6.1 (E2E Test)
  ├─→ Task 6.2 (Persistence Test)
  ├─→ Task 6.3 (Network Validation)
  └─→ Task 6.4 (Documentation Review)
```

## Estimated Total Time

- **Phase 1:** 7 hours
- **Phase 2:** 7 hours
- **Phase 3:** 9 hours
- **Phase 4:** 6 hours
- **Phase 5:** 9 hours
- **Phase 6:** 9 hours

**Total Estimated Time:** 47 hours (approximately 6 working days)

## Success Metrics

- All containers start successfully with `docker-compose up`
- Dashboard loads with refreshed data on startup
- Manual refresh button works with status notifications
- MongoDB data persists across container restarts
- Config.json changes apply without rebuilding
- Multiple users can access dashboard on office network
- Scheduled refresh executes successfully via Task Scheduler
- All documentation is accurate and complete
