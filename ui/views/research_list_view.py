"""
Research List View - Shows all research notes in a project
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget,
    QListWidgetItem, QLabel, QLineEdit, QComboBox, QMessageBox
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QFont
from typing import List
from models.research_note import ResearchNote


class ResearchListView(QWidget):
    """
    List view for research notes with search, filter, and management
    """

    # Signals
    research_selected = Signal(str)  # research_id
    add_research_requested = Signal()
    edit_research_requested = Signal(str)  # research_id
    delete_research_requested = Signal(str)  # research_id

    def __init__(self, parent=None):
        super().__init__(parent)
        self._research_notes: List[ResearchNote] = []
        self._filtered_notes: List[ResearchNote] = []
        self._categories: List[str] = []
        self._setup_ui()

    def _setup_ui(self):
        """Setup the UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Header
        header = QLabel("🔍 Research Notes")
        header.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        layout.addWidget(header)

        # Search and filter bar
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(10)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search research notes...")
        self.search_input.textChanged.connect(self._on_filter_changed)
        filter_layout.addWidget(self.search_input, stretch=2)

        self.category_filter = QComboBox()
        self.category_filter.addItem("All Categories", "")
        self.category_filter.currentIndexChanged.connect(self._on_filter_changed)
        filter_layout.addWidget(self.category_filter, stretch=1)

        self.clear_filter_btn = QPushButton("Clear")
        self.clear_filter_btn.setMaximumWidth(80)
        self.clear_filter_btn.clicked.connect(self._clear_filters)
        filter_layout.addWidget(self.clear_filter_btn)

        layout.addLayout(filter_layout)

        # Research list
        self.research_list = QListWidget()
        self.research_list.setAlternatingRowColors(True)
        self.research_list.itemClicked.connect(self._on_research_clicked)
        self.research_list.itemDoubleClicked.connect(self._on_research_double_clicked)
        self.research_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 5px;
                background-color: white;
            }
            QListWidget::item {
                padding: 10px;
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
        layout.addWidget(self.research_list)

        # Stats
        self.stats_label = QLabel("0 research notes")
        self.stats_label.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(self.stats_label)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        self.add_btn = QPushButton("➕ Add Research Note")
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
        self.add_btn.clicked.connect(self.add_research_requested.emit)
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

    def load_research_notes(self, research_notes: List[ResearchNote]):
        """
        Load research notes into the list

        Args:
            research_notes: List of ResearchNote objects
        """
        self._research_notes = research_notes
        self._filtered_notes = research_notes.copy()

        # Extract unique categories
        self._categories = sorted(list(set(
            note.category for note in research_notes if note.category
        )))

        # Update category filter
        current_category = self.category_filter.currentData()
        self.category_filter.clear()
        self.category_filter.addItem("All Categories", "")
        for category in self._categories:
            self.category_filter.addItem(f"📁 {category}", category)

        # Restore selection if possible
        if current_category:
            index = self.category_filter.findData(current_category)
            if index >= 0:
                self.category_filter.setCurrentIndex(index)

        self._refresh_list()

    def _refresh_list(self):
        """Refresh the research list widget"""
        self.research_list.clear()

        for note in self._filtered_notes:
            item = QListWidgetItem()

            # Display format: title + category + tags preview
            display_text = f"📝 {note.title}"

            if note.category:
                display_text += f" [{note.category}]"

            if note.tags:
                tags_preview = ", ".join(note.tags[:3])
                if len(note.tags) > 3:
                    tags_preview += "..."
                display_text += f"\n   🏷️ {tags_preview}"

            if note.sources:
                source_count = len(note.sources)
                display_text += f"\n   🔗 {source_count} source{'s' if source_count != 1 else ''}"

            item.setText(display_text)
            item.setData(Qt.ItemDataRole.UserRole, note.id)

            self.research_list.addItem(item)

        # Update stats
        total = len(self._research_notes)
        filtered = len(self._filtered_notes)
        if filtered == total:
            self.stats_label.setText(f"{total} research note{'s' if total != 1 else ''}")
        else:
            self.stats_label.setText(f"{filtered} of {total} research notes")

    def _on_filter_changed(self):
        """Apply search and category filters"""
        search_text = self.search_input.text().lower().strip()
        category_filter = self.category_filter.currentData()

        self._filtered_notes = []

        for note in self._research_notes:
            # Category filter
            if category_filter and note.category != category_filter:
                continue

            # Search filter
            if search_text:
                matches = (
                    search_text in note.title.lower() or
                    search_text in note.content.lower() or
                    (note.category and search_text in note.category.lower()) or
                    any(search_text in tag.lower() for tag in note.tags)
                )
                if not matches:
                    continue

            self._filtered_notes.append(note)

        self._refresh_list()

    def _clear_filters(self):
        """Clear all filters"""
        self.search_input.clear()
        self.category_filter.setCurrentIndex(0)

    def _on_research_clicked(self, item: QListWidgetItem):
        """Handle research note click"""
        research_id = item.data(Qt.ItemDataRole.UserRole)
        self.edit_btn.setEnabled(True)
        self.delete_btn.setEnabled(True)
        self.research_selected.emit(research_id)

    def _on_research_double_clicked(self, item: QListWidgetItem):
        """Handle research note double-click (edit)"""
        research_id = item.data(Qt.ItemDataRole.UserRole)
        self.edit_research_requested.emit(research_id)

    def _on_edit_clicked(self):
        """Handle edit button click"""
        current_item = self.research_list.currentItem()
        if current_item:
            research_id = current_item.data(Qt.ItemDataRole.UserRole)
            self.edit_research_requested.emit(research_id)

    def _on_delete_clicked(self):
        """Handle delete button click"""
        current_item = self.research_list.currentItem()
        if not current_item:
            return

        research_id = current_item.data(Qt.ItemDataRole.UserRole)

        # Find research note for confirmation
        note = None
        for n in self._research_notes:
            if n.id == research_id:
                note = n
                break

        if not note:
            return

        # Confirm deletion
        reply = QMessageBox.question(
            self,
            "Delete Research Note",
            f"Are you sure you want to delete '{note.title}'?\n\nThis action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.delete_research_requested.emit(research_id)

    def select_research(self, research_id: str):
        """
        Programmatically select a research note

        Args:
            research_id: Research note ID to select
        """
        for i in range(self.research_list.count()):
            item = self.research_list.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == research_id:
                self.research_list.setCurrentItem(item)
                self.edit_btn.setEnabled(True)
                self.delete_btn.setEnabled(True)
                break

    def clear_selection(self):
        """Clear current selection"""
        self.research_list.clearSelection()
        self.edit_btn.setEnabled(False)
        self.delete_btn.setEnabled(False)
