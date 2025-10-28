"""
Timeline View - Shows chronological events in the story
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget,
    QListWidgetItem, QLabel, QLineEdit, QMessageBox
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
    move_up_requested = Signal(str)  # event_id
    move_down_requested = Signal(str)  # event_id

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

        # Search bar
        search_layout = QHBoxLayout()
        search_layout.setSpacing(10)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search events...")
        self.search_input.textChanged.connect(self._on_search_changed)
        search_layout.addWidget(self.search_input)

        self.clear_search_btn = QPushButton("Clear")
        self.clear_search_btn.setMaximumWidth(80)
        self.clear_search_btn.clicked.connect(self._clear_search)
        search_layout.addWidget(self.clear_search_btn)

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
            }
            QListWidget::item:selected {
                background-color: #2196F3;
                color: white;
                border-left: 4px solid #0D47A1;
            }
            QListWidget::item:hover {
                background-color: #e3f2fd;
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

        self.move_up_btn = QPushButton("⬆️ Move Up")
        self.move_up_btn.setEnabled(False)
        self.move_up_btn.clicked.connect(self._on_move_up_clicked)
        button_layout.addWidget(self.move_up_btn)

        self.move_down_btn = QPushButton("⬇️ Move Down")
        self.move_down_btn.setEnabled(False)
        self.move_down_btn.clicked.connect(self._on_move_down_clicked)
        button_layout.addWidget(self.move_down_btn)

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

    def load_events(self, events: List[TimelineEvent]):
        """
        Load timeline events

        Args:
            events: List of TimelineEvent objects (should be sorted by sort_order)
        """
        self._events = sorted(events, key=lambda e: e.sort_order)
        self._filtered_events = self._events.copy()
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
        """Filter events based on search text"""
        search_text = text.lower().strip()

        if not search_text:
            self._filtered_events = self._events.copy()
        else:
            self._filtered_events = [
                event for event in self._events
                if search_text in event.title.lower() or
                   search_text in event.description.lower() or
                   (event.date and search_text in event.date.lower())
            ]

        self._refresh_list()

    def _clear_search(self):
        """Clear search input"""
        self.search_input.clear()

    def _on_event_clicked(self, item: QListWidgetItem):
        """Handle event click"""
        event_id = item.data(Qt.ItemDataRole.UserRole)
        self.edit_btn.setEnabled(True)
        self.delete_btn.setEnabled(True)

        # Enable/disable move buttons based on position
        current_row = self.timeline_list.row(item)
        self.move_up_btn.setEnabled(current_row > 0)
        self.move_down_btn.setEnabled(current_row < self.timeline_list.count() - 1)

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

    def _on_move_up_clicked(self):
        """Move event up in timeline"""
        current_item = self.timeline_list.currentItem()
        if current_item:
            event_id = current_item.data(Qt.ItemDataRole.UserRole)
            self.move_up_requested.emit(event_id)

    def _on_move_down_clicked(self):
        """Move event down in timeline"""
        current_item = self.timeline_list.currentItem()
        if current_item:
            event_id = current_item.data(Qt.ItemDataRole.UserRole)
            self.move_down_requested.emit(event_id)

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
