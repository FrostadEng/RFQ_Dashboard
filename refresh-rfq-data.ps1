# PowerShell Script to Refresh RFQ Dashboard Data
# This script runs the crawler inside the Docker container to update project data
# Designed to be run via Windows Task Scheduler

# Configuration
$COMPOSE_FILE = "docker-compose.yml"
$LOG_DIR = "logs"
$LOG_FILE = "$LOG_DIR\refresh-$(Get-Date -Format 'yyyy-MM-dd').log"

# Function to write log messages
function Write-Log {
    param([string]$Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[$timestamp] $Message"
    Write-Host $logMessage
    Add-Content -Path $LOG_FILE -Value $logMessage
}

# Create log directory if it doesn't exist
if (-not (Test-Path $LOG_DIR)) {
    New-Item -ItemType Directory -Path $LOG_DIR | Out-Null
}

Write-Log "=== Starting RFQ Data Refresh ==="

# Check if Docker is running
try {
    docker info | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Log "ERROR: Docker is not running. Please start Docker Desktop."
        exit 1
    }
} catch {
    Write-Log "ERROR: Docker command not found. Please ensure Docker Desktop is installed."
    exit 1
}

# Check if containers are running
Write-Log "Checking container status..."
$containerStatus = docker compose ps --format json | ConvertFrom-Json
if (-not $containerStatus) {
    Write-Log "ERROR: No containers are running. Please start the application with 'docker compose up -d'"
    exit 1
}

# Run the crawler inside the container
Write-Log "Executing crawler inside rfq-tracker-app container..."
try {
    docker compose exec -T app python run_crawler.py 2>&1 | ForEach-Object {
        Write-Log "CRAWLER: $_"
    }

    if ($LASTEXITCODE -eq 0) {
        Write-Log "SUCCESS: Data refresh completed successfully"
        exit 0
    } else {
        Write-Log "WARNING: Crawler completed with exit code $LASTEXITCODE"
        exit $LASTEXITCODE
    }
} catch {
    Write-Log "ERROR: Failed to execute crawler: $_"
    exit 1
}
