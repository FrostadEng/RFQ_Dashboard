import os
import logging
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QTreeView, QSplitter,
                             QPushButton, QFrame, QScrollArea, QDateEdit, QCheckBox)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QStandardItemModel, QStandardItem

from rfq_tracker.db_manager import DBManager
from .widgets.link_label import LinkLabel
from .widgets.collapsible_widget import CollapsibleWidget

logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    def __init__(self, db_manager: DBManager = None, dry_run: bool = False):
        super().__init__()
        self.db_manager = db_manager
        self.dry_run = dry_run
        self.setWindowTitle("Project RFQ Tracker")
        self.setGeometry(100, 100, 1600, 900)
        self.setStyleSheet(self.get_stylesheet())

        # Main layout is now a QSplitter
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.setCentralWidget(self.splitter)

        sidebar = self.create_sidebar()
        self.content_scroll_area = self.create_content_area()

        self.splitter.addWidget(sidebar)

        # Create the main content area with a vertical layout
        main_content_widget = QWidget()
        main_content_layout = QVBoxLayout(main_content_widget)
        main_content_layout.setContentsMargins(0, 0, 0, 0)
        main_content_layout.setSpacing(0)

        # Add the new persistent filter bar
        filter_bar = self.create_filter_bar()
        main_content_layout.addWidget(filter_bar)

        # Add the scroll area for details below the filter bar
        self.content_scroll_area = self.create_content_area()
        main_content_layout.addWidget(self.content_scroll_area)

        self.splitter.addWidget(main_content_widget)
        self.splitter.setSizes([300, 1300])

        self.load_projects()

    def create_filter_bar(self) -> QWidget:
        """Creates the persistent top filter bar for the main content area."""
        filter_widget = QWidget()
        filter_widget.setStyleSheet("background-color: #3c3f41; padding: 5px;")
        filter_layout = QHBoxLayout(filter_widget)

        # Date Range Filter
        date_filter_layout = QHBoxLayout()
        self.start_date_edit = QDateEdit(calendarPopup=True)
        self.end_date_edit = QDateEdit(calendarPopup=True)
        self.start_date_edit.setDate(QDate.currentDate().addMonths(-6))
        self.end_date_edit.setDate(QDate.currentDate())
        date_filter_layout.addWidget(QLabel("From:"))
        date_filter_layout.addWidget(self.start_date_edit)
        date_filter_layout.addWidget(QLabel("To:"))
        date_filter_layout.addWidget(self.end_date_edit)

        # File Type Filter
        self.file_filter_input = QLineEdit()
        self.file_filter_input.setPlaceholderText("Filter by file type (e.g., .pdf)...")

        # Add a filter button to apply all filters at once
        filter_button = QPushButton("Apply Filters")
        filter_button.clicked.connect(self.apply_filters)

        # Fixture/Contractor Toggle
        self.visibility_toggle = QCheckBox("Show Contractors Only")
        self.visibility_toggle.stateChanged.connect(self.toggle_supplier_visibility)

        filter_layout.addLayout(date_filter_layout)
        filter_layout.addWidget(self.file_filter_input)
        filter_layout.addWidget(self.visibility_toggle)
        filter_layout.addWidget(filter_button)
        filter_layout.addStretch()

        return filter_widget

    def apply_filters(self):
        """Applies all active filters to the current view by re-loading the data."""
        logger.info("Applying filters...")
        current_index = self.tree_view.currentIndex()
        if current_index.isValid():
            self.on_tree_item_selected(current_index)

    def toggle_supplier_visibility(self):
        """Shows/hides Fixture vs. Contractor nodes in the tree."""
        show_contractors_only = self.visibility_toggle.isChecked()
        logger.info(f"Toggling visibility: Show Contractors Only = {show_contractors_only}")

        root = self.tree_model.invisibleRootItem()
        for i in range(root.rowCount()):
            project_item = root.child(i)
            if not project_item.hasChildren():
                continue

            for j in range(project_item.rowCount()):
                category_item = project_item.child(j)
                if category_item is None: continue

                if category_item.text() == "Fixtures":
                    self.tree_view.setRowHidden(j, project_item.index(), show_contractors_only)
                elif category_item.text() == "Contractors":
                    # This ensures contractors are always visible if the toggle isn't on
                    self.tree_view.setRowHidden(j, project_item.index(), False)

    def filter_tree(self, text: str):
        """Filters the tree view to show only items matching the search text."""
        search_text = text.lower()
        root = self.tree_model.invisibleRootItem()

        for i in range(root.rowCount()): # Iterate through projects
            project_item = root.child(i)
            project_matches = search_text in project_item.text().lower()

            # If we haven't loaded the children yet, we can't check them
            if not project_item.hasChildren() or (project_item.hasChildren() and project_item.child(0).text() == ""):
                project_item.setHidden(not project_matches)
                continue

            any_child_matches = False
            for j in range(project_item.rowCount()): # Iterate through categories
                category_item = project_item.child(j)
                if not category_item: continue

                category_has_matching_child = False
                for k in range(category_item.rowCount()): # Iterate through suppliers
                    supplier_item = category_item.child(k)
                    if supplier_item and search_text in supplier_item.text().lower():
                        supplier_item.setHidden(False)
                        category_has_matching_child = True
                    elif supplier_item:
                        supplier_item.setHidden(True)

                if category_has_matching_child:
                    any_child_matches = True

                category_item.setHidden(not category_has_matching_child)

            # Hide the project if neither it nor any of its children match
            project_item.setHidden(not (project_matches or any_child_matches))

    def create_sidebar(self) -> QWidget:
        sidebar = QWidget()
        sidebar_layout = QVBoxLayout(sidebar)

        title_label = QLabel("Projects")
        title_label.setObjectName("TitleLabel") # For styling
        sidebar_layout.addWidget(title_label)

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search Project or Supplier...")
        self.search_bar.textChanged.connect(self.filter_tree)
        sidebar_layout.addWidget(self.search_bar)

        self.tree_view = QTreeView()
        self.tree_model = QStandardItemModel()
        self.tree_view.setModel(self.tree_model)
        self.tree_view.setHeaderHidden(True)
        self.tree_view.clicked.connect(self.on_tree_item_selected)
        sidebar_layout.addWidget(self.tree_view)

        return sidebar

    def create_content_area(self) -> QScrollArea:
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)

        content_widget = QWidget()
        self.content_layout = QVBoxLayout(content_widget)
        self.content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.placeholder_label = QLabel("Select a project or supplier to see details.")
        self.placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.content_layout.addWidget(self.placeholder_label)

        scroll_area.setWidget(content_widget)
        return scroll_area

    def load_projects(self, date_filter: dict = None):
        self.tree_model.clear()
        if self.dry_run:
            logger.info("Dry Run: Loading mock projects into tree.")
            for i in range(2):
                project_item = QStandardItem(f"Project 800{123+i}")
                project_item.setData({"type": "project", "number": f"800{123+i}"}, Qt.ItemDataRole.UserRole)
                project_item.appendRow(QStandardItem())
                self.tree_model.appendRow(project_item)
            return

        query = {}
        if date_filter:
            # This query assumes the 'last_scanned' field is what we filter by.
            # This could be adapted to filter by transmission or receipt dates.
            query["last_scanned"] = {
                "$gte": f"{date_filter['start']}T00:00:00Z",
                "$lte": f"{date_filter['end']}T23:59:59Z"
            }

        try:
            projects = self.db_manager.db.projects.find(query).sort("project_number", -1)
            for project in projects:
                project_item = QStandardItem(f"Project {project['project_number']}")
                project_item.setData(project, Qt.ItemDataRole.UserRole)
                project_item.setData("project", Qt.ItemDataRole.UserRole + 1)
                project_item.appendRow(QStandardItem())
                self.tree_model.appendRow(project_item)
            logger.info(f"Loaded {self.tree_model.rowCount()} projects matching filter.")
        except Exception as e:
            logger.error(f"Failed to load projects from MongoDB: {e}")

    def on_tree_item_selected(self, index):
        item = self.tree_model.itemFromIndex(index)
        item_data = item.data(Qt.ItemDataRole.UserRole)
        item_type = item.data(Qt.ItemDataRole.UserRole + 1)

        self.clear_content_area()

        if item_type == "project":
            # If the project item has the dummy child, it means we haven't loaded suppliers yet
            if item.hasChildren() and item.child(0).text() == "":
                self.load_suppliers_for_project(item, item_data['project_number'])
            # Display project-level summary
            self.display_project_summary(item_data)
        elif item_type == "supplier":
            # Display supplier-level details
            self.display_supplier_details(item_data)
        else:
            self.content_layout.addWidget(self.placeholder_label)

    def display_project_summary(self, project_data):
        """Displays a summary for the selected project."""
        title = QLabel(f"Project Summary: {project_data['project_number']}")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.content_layout.addWidget(title)
        # More project-level details can be added here later

    def display_supplier_details(self, supplier_data):
        """Displays the Sent/Received columns for a selected supplier."""
        self.current_file_widgets = [] # Reset the list of file widgets

        # Main container for the two columns and filter bar
        details_container = QWidget()
        container_layout = QVBoxLayout(details_container)

        # Filter bar
        filter_bar = QWidget()
        filter_layout = QHBoxLayout(filter_bar)
        file_filter_input = QLineEdit()
        file_filter_input.setPlaceholderText("Filter files by extension (e.g., .pdf)...")
        file_filter_input.textChanged.connect(self.filter_files_by_type)
        filter_layout.addWidget(file_filter_input)

        container_layout.addWidget(filter_bar)

        details_widget = QWidget()
        details_layout = QHBoxLayout(details_widget)
        details_layout.setSpacing(20)

        # Sent Column
        sent_widget = QWidget()
        sent_layout = QVBoxLayout(sent_widget)
        sent_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        sent_title = QLabel("Sent Transmissions")
        sent_title.setStyleSheet("font-size: 16px; font-weight: bold;")
        sent_layout.addWidget(sent_title)

        # Received Column
        received_widget = QWidget()
        received_layout = QVBoxLayout(received_widget)
        received_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        received_title = QLabel("Received Submissions")
        received_title.setStyleSheet("font-size: 16px; font-weight: bold;")
        received_layout.addWidget(received_title)

        # Get filter values
        start_date = self.start_date_edit.date().toString(Qt.DateFormat.ISODate)
        end_date = self.end_date_edit.date().toString(Qt.DateFormat.ISODate)
        file_filter = self.file_filter_input.text()

        # Build the query
        query = {
            "project_number": supplier_data["project_number"],
            "supplier_name": supplier_data["supplier_name"]
        }
        date_query_part = {"$gte": f"{start_date}T00:00:00Z", "$lte": f"{end_date}T23:59:59Z"}

        # Populate Sent column
        sent_query = query.copy()
        sent_query["sent_date"] = date_query_part
        if file_filter:
            sent_query["zip_name"] = {"$regex": file_filter, "$options": "i"}

        transmissions = self.db_manager.db.transmissions.find(sent_query)
        for trans in transmissions:
            sent_layout.addWidget(self.create_file_list_widget(trans, is_sent=True))

        # Populate Received column
        received_query = query.copy()
        received_query["received_date"] = date_query_part
        if file_filter:
            # This is a simplification; a real implementation would need to search inside the 'received_files' array
            received_query["received_folder_path"] = {"$regex": file_filter, "$options": "i"}

        receipts = self.db_manager.db.receipts.find(received_query)
        for receipt in receipts:
            received_layout.addWidget(self.create_file_list_widget(receipt, is_sent=False))

        details_layout.addWidget(sent_widget)
        details_layout.addWidget(received_widget)

        container_layout.addWidget(details_widget)
        self.content_layout.addWidget(details_container)
        self.content_layout.addStretch() # Pushes content to the top

    def filter_files_by_type(self, text: str):
        """Filters the file list widgets based on the input text."""
        filter_text = text.lower()
        for widget in self.current_file_widgets:
            # We assume the widget title is the filename we want to filter
            if filter_text in widget.toggle_button.text().lower():
                widget.setVisible(True)
            else:
                widget.setVisible(False)

    def create_file_list_widget(self, item_data: dict, is_sent: bool) -> CollapsibleWidget:
        """Creates a collapsible widget for a single transmission or receipt."""
        if is_sent:
            title = item_data['zip_name'] if isinstance(item_data, dict) else item_data
            files = item_data.get('source_files', []) if isinstance(item_data, dict) else ["mock_file1.pdf", "mock_file2.dwg"]
            base_path = os.path.dirname(item_data['zip_path']) if isinstance(item_data, dict) else "/mock/path"
        else:
            title = os.path.basename(item_data['received_folder_path']) if isinstance(item_data, dict) else item_data
            files = item_data.get('received_files', []) if isinstance(item_data, dict) else ["mock_response.docx"]
            base_path = item_data['received_folder_path'] if isinstance(item_data, dict) else "/mock/path"

        widget = CollapsibleWidget(title=title)
        content_layout = QVBoxLayout()

        if not files:
            content_layout.addWidget(QLabel("No source files found."))
        else:
            for file_path in files:
                file_name = os.path.basename(file_path)
                link_label = LinkLabel(file_name, os.path.join(base_path, file_name))
                content_layout.addWidget(link_label)

        widget.set_content_layout(content_layout)
        self.current_file_widgets.append(widget) # Store for filtering
        return widget

    def load_suppliers_for_project(self, project_item: QStandardItem, project_number: str):
        project_item.removeRow(0) # Remove dummy item
        logger.info(f"Lazily loading suppliers for project {project_number}...")

        fixtures_node = QStandardItem("Fixtures")
        contractors_node = QStandardItem("Contractors")

        suppliers = self.db_manager.db.suppliers.find({"project_number": project_number}).sort("supplier_name", 1)

        for supplier in suppliers:
            # Get counts for sent and received items
            sent_count = self.db_manager.db.transmissions.count_documents({"project_number": project_number, "supplier_name": supplier['supplier_name']})
            received_count = self.db_manager.db.receipts.count_documents({"project_number": project_number, "supplier_name": supplier['supplier_name']})

            # Format the display text
            display_text = f"{supplier['supplier_name']} (S: {sent_count}, R: {received_count})"
            supplier_item = QStandardItem(display_text)

            supplier_item.setData(supplier, Qt.ItemDataRole.UserRole)
            supplier_item.setData("supplier", Qt.ItemDataRole.UserRole + 1)

            if supplier.get('category') == 'Fixture':
                fixtures_node.appendRow(supplier_item)
            elif supplier.get('category') == 'Contractor':
                contractors_node.appendRow(supplier_item)

        if fixtures_node.rowCount() > 0:
            project_item.appendRow(fixtures_node)
        if contractors_node.rowCount() > 0:
            project_item.appendRow(contractors_node)

    def clear_content_area(self):
        while self.content_layout.count():
            child = self.content_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def get_stylesheet(self) -> str:
        return """
            QWidget {
                background-color: #2b2b2b; /* Darker background */
                color: #dcdcdc; /* Lighter text */
                font-family: "Segoe UI", "Arial";
                font-size: 14px;
            }
            QMainWindow {
                background-color: #2b2b2b;
            }
            QSplitter::handle {
                background-color: #3c3f41;
            }
            QTreeView {
                background-color: #2b2b2b;
                border: 1px solid #3c3f41;
                font-size: 15px;
            }
            QTreeView::item {
                padding: 8px;
            }
            QTreeView::item:selected {
                background-color: #4a6984; /* A more subtle selection color */
            }
            QTreeView::branch {
                background: transparent;
            }
            QLabel#TitleLabel {
                font-size: 20px;
                font-weight: bold;
                margin-bottom: 10px;
                color: #5daee7; /* Accent color for titles */
            }
            QLabel#SectionTitle {
                font-size: 16px;
                font-weight: bold;
                color: #cccccc;
                margin-top: 5px;
                margin-bottom: 5px;
            }
            QLineEdit {
                background-color: #3c3f41;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 6px;
            }
            QPushButton {
                background-color: #5daee7;
                color: #ffffff;
                border: none;
                border-radius: 4px;
                padding: 8px 12px;
            }
            QPushButton:hover {
                background-color: #73b8e8;
            }
            QDateEdit {
                background-color: #3c3f41;
                border: 1px solid #555;
                padding: 5px;
            }
            QDateEdit::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 15px;
                border-left-width: 1px;
                border-left-color: darkgray;
                border-left-style: solid;
            }
            QScrollArea {
                border: none;
            }
        """