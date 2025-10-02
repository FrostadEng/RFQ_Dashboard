# Docker Containerization for RFQ Dashboard - Lite Summary

Containerize the RFQ Dashboard with Docker Compose to eliminate MongoDB installation complexity, enable network deployment, and provide automatic data refresh on startup plus manual refresh via UI button.

## Key Points
- Docker Compose orchestrates Streamlit app and MongoDB containers
- Volume mounts for config.json (editable), Projects folder (read-only), and MongoDB data (persistent)
- Auto-refresh on startup and manual refresh button with status notifications
- Network deployment on port 8501 for office-wide access
