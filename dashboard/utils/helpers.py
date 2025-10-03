"""
Helper utility functions for RFQ Dashboard.
"""

import sys
import logging
import platform
import subprocess
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

logger = logging.getLogger(__name__)


def format_timestamp(timestamp_str: str) -> str:
    """Format ISO 8601 timestamp to human-readable format."""
    try:
        dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except:
        return timestamp_str


def create_file_link(file_path: str, link_text: str = "Open") -> str:
    """
    Create clickable link to open file in system default application.

    Args:
        file_path: Absolute path to file
        link_text: Display text for link

    Returns:
        Markdown link string
    """
    try:
        # Convert to absolute path and normalize
        abs_path = str(Path(file_path).resolve())

        # URL encode the path
        encoded_path = quote(abs_path.replace('\\', '/'))

        # Platform-specific file URL format
        if platform.system() == 'Windows':
            file_url = f"file:///{encoded_path}"
        else:
            file_url = f"file://{encoded_path}"

        return f"[{link_text}]({file_url})"
    except Exception as e:
        logger.error(f"Error creating file link for {file_path}: {e}")
        return f"⚠️ {link_text} (path error)"


def run_startup_crawler() -> tuple[bool, str]:
    """
    Run the crawler on dashboard startup to refresh data.

    Returns:
        Tuple of (success: bool, message: str)
    """
    try:
        # Run crawler with 5 minute timeout
        result = subprocess.run(
            [sys.executable, "run_crawler.py"],
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes
        )

        if result.returncode == 0:
            return True, "Data refreshed successfully"
        else:
            error_msg = result.stderr if result.stderr else "Unknown error"
            logger.warning(f"Crawler completed with errors: {error_msg}")
            return False, f"Crawler completed with warnings: {error_msg[:100]}"
    except subprocess.TimeoutExpired:
        logger.error("Crawler timed out after 5 minutes")
        return False, "Crawler timed out after 5 minutes"
    except Exception as e:
        logger.error(f"Error running crawler: {e}")
        return False, f"Error refreshing data: {str(e)[:100]}"


def run_manual_refresh() -> tuple[bool, str]:
    """
    Run manual refresh synchronously (not in background).

    Returns:
        Tuple of (success: bool, message: str)
    """
    try:
        result = subprocess.run(
            [sys.executable, "run_crawler.py"],
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes
        )

        if result.returncode == 0:
            return True, "Data refreshed successfully"
        else:
            error_msg = result.stderr if result.stderr else "Unknown error"
            logger.warning(f"Manual refresh completed with errors: {error_msg}")
            return False, f"Completed with warnings: {error_msg[:100]}"
    except subprocess.TimeoutExpired:
        logger.error("Manual refresh timed out")
        return False, "Refresh timed out after 5 minutes"
    except Exception as e:
        logger.error(f"Manual refresh error: {e}")
        return False, f"Error: {str(e)[:100]}"
