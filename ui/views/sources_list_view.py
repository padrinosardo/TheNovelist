"""
Sources List View - Shows all sources/citations in a project
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget,
    QListWidgetItem, QLabel, QLineEdit, QComboBox, QMessageBox, QTextEdit
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QFont
from typing import List
from models.source import Source


class SourcesListView(QWidget):
    """
    List view for sources with search, filter, and bibliography generation
    """

    # Signals
    source_selected = Signal(str)  # source_id
    add_source_requested = Signal()
    edit_source_requested = Signal(str)  # source_id
    delete_source_requested = Signal(str)  # source_id

    def __init__(self, parent=None):
        super().__init__(parent)
        self._sources: List[Source] = []
        self._filtered_sources: List[Source] = []
        self._setup_ui()

    def _setup_ui(self):
        """Setup the UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Header
        header = QLabel("🔗 Sources & Citations")
        header.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        layout.addWidget(header)

        # Search and filter bar
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(10)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search sources...")
        self.search_input.textChanged.connect(self._on_filter_changed)
        filter_layout.addWidget(self.search_input, stretch=2)

        self.type_filter = QComboBox()
        self.type_filter.addItem("All Types", "")
        self.type_filter.addItem("📚 Book", "book")
        self.type_filter.addItem("🌐 Website", "web")
        self.type_filter.addItem("📰 Article", "article")
        self.type_filter.addItem("📑 Journal", "journal")
        self.type_filter.addItem("🎥 Other", "other")
        self.type_filter.currentIndexChanged.connect(self._on_filter_changed)
        filter_layout.addWidget(self.type_filter, stretch=1)

        self.clear_filter_btn = QPushButton("Clear")
        self.clear_filter_btn.setMaximumWidth(80)
        self.clear_filter_btn.clicked.connect(self._clear_filters)
        filter_layout.addWidget(self.clear_filter_btn)

        layout.addLayout(filter_layout)

        # Sources list
        self.sources_list = QListWidget()
        self.sources_list.setAlternatingRowColors(True)
        self.sources_list.itemClicked.connect(self._on_source_clicked)
        self.sources_list.itemDoubleClicked.connect(self._on_source_double_clicked)
        self.sources_list.setStyleSheet("""
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
        layout.addWidget(self.sources_list)

        # Stats
        self.stats_label = QLabel("0 sources")
        self.stats_label.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(self.stats_label)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        self.add_btn = QPushButton("➕ Add Source")
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
        self.add_btn.clicked.connect(self.add_source_requested.emit)
        button_layout.addWidget(self.add_btn)

        self.edit_btn = QPushButton("✏️ Edit")
        self.edit_btn.setEnabled(False)
        self.edit_btn.clicked.connect(self._on_edit_clicked)
        button_layout.addWidget(self.edit_btn)

        self.generate_bib_btn = QPushButton("📋 Generate Bibliography")
        self.generate_bib_btn.clicked.connect(self._generate_bibliography)
        button_layout.addWidget(self.generate_bib_btn)

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

    def load_sources(self, sources: List[Source]):
        """
        Load sources into the list

        Args:
            sources: List of Source objects
        """
        self._sources = sources
        self._filtered_sources = sources.copy()
        self._refresh_list()

    def _refresh_list(self):
        """Refresh the sources list widget"""
        self.sources_list.clear()

        for source in self._filtered_sources:
            item = QListWidgetItem()

            # Get type icon
            type_icons = {
                "book": "📚",
                "web": "🌐",
                "article": "📰",
                "journal": "📑",
                "other": "🎥"
            }
            icon = type_icons.get(source.source_type, "📄")

            # Display format: icon + title + author
            display_text = f"{icon} {source.title}"

            if source.author:
                display_text += f"\n   by {source.author}"

            if source.year:
                display_text += f" ({source.year})"

            if source.url:
                display_text += f"\n   🔗 {source.url[:50]}{'...' if len(source.url) > 50 else ''}"

            item.setText(display_text)
            item.setData(Qt.ItemDataRole.UserRole, source.id)

            self.sources_list.addItem(item)

        # Update stats
        total = len(self._sources)
        filtered = len(self._filtered_sources)
        if filtered == total:
            self.stats_label.setText(f"{total} source{'s' if total != 1 else ''}")
        else:
            self.stats_label.setText(f"{filtered} of {total} sources")

    def _on_filter_changed(self):
        """Apply search and type filters"""
        search_text = self.search_input.text().lower().strip()
        type_filter = self.type_filter.currentData()

        self._filtered_sources = []

        for source in self._sources:
            # Type filter
            if type_filter and source.source_type != type_filter:
                continue

            # Search filter
            if search_text:
                matches = (
                    search_text in source.title.lower() or
                    (source.author and search_text in source.author.lower()) or
                    (source.url and search_text in source.url.lower())
                )
                if not matches:
                    continue

            self._filtered_sources.append(source)

        self._refresh_list()

    def _clear_filters(self):
        """Clear all filters"""
        self.search_input.clear()
        self.type_filter.setCurrentIndex(0)

    def _on_source_clicked(self, item: QListWidgetItem):
        """Handle source click"""
        source_id = item.data(Qt.ItemDataRole.UserRole)
        self.edit_btn.setEnabled(True)
        self.delete_btn.setEnabled(True)
        self.source_selected.emit(source_id)

    def _on_source_double_clicked(self, item: QListWidgetItem):
        """Handle source double-click (edit)"""
        source_id = item.data(Qt.ItemDataRole.UserRole)
        self.edit_source_requested.emit(source_id)

    def _on_edit_clicked(self):
        """Handle edit button click"""
        current_item = self.sources_list.currentItem()
        if current_item:
            source_id = current_item.data(Qt.ItemDataRole.UserRole)
            self.edit_source_requested.emit(source_id)

    def _on_delete_clicked(self):
        """Handle delete button click"""
        current_item = self.sources_list.currentItem()
        if not current_item:
            return

        source_id = current_item.data(Qt.ItemDataRole.UserRole)

        # Find source for confirmation
        source = None
        for s in self._sources:
            if s.id == source_id:
                source = s
                break

        if not source:
            return

        # Confirm deletion
        reply = QMessageBox.question(
            self,
            "Delete Source",
            f"Are you sure you want to delete '{source.title}'?\n\nThis action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.delete_source_requested.emit(source_id)

    def _generate_bibliography(self):
        """Generate bibliography from all sources"""
        if not self._sources:
            QMessageBox.information(
                self,
                "No Sources",
                "No sources available to generate bibliography."
            )
            return

        # Create dialog with bibliography
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QTabWidget, QTextEdit, QPushButton

        dialog = QDialog(self)
        dialog.setWindowTitle("Bibliography")
        dialog.setMinimumWidth(700)
        dialog.setMinimumHeight(500)

        layout = QVBoxLayout(dialog)

        tabs = QTabWidget()

        # APA Format
        apa_text = QTextEdit()
        apa_text.setReadOnly(True)
        apa_bibliography = "\n\n".join([source.generate_apa_citation() for source in sorted(self._sources, key=lambda s: s.author or s.title)])
        apa_text.setPlainText(apa_bibliography)
        tabs.addTab(apa_text, "APA Format")

        # MLA Format
        mla_text = QTextEdit()
        mla_text.setReadOnly(True)
        mla_bibliography = "\n\n".join([source.generate_mla_citation() for source in sorted(self._sources, key=lambda s: s.author or s.title)])
        mla_text.setPlainText(mla_bibliography)
        tabs.addTab(mla_text, "MLA Format")

        # BibTeX Format
        bibtex_text = QTextEdit()
        bibtex_text.setReadOnly(True)
        bibtex_bibliography = "\n\n".join([source.generate_bibtex_citation() for source in self._sources])
        bibtex_text.setPlainText(bibtex_bibliography)
        tabs.addTab(bibtex_text, "BibTeX Format")

        layout.addWidget(tabs)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)

        dialog.exec()

    def select_source(self, source_id: str):
        """
        Programmatically select a source

        Args:
            source_id: Source ID to select
        """
        for i in range(self.sources_list.count()):
            item = self.sources_list.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == source_id:
                self.sources_list.setCurrentItem(item)
                self.edit_btn.setEnabled(True)
                self.delete_btn.setEnabled(True)
                break

    def clear_selection(self):
        """Clear current selection"""
        self.sources_list.clearSelection()
        self.edit_btn.setEnabled(False)
        self.delete_btn.setEnabled(False)
