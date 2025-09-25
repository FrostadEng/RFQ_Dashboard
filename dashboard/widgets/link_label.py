import os
import sys
import logging
import subprocess
from PyQt6.QtWidgets import QLabel, QWidget
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QCursor

logger = logging.getLogger(__name__)

class LinkLabel(QLabel):
    """A QLabel that acts like a hyperlink and opens a file path."""
    def __init__(self, text: str, path: str, parent: QWidget = None):
        super().__init__(text, parent)
        self.path = path
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setStyleSheet("color: #3498db; text-decoration: underline;")

    def mousePressEvent(self, event):
        open_file_location(self.path)

def open_file_location(path: str):
    """Opens the given file or directory in the system's file explorer."""
    try:
        if os.path.isdir(path):
            directory = path
        else:
            directory = os.path.dirname(path)

        if sys.platform == "win32":
            os.startfile(directory)
        elif sys.platform == "darwin": # macOS
            subprocess.run(["open", directory])
        else: # Linux
            subprocess.run(["xdg-open", directory])
        logger.info(f"Opened file location: {directory}")
    except Exception as e:
        logger.error(f"Failed to open file location {path}: {e}")