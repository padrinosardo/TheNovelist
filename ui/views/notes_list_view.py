"""
Notes List View - Shows all generic notes in a project
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget,
    QListWidgetItem, QLabel, QLineEdit, QCheckBox, QMessageBox
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QFont, QColor
from typing import List
from models.note import Note


class NotesListView(QWidget):
    """
    List view for generic notes with search, filter by pinned, and management
    """

    # Signals
    note_selected = Signal(str)  # note_id
    add_note_requested = Signal()
    edit_note_requested = Signal(str)  # note_id
    delete_note_requested = Signal(str)  # note_id
    toggle_pin_requested = Signal(str)  # note_id

    def __init__(self, parent=None):
        super().__init__(parent)
        self._notes: List[Note] = []
        self._filtered_notes: List[Note] = []
        self._setup_ui()

    def _setup_ui(self):
        """Setup the UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Header
        header = QLabel("📝 Notes")
        header.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        layout.addWidget(header)

        # Search and filter bar
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(10)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search notes...")
        self.search_input.textChanged.connect(self._on_filter_changed)
        filter_layout.addWidget(self.search_input)

        self.pinned_only_checkbox = QCheckBox("Pinned Only")
        self.pinned_only_checkbox.stateChanged.connect(self._on_filter_changed)
        filter_layout.addWidget(self.pinned_only_checkbox)

        self.clear_filter_btn = QPushButton("Clear")
        self.clear_filter_btn.setMaximumWidth(80)
        self.clear_filter_btn.clicked.connect(self._clear_filters)
        filter_layout.addWidget(self.clear_filter_btn)

        layout.addLayout(filter_layout)

        # Notes list
        self.notes_list = QListWidget()
        self.notes_list.setAlternatingRowColors(True)
        self.notes_list.itemClicked.connect(self._on_note_clicked)
        self.notes_list.itemDoubleClicked.connect(self._on_note_double_clicked)
        self.notes_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 5px;
                background-color: white;
            }
            QListWidget::item {
                padding: 10px;
                border-radius: 3px;
                margin: 2px;
                color: #333;
            }
            QListWidget::item:selected {
                background-color: #2196F3;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #e3f2fd;
                color: #333;
            }
        """)
        layout.addWidget(self.notes_list)

        # Stats
        self.stats_label = QLabel("0 notes")
        self.stats_label.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(self.stats_label)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        self.add_btn = QPushButton("➕ Add Note")
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
        self.add_btn.clicked.connect(self.add_note_requested.emit)
        button_layout.addWidget(self.add_btn)

        self.edit_btn = QPushButton("✏️ Edit")
        self.edit_btn.setEnabled(False)
        self.edit_btn.clicked.connect(self._on_edit_clicked)
        button_layout.addWidget(self.edit_btn)

        self.pin_btn = QPushButton("📌 Toggle Pin")
        self.pin_btn.setEnabled(False)
        self.pin_btn.clicked.connect(self._on_toggle_pin_clicked)
        button_layout.addWidget(self.pin_btn)

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

    def load_notes(self, notes: List[Note]):
        """
        Load notes into the list

        Args:
            notes: List of Note objects
        """
        self._notes = notes
        self._filtered_notes = notes.copy()
        self._refresh_list()

    def _refresh_list(self):
        """Refresh the notes list widget"""
        self.notes_list.clear()

        # Sort: pinned first, then by title
        sorted_notes = sorted(
            self._filtered_notes,
            key=lambda n: (not n.pinned, n.title.lower())
        )

        for note in sorted_notes:
            item = QListWidgetItem()

            # Display format: pin + title + tags preview
            display_text = ""

            if note.pinned:
                display_text += "📌 "

            display_text += note.title

            if note.tags:
                tags_preview = ", ".join(note.tags[:3])
                if len(note.tags) > 3:
                    tags_preview += "..."
                display_text += f"\n   🏷️ {tags_preview}"

            # Show linked entities
            links = []
            if note.linked_to_scene:
                links.append("Scene")
            if note.linked_to_character:
                links.append("Character")
            if note.linked_to_location:
                links.append("Location")

            if links:
                display_text += f"\n   🔗 Linked to: {', '.join(links)}"

            item.setText(display_text)
            item.setData(Qt.ItemDataRole.UserRole, note.id)

            # Apply color if set
            if note.color:
                try:
                    color = QColor(note.color)
                    item.setBackground(color)
                    # Use contrasting text color
                    brightness = color.red() * 0.299 + color.green() * 0.587 + color.blue() * 0.114
                    if brightness < 128:
                        item.setForeground(QColor("white"))
                except:
                    pass  # Invalid color

            self.notes_list.addItem(item)

        # Update stats
        total = len(self._notes)
        filtered = len(self._filtered_notes)
        pinned_count = sum(1 for n in self._notes if n.pinned)

        stats_text = f"{total} note{'s' if total != 1 else ''}"
        if pinned_count > 0:
            stats_text += f" ({pinned_count} pinned)"

        if filtered != total:
            stats_text = f"{filtered} of " + stats_text

        self.stats_label.setText(stats_text)

    def _on_filter_changed(self):
        """Apply search and pinned filters"""
        search_text = self.search_input.text().lower().strip()
        pinned_only = self.pinned_only_checkbox.isChecked()

        self._filtered_notes = []

        for note in self._notes:
            # Pinned filter
            if pinned_only and not note.pinned:
                continue

            # Search filter
            if search_text:
                matches = (
                    search_text in note.title.lower() or
                    search_text in note.content.lower() or
                    any(search_text in tag.lower() for tag in note.tags)
                )
                if not matches:
                    continue

            self._filtered_notes.append(note)

        self._refresh_list()

    def _clear_filters(self):
        """Clear all filters"""
        self.search_input.clear()
        self.pinned_only_checkbox.setChecked(False)

    def _on_note_clicked(self, item: QListWidgetItem):
        """Handle note click"""
        note_id = item.data(Qt.ItemDataRole.UserRole)
        self.edit_btn.setEnabled(True)
        self.delete_btn.setEnabled(True)
        self.pin_btn.setEnabled(True)
        self.note_selected.emit(note_id)

    def _on_note_double_clicked(self, item: QListWidgetItem):
        """Handle note double-click (edit)"""
        note_id = item.data(Qt.ItemDataRole.UserRole)
        self.edit_note_requested.emit(note_id)

    def _on_edit_clicked(self):
        """Handle edit button click"""
        current_item = self.notes_list.currentItem()
        if current_item:
            note_id = current_item.data(Qt.ItemDataRole.UserRole)
            self.edit_note_requested.emit(note_id)

    def _on_toggle_pin_clicked(self):
        """Handle toggle pin button click"""
        current_item = self.notes_list.currentItem()
        if current_item:
            note_id = current_item.data(Qt.ItemDataRole.UserRole)
            self.toggle_pin_requested.emit(note_id)

    def _on_delete_clicked(self):
        """Handle delete button click"""
        current_item = self.notes_list.currentItem()
        if not current_item:
            return

        note_id = current_item.data(Qt.ItemDataRole.UserRole)

        # Find note for confirmation
        note = None
        for n in self._notes:
            if n.id == note_id:
                note = n
                break

        if not note:
            return

        # Confirm deletion
        reply = QMessageBox.question(
            self,
            "Delete Note",
            f"Are you sure you want to delete '{note.title}'?\n\nThis action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.delete_note_requested.emit(note_id)

    def select_note(self, note_id: str):
        """
        Programmatically select a note

        Args:
            note_id: Note ID to select
        """
        for i in range(self.notes_list.count()):
            item = self.notes_list.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == note_id:
                self.notes_list.setCurrentItem(item)
                self.edit_btn.setEnabled(True)
                self.delete_btn.setEnabled(True)
                self.pin_btn.setEnabled(True)
                break

    def clear_selection(self):
        """Clear current selection"""
        self.notes_list.clearSelection()
        self.edit_btn.setEnabled(False)
        self.delete_btn.setEnabled(False)
        self.pin_btn.setEnabled(False)
