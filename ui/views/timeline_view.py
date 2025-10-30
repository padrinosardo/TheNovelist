"""
Timeline View - Shows chronological events in the story
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget,
    QListWidgetItem, QLabel, QLineEdit, QMessageBox, QComboBox
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QFont
from typing import List
from models.timeline_event import TimelineEvent


class TimelineView(QWidget):
    """
    Timeline view showing story events in chronological order
    """

    # Signals
    event_selected = Signal(str)  # event_id
    add_event_requested = Signal()
    edit_event_requested = Signal(str)  # event_id
    delete_event_requested = Signal(str)  # event_id

    def __init__(self, parent=None):
        super().__init__(parent)
        self._events: List[TimelineEvent] = []
        self._filtered_events: List[TimelineEvent] = []
        self._setup_ui()

    def _setup_ui(self):
        """Setup the UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Header
        header = QLabel("⏱️ Story Timeline")
        header.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        layout.addWidget(header)

        # Search and filters bar
        search_layout = QHBoxLayout()
        search_layout.setSpacing(10)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search events...")
        self.search_input.textChanged.connect(self._on_search_changed)
        search_layout.addWidget(self.search_input)

        # Character filter
        self.character_filter = QComboBox()
        self.character_filter.addItem("All Characters", "")
        self.character_filter.setMinimumWidth(150)
        self.character_filter.currentIndexChanged.connect(self._on_filter_changed)
        search_layout.addWidget(self.character_filter)

        # Location filter
        self.location_filter = QComboBox()
        self.location_filter.addItem("All Locations", "")
        self.location_filter.setMinimumWidth(150)
        self.location_filter.currentIndexChanged.connect(self._on_filter_changed)
        search_layout.addWidget(self.location_filter)

        self.clear_filters_btn = QPushButton("Clear Filters")
        self.clear_filters_btn.setMaximumWidth(120)
        self.clear_filters_btn.clicked.connect(self._clear_filters)
        search_layout.addWidget(self.clear_filters_btn)

        layout.addLayout(search_layout)

        # Timeline list (chronological order)
        self.timeline_list = QListWidget()
        self.timeline_list.setAlternatingRowColors(True)
        self.timeline_list.itemClicked.connect(self._on_event_clicked)
        self.timeline_list.itemDoubleClicked.connect(self._on_event_double_clicked)
        self.timeline_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 5px;
                background-color: white;
            }
            QListWidget::item {
                padding: 10px;
                border-left: 4px solid #2196F3;
                margin: 3px;
                border-radius: 3px;
                color: #333;
            }
            QListWidget::item:selected {
                background-color: #2196F3;
                color: white;
                border-left: 4px solid #0D47A1;
            }
            QListWidget::item:hover {
                background-color: #e3f2fd;
                color: #333;
            }
        """)
        layout.addWidget(self.timeline_list)

        # Stats
        self.stats_label = QLabel("0 events")
        self.stats_label.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(self.stats_label)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        self.add_btn = QPushButton("➕ Add Event")
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
        self.add_btn.clicked.connect(self.add_event_requested.emit)
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

    def load_events(self, events: List[TimelineEvent], characters=None, locations=None):
        """
        Load timeline events and sort chronologically

        Args:
            events: List of TimelineEvent objects
            characters: List of Character objects (optional, for filter)
            locations: List of Location objects (optional, for filter)
        """
        # Sort chronologically by date (oldest first)
        # Events without dates go to the end
        def sort_key(event):
            if not event.date:
                return (1, "")  # No date goes last
            return (0, event.date.lower())

        self._events = sorted(events, key=sort_key)
        self._filtered_events = self._events.copy()

        # Update character filter
        self.character_filter.clear()
        self.character_filter.addItem("All Characters", "")
        if characters:
            for char in characters:
                self.character_filter.addItem(f"👤 {char.name}", char.id)

        # Update location filter
        self.location_filter.clear()
        self.location_filter.addItem("All Locations", "")
        if locations:
            for loc in locations:
                self.location_filter.addItem(f"📍 {loc.name}", loc.id)

        self._refresh_list()

    def _refresh_list(self):
        """Refresh the timeline list widget"""
        self.timeline_list.clear()

        for event in self._filtered_events:
            item = QListWidgetItem()

            # Display format: date + title + description preview
            display_text = f"📅 {event.date if event.date else 'No date'}\n"
            display_text += f"   {event.title}"

            if event.description:
                # Preview first 50 chars of description
                preview = event.description[:50]
                if len(event.description) > 50:
                    preview += "..."
                display_text += f"\n   {preview}"

            # Show related entities
            entity_info = []
            if event.characters:
                entity_info.append(f"{len(event.characters)} character(s)")
            if event.locations:
                entity_info.append(f"{len(event.locations)} location(s)")

            if entity_info:
                display_text += f"\n   🔗 {', '.join(entity_info)}"

            item.setText(display_text)
            item.setData(Qt.ItemDataRole.UserRole, event.id)

            self.timeline_list.addItem(item)

        # Update stats
        total = len(self._events)
        filtered = len(self._filtered_events)
        if filtered == total:
            self.stats_label.setText(f"{total} event{'s' if total != 1 else ''}")
        else:
            self.stats_label.setText(f"{filtered} of {total} events")

    def _on_search_changed(self, text: str):
        """Filter events based on search text and active filters"""
        self._apply_filters()

    def _on_filter_changed(self):
        """Handle filter combo box changes"""
        self._apply_filters()

    def _apply_filters(self):
        """Apply all active filters (search, character, location)"""
        search_text = self.search_input.text().lower().strip()
        selected_char_id = self.character_filter.currentData()
        selected_loc_id = self.location_filter.currentData()

        self._filtered_events = []

        for event in self._events:
            # Search filter
            if search_text:
                if not (search_text in event.title.lower() or
                       search_text in event.description.lower() or
                       (event.date and search_text in event.date.lower())):
                    continue

            # Character filter
            if selected_char_id:
                if selected_char_id not in event.characters:
                    continue

            # Location filter
            if selected_loc_id:
                if selected_loc_id not in event.locations:
                    continue

            self._filtered_events.append(event)

        self._refresh_list()

    def _clear_filters(self):
        """Clear all filters"""
        self.search_input.clear()
        self.character_filter.setCurrentIndex(0)
        self.location_filter.setCurrentIndex(0)

    def _on_event_clicked(self, item: QListWidgetItem):
        """Handle event click"""
        event_id = item.data(Qt.ItemDataRole.UserRole)
        self.edit_btn.setEnabled(True)
        self.delete_btn.setEnabled(True)
        self.event_selected.emit(event_id)

    def _on_event_double_clicked(self, item: QListWidgetItem):
        """Handle event double-click (edit)"""
        event_id = item.data(Qt.ItemDataRole.UserRole)
        self.edit_event_requested.emit(event_id)

    def _on_edit_clicked(self):
        """Handle edit button click"""
        current_item = self.timeline_list.currentItem()
        if current_item:
            event_id = current_item.data(Qt.ItemDataRole.UserRole)
            self.edit_event_requested.emit(event_id)

    def _on_delete_clicked(self):
        """Handle delete button click"""
        current_item = self.timeline_list.currentItem()
        if not current_item:
            return

        event_id = current_item.data(Qt.ItemDataRole.UserRole)

        # Find event for confirmation
        event = None
        for e in self._events:
            if e.id == event_id:
                event = e
                break

        if not event:
            return

        # Confirm deletion
        reply = QMessageBox.question(
            self,
            "Delete Timeline Event",
            f"Are you sure you want to delete '{event.title}'?\n\nThis action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.delete_event_requested.emit(event_id)

    def select_event(self, event_id: str):
        """
        Programmatically select an event

        Args:
            event_id: Event ID to select
        """
        for i in range(self.timeline_list.count()):
            item = self.timeline_list.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == event_id:
                self.timeline_list.setCurrentItem(item)
                current_row = i
                self.edit_btn.setEnabled(True)
                self.delete_btn.setEnabled(True)
                self.move_up_btn.setEnabled(current_row > 0)
                self.move_down_btn.setEnabled(current_row < self.timeline_list.count() - 1)
                break

    def clear_selection(self):
        """Clear current selection"""
        self.timeline_list.clearSelection()
        self.edit_btn.setEnabled(False)
        self.delete_btn.setEnabled(False)
        self.move_up_btn.setEnabled(False)
        self.move_down_btn.setEnabled(False)
