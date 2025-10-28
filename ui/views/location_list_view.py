"""
Location List View - Shows all locations in a project
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget,
    QListWidgetItem, QLabel, QLineEdit, QMessageBox
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QFont
from typing import List
from models.location import Location


class LocationListView(QWidget):
    """
    List view for locations with search and management
    """

    # Signals
    location_selected = Signal(str)  # location_id
    add_location_requested = Signal()
    edit_location_requested = Signal(str)  # location_id
    delete_location_requested = Signal(str)  # location_id

    def __init__(self, parent=None):
        super().__init__(parent)
        self._locations: List[Location] = []
        self._filtered_locations: List[Location] = []
        self._setup_ui()

    def _setup_ui(self):
        """Setup the UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Header
        header = QLabel("🗺️ Locations")
        header.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        layout.addWidget(header)

        # Search bar
        search_layout = QHBoxLayout()
        search_layout.setSpacing(10)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search locations...")
        self.search_input.textChanged.connect(self._on_search_changed)
        search_layout.addWidget(self.search_input)

        self.clear_search_btn = QPushButton("Clear")
        self.clear_search_btn.setMaximumWidth(80)
        self.clear_search_btn.clicked.connect(self._clear_search)
        search_layout.addWidget(self.clear_search_btn)

        layout.addLayout(search_layout)

        # Location list
        self.location_list = QListWidget()
        self.location_list.setAlternatingRowColors(True)
        self.location_list.itemClicked.connect(self._on_location_clicked)
        self.location_list.itemDoubleClicked.connect(self._on_location_double_clicked)
        self.location_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 5px;
                background-color: white;
            }
            QListWidget::item {
                padding: 8px;
                border-radius: 3px;
            }
            QListWidget::item:selected {
                background-color: #2196F3;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #e3f2fd;
            }
        """)
        layout.addWidget(self.location_list)

        # Stats
        self.stats_label = QLabel("0 locations")
        self.stats_label.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(self.stats_label)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        self.add_btn = QPushButton("➕ Add Location")
        self.add_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.add_btn.clicked.connect(self.add_location_requested.emit)
        button_layout.addWidget(self.add_btn)

        self.edit_btn = QPushButton("✏️ Edit")
        self.edit_btn.setEnabled(False)
        self.edit_btn.clicked.connect(self._on_edit_clicked)
        button_layout.addWidget(self.edit_btn)

        self.delete_btn = QPushButton("🗑️ Delete")
        self.delete_btn.setEnabled(False)
        self.delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
            QPushButton:disabled {
                background-color: #ccc;
            }
        """)
        self.delete_btn.clicked.connect(self._on_delete_clicked)
        button_layout.addWidget(self.delete_btn)

        layout.addLayout(button_layout)

    def load_locations(self, locations: List[Location]):
        """
        Load locations into the list

        Args:
            locations: List of Location objects
        """
        self._locations = locations
        self._filtered_locations = locations.copy()
        self._refresh_list()

    def _refresh_list(self):
        """Refresh the location list widget"""
        self.location_list.clear()

        for location in self._filtered_locations:
            item = QListWidgetItem()

            # Display format: icon + name + type
            location_type = location.location_type if location.location_type else "generic"
            display_text = f"📍 {location.name}"
            if location.location_type:
                display_text += f" ({location_type})"

            # Show parent if exists
            if location.parent_location_id:
                parent = self._find_location_by_id(location.parent_location_id)
                if parent:
                    display_text += f" ⊂ {parent.name}"

            item.setText(display_text)
            item.setData(Qt.ItemDataRole.UserRole, location.id)

            self.location_list.addItem(item)

        # Update stats
        total = len(self._locations)
        filtered = len(self._filtered_locations)
        if filtered == total:
            self.stats_label.setText(f"{total} location{'s' if total != 1 else ''}")
        else:
            self.stats_label.setText(f"{filtered} of {total} locations")

    def _find_location_by_id(self, location_id: str) -> Location:
        """Find location by ID"""
        for loc in self._locations:
            if loc.id == location_id:
                return loc
        return None

    def _on_search_changed(self, text: str):
        """Filter locations based on search text"""
        search_text = text.lower().strip()

        if not search_text:
            self._filtered_locations = self._locations.copy()
        else:
            self._filtered_locations = [
                loc for loc in self._locations
                if search_text in loc.name.lower() or
                   search_text in loc.description.lower() or
                   (loc.location_type and search_text in loc.location_type.lower())
            ]

        self._refresh_list()

    def _clear_search(self):
        """Clear search input"""
        self.search_input.clear()

    def _on_location_clicked(self, item: QListWidgetItem):
        """Handle location click"""
        location_id = item.data(Qt.ItemDataRole.UserRole)
        self.edit_btn.setEnabled(True)
        self.delete_btn.setEnabled(True)
        self.location_selected.emit(location_id)

    def _on_location_double_clicked(self, item: QListWidgetItem):
        """Handle location double-click (edit)"""
        location_id = item.data(Qt.ItemDataRole.UserRole)
        self.edit_location_requested.emit(location_id)

    def _on_edit_clicked(self):
        """Handle edit button click"""
        current_item = self.location_list.currentItem()
        if current_item:
            location_id = current_item.data(Qt.ItemDataRole.UserRole)
            self.edit_location_requested.emit(location_id)

    def _on_delete_clicked(self):
        """Handle delete button click"""
        current_item = self.location_list.currentItem()
        if not current_item:
            return

        location_id = current_item.data(Qt.ItemDataRole.UserRole)

        # Find location name for confirmation
        location = self._find_location_by_id(location_id)
        if not location:
            return

        # Confirm deletion
        reply = QMessageBox.question(
            self,
            "Delete Location",
            f"Are you sure you want to delete '{location.name}'?\n\nThis action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.delete_location_requested.emit(location_id)

    def select_location(self, location_id: str):
        """
        Programmatically select a location

        Args:
            location_id: Location ID to select
        """
        for i in range(self.location_list.count()):
            item = self.location_list.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == location_id:
                self.location_list.setCurrentItem(item)
                self.edit_btn.setEnabled(True)
                self.delete_btn.setEnabled(True)
                break

    def clear_selection(self):
        """Clear current selection"""
        self.location_list.clearSelection()
        self.edit_btn.setEnabled(False)
        self.delete_btn.setEnabled(False)
