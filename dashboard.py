import sys
import os
import json
import logging
import subprocess
import argparse
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QLineEdit, QListWidget, QListWidgetItem,
                             QPushButton, QSpacerItem, QSizePolicy, QFrame,
                             QScrollArea)
from PyQt6.QtCore import (Qt, QPropertyAnimation, QEasingCurve, QParallelAnimationGroup,
                          QAbstractAnimation)
from PyQt6.QtGui import QCursor

from rfq_tracker.db_manager import DBManager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LinkLabel(QLabel):
    def __init__(self, text: str, path: str, parent: QWidget = None):
        super().__init__(text, parent)
        self.path = path
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setStyleSheet("color: #3498db; text-decoration: underline;")

    def mousePressEvent(self, event):
        open_file_location(self.path)

def open_file_location(path: str):
    try:
        directory = os.path.dirname(path) if not os.path.isdir(path) else path
        if sys.platform == "win32":
            os.startfile(directory)
        elif sys.platform == "darwin":
            subprocess.run(["open", directory])
        else:
            subprocess.run(["xdg-open", directory])
        logger.info(f"Opened file location: {directory}")
    except Exception as e:
        logger.error(f"Failed to open file location {path}: {e}")

class CollapsibleWidget(QWidget):
    def __init__(self, title: str = "", parent: QWidget = None):
        super().__init__(parent)
        self.is_expanded = False
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self.header = QWidget()
        self.header_layout = QHBoxLayout(self.header)
        self.toggle_button = QPushButton(title)
        self.toggle_button.setStyleSheet("text-align: left; font-weight: bold; font-size: 16px; border: none;")
        self.toggle_button.clicked.connect(self.toggle)
        self.header_layout.addWidget(self.toggle_button)
        self.header_layout.addStretch()
        self.content_area = QWidget()
        self.content_layout = QVBoxLayout(self.content_area)
        self.content_area.setVisible(False)
        self.content_area.setFixedHeight(0)
        main_layout.addWidget(self.header)
        main_layout.addWidget(self.content_area)
        self.animation = QPropertyAnimation(self.content_area, b"maximumHeight")
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutCubic)

    def set_content_layout(self, layout: QVBoxLayout):
        # Existing content layout clearing logic
        temp_widget = QWidget()
        temp_widget.setLayout(layout)
        self.content_layout.addWidget(temp_widget)

    def toggle(self):
        self.is_expanded = not self.is_expanded
        start_height = self.content_area.height()
        end_height = self.content_layout.sizeHint().height() if self.is_expanded else 0
        self.animation.setStartValue(start_height)
        self.animation.setEndValue(end_height)
        if self.is_expanded: self.content_area.setVisible(True)
        self.animation.start()
        if not self.is_expanded:
            self.animation.finished.connect(lambda: self.content_area.setVisible(False))

class MainWindow(QMainWindow):
    def __init__(self, db_manager: DBManager = None, dry_run: bool = False):
        super().__init__()
        self.db_manager = db_manager
        self.dry_run = dry_run
        self.setWindowTitle("Project RFQ Tracker")
        self.setGeometry(100, 100, 1600, 900)
        self.setStyleSheet(self.get_stylesheet())
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        self.setCentralWidget(main_widget)
        sidebar = self.create_sidebar()
        self.content_scroll_area = self.create_content_area()
        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.content_scroll_area, 1)
        self.load_projects()

    def create_sidebar(self) -> QWidget:
        # UI setup remains the same
        sidebar = QWidget()
        sidebar.setFixedWidth(300)
        sidebar_layout = QVBoxLayout(sidebar)
        title_label = QLabel("Projects")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 10px;")
        sidebar_layout.addWidget(title_label)
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search Project Number...")
        self.search_bar.textChanged.connect(self.filter_projects)
        sidebar_layout.addWidget(self.search_bar)
        self.project_list_widget = QListWidget()
        self.project_list_widget.itemSelectionChanged.connect(self.on_project_selected)
        sidebar_layout.addWidget(self.project_list_widget)
        # ... pagination ...
        return sidebar

    def create_content_area(self) -> QScrollArea:
        # UI setup remains the same
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        content_widget = QWidget()
        self.content_layout = QVBoxLayout(content_widget)
        self.placeholder_label = QLabel("Select a project to see details.")
        self.content_layout.addWidget(self.placeholder_label)
        scroll_area.setWidget(content_widget)
        return scroll_area

    def load_projects(self):
        self.project_list_widget.clear()
        if self.dry_run:
            logger.info("Dry Run: Loading mock projects.")
            for i in range(5):
                project_data = {'project_number': f'800{123+i}'}
                item = QListWidgetItem(f"Project {project_data['project_number']}")
                item.setData(Qt.ItemDataRole.UserRole, project_data)
                self.project_list_widget.addItem(item)
            return

        try:
            projects = self.db_manager.db.projects.find().sort("project_number", -1)
            for project in projects:
                item = QListWidgetItem(f"Project {project['project_number']}")
                item.setData(Qt.ItemDataRole.UserRole, project)
                self.project_list_widget.addItem(item)
            logger.info(f"Loaded {self.project_list_widget.count()} projects.")
        except Exception as e:
            logger.error(f"Failed to load projects from MongoDB: {e}")

    def on_project_selected(self):
        selected_items = self.project_list_widget.selectedItems()
        if not selected_items: return
        project_data = selected_items[0].data(Qt.ItemDataRole.UserRole)
        self.clear_content_area()
        self.load_supplier_data(project_data['project_number'])

    def load_supplier_data(self, project_number: str):
        if self.dry_run:
            logger.info(f"Dry Run: Loading mock suppliers for project {project_number}.")
            for i in range(3):
                supplier_data = {
                    'supplier_name': f'Mock Supplier {i+1}',
                    'project_number': project_number
                }
                supplier_widget = self.create_supplier_widget(supplier_data)
                self.content_layout.addWidget(supplier_widget)
            self.content_layout.addStretch()
            return

        suppliers = self.db_manager.db.suppliers.find({"project_number": project_number})
        for supplier in suppliers:
            supplier_widget = self.create_supplier_widget(supplier)
            self.content_layout.addWidget(supplier_widget)
        self.content_layout.addStretch()

    def create_supplier_widget(self, supplier_data: dict) -> CollapsibleWidget:
        supplier_widget = CollapsibleWidget(title=supplier_data['supplier_name'])
        content_layout = QVBoxLayout()
        columns_layout = QHBoxLayout()

        # Sent
        sent_layout = QVBoxLayout()
        sent_layout.addWidget(QLabel("Sent Transmissions"))
        if self.dry_run:
            sent_layout.addWidget(LinkLabel("mock_transmission.zip", "/path/to/mock_transmission.zip"))
        else:
            transmissions = self.db_manager.db.transmissions.find({"project_number": supplier_data["project_number"], "supplier_name": supplier_data["supplier_name"]})
            for trans in transmissions:
                sent_layout.addWidget(LinkLabel(trans['zip_name'], trans['zip_path']))
        sent_layout.addStretch()

        # Received
        received_layout = QVBoxLayout()
        received_layout.addWidget(QLabel("Received Submissions"))
        if self.dry_run:
             received_layout.addWidget(LinkLabel("mock_submission_folder", "/path/to/mock_submission"))
        else:
            receipts = self.db_manager.db.receipts.find({"project_number": supplier_data["project_number"], "supplier_name": supplier_data["supplier_name"]})
            for receipt in receipts:
                received_layout.addWidget(LinkLabel(os.path.basename(receipt['received_folder_path']), receipt['received_folder_path']))
        received_layout.addStretch()

        columns_layout.addLayout(sent_layout)
        columns_layout.addLayout(received_layout)
        content_layout.addLayout(columns_layout)
        supplier_widget.set_content_layout(content_layout)
        return supplier_widget

    def filter_projects(self):
        filter_text = self.search_bar.text().lower()
        for i in range(self.project_list_widget.count()):
            item = self.project_list_widget.item(i)
            item.setHidden(filter_text not in item.text().lower())

    def clear_content_area(self):
        while self.content_layout.count():
            child = self.content_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def get_stylesheet(self) -> str: return """/* Stylesheet remains the same */ QMainWindow, QWidget, QScrollArea { background-color: #2c3e50; color: #ecf0f1; font-family: "Segoe UI", "Arial"; } QLabel { font-size: 14px; } QLineEdit { background-color: #34495e; border: 1px solid #2c3e50; border-radius: 5px; padding: 8px; font-size: 14px; } QListWidget { background-color: #34495e; border: none; font-size: 16px; } QListWidget::item { padding: 10px; } QListWidget::item:selected { background-color: #3498db; color: white; } QPushButton { background-color: #3498db; color: white; border: none; border-radius: 5px; padding: 8px 16px; } QPushButton:hover { background-color: #2980b9; } QScrollArea { border: none; } """

def main():
    parser = argparse.ArgumentParser(description="RFQ Tracker Dashboard")
    parser.add_argument("--dry-run", action="store_true", help="Run with mock data without connecting to MongoDB.")
    args = parser.parse_args()

    app = QApplication(sys.argv)

    db_manager = None
    if not args.dry_run:
        config = json.load(open("config.json"))
        db_manager = DBManager(mongo_uri=config.get("mongo_uri"), db_name=config.get("mongo_db"))
        db_manager.connect()

    window = MainWindow(db_manager, dry_run=args.dry_run)
    window.show()

    exit_code = app.exec()
    if db_manager:
        db_manager.close()
    sys.exit(exit_code)

if __name__ == "__main__":
    main()