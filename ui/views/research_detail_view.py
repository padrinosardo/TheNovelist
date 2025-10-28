"""
Research Detail View - Edit/view a single research note
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel,
    QLineEdit, QTextEdit, QComboBox, QPushButton, QScrollArea,
    QFrame, QListWidget, QListWidgetItem, QMessageBox, QInputDialog
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QFont
from typing import List, Optional
from models.research_note import ResearchNote


class ResearchDetailView(QWidget):
    """
    Detail view for editing/viewing a research note
    """

    # Signals
    save_requested = Signal(ResearchNote)  # Updated research note
    cancel_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_note: Optional[ResearchNote] = None
        self._all_categories: List[str] = []
        self._setup_ui()

    def _setup_ui(self):
        """Setup the UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Scroll area for long content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        scroll_widget = QWidget()
        layout = QVBoxLayout(scroll_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Header
        header = QLabel("📝 Research Note Details")
        header.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        layout.addWidget(header)

        # === BASIC INFO ===
        form_layout = QFormLayout()
        form_layout.setSpacing(10)

        # Title
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Enter research note title...")
        form_layout.addRow("Title *:", self.title_input)

        # Category
        category_layout = QHBoxLayout()
        category_layout.setSpacing(5)

        self.category_combo = QComboBox()
        self.category_combo.setEditable(True)
        self.category_combo.setPlaceholderText("Select or enter category...")
        category_layout.addWidget(self.category_combo)

        self.new_category_btn = QPushButton("+ New")
        self.new_category_btn.setMaximumWidth(60)
        self.new_category_btn.clicked.connect(self._add_new_category)
        category_layout.addWidget(self.new_category_btn)

        form_layout.addRow("Category:", category_layout)

        layout.addLayout(form_layout)

        # Content
        content_label = QLabel("Content:")
        content_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        layout.addWidget(content_label)

        self.content_input = QTextEdit()
        self.content_input.setPlaceholderText("Write your research notes here...")
        self.content_input.setMinimumHeight(200)
        layout.addWidget(self.content_input)

        # === SOURCES SECTION ===
        sources_label = QLabel("Sources:")
        sources_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        layout.addWidget(sources_label)

        self.sources_list = QListWidget()
        self.sources_list.setMaximumHeight(120)
        self.sources_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #ccc;
                border-radius: 5px;
                background-color: #f9f9f9;
            }
            QListWidget::item {
                color: #333;
                padding: 5px;
            }
        """)
        layout.addWidget(self.sources_list)

        sources_btn_layout = QHBoxLayout()
        sources_btn_layout.setSpacing(10)

        self.add_source_btn = QPushButton("Add Source")
        self.add_source_btn.clicked.connect(self._add_source)
        sources_btn_layout.addWidget(self.add_source_btn)

        self.remove_source_btn = QPushButton("Remove Selected")
        self.remove_source_btn.clicked.connect(self._remove_source)
        sources_btn_layout.addWidget(self.remove_source_btn)

        sources_btn_layout.addStretch()
        layout.addLayout(sources_btn_layout)

        # === TAGS SECTION ===
        tags_label = QLabel("Tags:")
        tags_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        layout.addWidget(tags_label)

        self.tags_input = QLineEdit()
        self.tags_input.setPlaceholderText("Enter tags separated by commas (e.g., medieval, weapons, history)")
        layout.addWidget(self.tags_input)

        tags_hint = QLabel("💡 Tip: Use tags to organize and find related research notes quickly")
        tags_hint.setStyleSheet("color: #666; font-style: italic; font-size: 11px;")
        layout.addWidget(tags_hint)

        # Add stretch
        layout.addStretch()

        scroll.setWidget(scroll_widget)
        main_layout.addWidget(scroll)

        # === BUTTONS ===
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(20, 10, 20, 20)
        button_layout.setSpacing(10)

        button_layout.addStretch()

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setMinimumWidth(100)
        self.cancel_btn.clicked.connect(self.cancel_requested.emit)
        button_layout.addWidget(self.cancel_btn)

        self.save_btn = QPushButton("Save Research Note")
        self.save_btn.setMinimumWidth(120)
        self.save_btn.setStyleSheet("""
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
        self.save_btn.clicked.connect(self._on_save_clicked)
        button_layout.addWidget(self.save_btn)

        main_layout.addLayout(button_layout)

    def load_categories(self, categories: List[str]):
        """
        Load available categories

        Args:
            categories: List of existing categories
        """
        self._all_categories = categories

        current_text = self.category_combo.currentText()
        self.category_combo.clear()
        self.category_combo.addItem("")  # Empty option

        for category in sorted(categories):
            self.category_combo.addItem(category)

        # Restore previous selection
        if current_text:
            index = self.category_combo.findText(current_text)
            if index >= 0:
                self.category_combo.setCurrentIndex(index)

    def load_research_note(self, note: ResearchNote):
        """
        Load a research note for editing

        Args:
            note: ResearchNote to edit
        """
        self._current_note = note

        # Load basic info
        self.title_input.setText(note.title)
        self.content_input.setPlainText(note.content)

        # Load category
        if note.category:
            index = self.category_combo.findText(note.category)
            if index >= 0:
                self.category_combo.setCurrentIndex(index)
            else:
                # Category doesn't exist in list, add it
                self.category_combo.addItem(note.category)
                self.category_combo.setCurrentText(note.category)

        # Load sources
        self.sources_list.clear()
        for source in note.sources:
            item = QListWidgetItem(f"🔗 {source}")
            self.sources_list.addItem(item)

        # Load tags
        self.tags_input.setText(", ".join(note.tags))

    def clear_form(self):
        """Clear the form for new research note"""
        self._current_note = None

        self.title_input.clear()
        self.content_input.clear()
        self.category_combo.setCurrentIndex(0)
        self.sources_list.clear()
        self.tags_input.clear()

    def _add_new_category(self):
        """Add a new category"""
        category, ok = QInputDialog.getText(
            self,
            "New Category",
            "Enter category name:"
        )

        if ok and category.strip():
            category = category.strip()
            if category not in self._all_categories:
                self._all_categories.append(category)
                self.category_combo.addItem(category)

            self.category_combo.setCurrentText(category)

    def _add_source(self):
        """Add a source URL/reference"""
        source, ok = QInputDialog.getText(
            self,
            "Add Source",
            "Enter source URL or reference:"
        )

        if ok and source.strip():
            item = QListWidgetItem(f"🔗 {source.strip()}")
            self.sources_list.addItem(item)

    def _remove_source(self):
        """Remove selected source"""
        current_item = self.sources_list.currentItem()
        if current_item:
            row = self.sources_list.row(current_item)
            self.sources_list.takeItem(row)

    def _on_save_clicked(self):
        """Validate and save research note"""
        # Validate title
        title = self.title_input.text().strip()
        if not title:
            QMessageBox.warning(
                self,
                "Invalid Title",
                "Please enter a research note title."
            )
            self.title_input.setFocus()
            return

        # Get category
        category = self.category_combo.currentText().strip()

        # Get sources
        sources = []
        for i in range(self.sources_list.count()):
            item = self.sources_list.item(i)
            source_text = item.text().replace("🔗 ", "").strip()
            sources.append(source_text)

        # Get tags
        tags_text = self.tags_input.text().strip()
        tags = [tag.strip() for tag in tags_text.split(",") if tag.strip()]

        # Create/update research note
        if self._current_note:
            # Update existing
            note = self._current_note
            note.title = title
            note.content = self.content_input.toPlainText()
            note.category = category
            note.sources = sources
            note.tags = tags
        else:
            # Create new
            note = ResearchNote(
                title=title,
                content=self.content_input.toPlainText(),
                category=category,
                sources=sources,
                tags=tags
            )

        # Emit save signal
        self.save_requested.emit(note)
