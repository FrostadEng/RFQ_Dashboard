import os
import subprocess
import logging
import sys
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTextBrowser, QTableWidget, QTableWidgetItem,
    QTextEdit, QPushButton, QHBoxLayout, QLabel, QHeaderView
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

from rag_chat import get_rag_response

logger = logging.getLogger(__name__)

class RagWorker(QThread):
    """
    Worker thread to run the RAG process without freezing the UI.
    """
    finished = pyqtSignal(dict)

    def __init__(self, query: str):
        super().__init__()
        self.query = query

    def run(self):
        """This will be executed in the new thread."""
        result = get_rag_response(self.query)
        self.finished.emit(result)

class AskTerenceWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        # 1. Chat History Panel
        self.chat_history = QTextBrowser()
        self.chat_history.setReadOnly(True)
        self.chat_history.setStyleSheet("background-color: #2c2c2e; border: 1px solid #444;")
        main_layout.addWidget(self.chat_history, 5)

        # 2. Sources Panel
        sources_label = QLabel("Sources:")
        sources_label.setStyleSheet("font-weight: bold;")
        self.sources_table = QTableWidget()
        self.sources_table.setColumnCount(3)
        self.sources_table.setHorizontalHeaderLabels(["File Path", "Snippet", "Action"])
        self.sources_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.sources_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.sources_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.sources_table.cellClicked.connect(self.on_source_cell_clicked)
        main_layout.addWidget(sources_label)
        main_layout.addWidget(self.sources_table, 2)

        # 3. Input Panel
        input_layout = QHBoxLayout()
        self.input_box = QTextEdit()
        self.input_box.setPlaceholderText("Ask a question about your projects...")
        self.input_box.setFixedHeight(50)
        self.ask_button = QPushButton("Ask")
        self.ask_button.clicked.connect(self.handle_ask_button_click)

        input_layout.addWidget(self.input_box)
        input_layout.addWidget(self.ask_button)
        main_layout.addLayout(input_layout, 1)

    def handle_ask_button_click(self):
        query = self.input_box.toPlainText().strip()
        if not query:
            return

        self.append_message("You", query)
        self.input_box.clear()

        self.ask_button.setEnabled(False)
        self.ask_button.setText("Thinking...")

        # Run backend in a separate thread
        self.worker = RagWorker(query)
        self.worker.start()
        self.worker.finished.connect(self.update_ui_with_response)

    def update_ui_with_response(self, response: dict):
        """Updates the UI with the response from the backend."""
        self.append_message("Terence", response.get("answer", "No answer found."))

        self.sources_table.setRowCount(0)
        sources = response.get("sources", [])
        for row, source in enumerate(sources):
            self.sources_table.insertRow(row)
            self.sources_table.setItem(row, 0, QTableWidgetItem(source.get("file_path")))
            self.sources_table.setItem(row, 1, QTableWidgetItem(source.get("snippet")))

            open_button = QPushButton("Open")
            open_button.setProperty("file_path", source.get("file_path"))
            self.sources_table.setCellWidget(row, 2, open_button)
            open_button.clicked.connect(lambda _, p=source.get("file_path"): self.open_file(p))

        self.ask_button.setEnabled(True)
        self.ask_button.setText("Ask")

    def append_message(self, sender: str, message: str):
        """Appends a message to the chat history with basic color coding."""
        color = "#5daee7" if sender == "You" else "#dcdcdc"
        formatted_message = f'<p style="color:{color};"><b>{sender}:</b> {message}</p>'
        self.chat_history.append(formatted_message)

    def on_source_cell_clicked(self, row, column):
        """Handle clicks on the 'Open' button in the sources table."""
        if column == 2: # "Action" column
            widget = self.sources_table.cellWidget(row, column)
            if isinstance(widget, QPushButton):
                file_path = widget.property("file_path")
                if file_path:
                    self.open_file(file_path)

    def open_file(self, file_path: str):
        """Opens a file using the system's default application."""
        if not file_path or not os.path.exists(file_path):
            logger.warning(f"File not found or path is invalid: {file_path}")
            # Optionally, show a message box to the user
            return

        try:
            logger.info(f"Opening file: {file_path}")
            if os.name == "nt":  # Windows
                os.startfile(file_path)
            elif sys.platform == "darwin": # macOS
                subprocess.call(("open", file_path))
            else: # Linux
                subprocess.call(("xdg-open", file_path))
        except Exception as e:
            logger.error(f"Failed to open file {file_path}: {e}")