from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve

class CollapsibleWidget(QWidget):
    """
    A custom widget that can be collapsed or expanded, with an animation.
    It contains a header (always visible) and a content area (collapsible).
    """
    def __init__(self, title: str = "", parent: QWidget = None):
        super().__init__(parent)
        self.is_expanded = False

        # Main layout for this widget
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Header (always visible)
        self.header = QWidget()
        self.header_layout = QHBoxLayout(self.header)
        self.header_layout.setContentsMargins(10, 10, 10, 10)

        self.toggle_button = QPushButton(title)
        self.toggle_button.setStyleSheet("text-align: left; font-weight: bold; font-size: 16px; border: none;")
        self.toggle_button.clicked.connect(self.toggle)

        self.header_layout.addWidget(self.toggle_button)
        self.header_layout.addStretch()

        # Content area (collapsible)
        self.content_area = QWidget()
        self.content_layout = QVBoxLayout(self.content_area)
        self.content_layout.setContentsMargins(10, 10, 10, 10)

        # Initially, content area is hidden
        self.content_area.setVisible(False)
        self.content_area.setFixedHeight(0)

        # Add header and content to the main layout
        main_layout.addWidget(self.header)
        main_layout.addWidget(self.content_area)

        # Animation setup
        self.animation = QPropertyAnimation(self.content_area, b"maximumHeight")
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutCubic)

    def set_content_layout(self, layout: QVBoxLayout):
        """Sets the layout for the content area."""
        # Clear existing layout
        while self.content_layout.count():
            child = self.content_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Add new layout's widgets to our content layout
        temp_widget = QWidget()
        temp_widget.setLayout(layout)
        self.content_layout.addWidget(temp_widget)

    def toggle(self):
        """Toggles the visibility of the content area with an animation."""
        self.is_expanded = not self.is_expanded

        start_height = self.content_area.height()
        end_height = self.content_layout.sizeHint().height() if self.is_expanded else 0

        self.animation.setStartValue(start_height)
        self.animation.setEndValue(end_height)

        # Make content area visible before starting the expansion animation
        if self.is_expanded:
            self.content_area.setVisible(True)

        self.animation.start()

        # Hide content area after the collapse animation finishes
        if not self.is_expanded:
            self.animation.finished.connect(lambda: self.content_area.setVisible(False))