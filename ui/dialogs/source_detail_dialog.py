"""
Source Detail Dialog - Edit/create source citations
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel,
    QLineEdit, QTextEdit, QComboBox, QPushButton, QMessageBox,
    QScrollArea, QFrame, QGroupBox
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QFont
from typing import Optional
from models.source import Source


class SourceDetailDialog(QDialog):
    """
    Dialog for creating/editing source citations
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Source Details")
        self.setMinimumWidth(600)
        self.setMinimumHeight(700)

        self._current_source: Optional[Source] = None
        self._setup_ui()

    def _setup_ui(self):
        """Setup the UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(15)

        # Header
        header = QLabel("🔗 Source Citation Details")
        header.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        scroll_layout.addWidget(header)

        # === BASIC INFO ===
        basic_group = QGroupBox("Basic Information")
        basic_layout = QFormLayout()
        basic_layout.setSpacing(10)

        # Title
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Enter source title...")
        basic_layout.addRow("Title *:", self.title_input)

        # Author
        self.author_input = QLineEdit()
        self.author_input.setPlaceholderText("e.g., Smith, John")
        basic_layout.addRow("Author:", self.author_input)

        # Type
        self.type_combo = QComboBox()
        self.type_combo.addItem("📚 Book", "book")
        self.type_combo.addItem("🌐 Website", "web")
        self.type_combo.addItem("📰 Article", "article")
        self.type_combo.addItem("📑 Journal", "journal")
        self.type_combo.addItem("🎥 Other", "other")
        basic_layout.addRow("Type *:", self.type_combo)

        # Year
        self.year_input = QLineEdit()
        self.year_input.setPlaceholderText("e.g., 2024")
        self.year_input.setMaximumWidth(150)
        basic_layout.addRow("Year:", self.year_input)

        basic_group.setLayout(basic_layout)
        scroll_layout.addWidget(basic_group)

        # === PUBLICATION INFO ===
        pub_group = QGroupBox("Publication Information")
        pub_layout = QFormLayout()
        pub_layout.setSpacing(10)

        # Publisher
        self.publisher_input = QLineEdit()
        self.publisher_input.setPlaceholderText("e.g., Oxford University Press")
        pub_layout.addRow("Publisher:", self.publisher_input)

        # URL
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://...")
        pub_layout.addRow("URL:", self.url_input)

        # DOI
        self.doi_input = QLineEdit()
        self.doi_input.setPlaceholderText("e.g., 10.1000/xyz123")
        pub_layout.addRow("DOI:", self.doi_input)

        # Accessed Date
        self.accessed_date_input = QLineEdit()
        self.accessed_date_input.setPlaceholderText("e.g., January 15, 2024")
        pub_layout.addRow("Accessed Date:", self.accessed_date_input)

        pub_group.setLayout(pub_layout)
        scroll_layout.addWidget(pub_group)

        # === NOTES ===
        notes_label = QLabel("Notes:")
        notes_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        scroll_layout.addWidget(notes_label)

        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText("Additional notes about this source...")
        self.notes_input.setMaximumHeight(100)
        scroll_layout.addWidget(self.notes_input)

        # === CITATION PREVIEW ===
        preview_label = QLabel("Citation Preview:")
        preview_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        scroll_layout.addWidget(preview_label)

        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setMaximumHeight(120)
        self.preview_text.setStyleSheet("""
            QTextEdit {
                background-color: #f5f5f5;
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        scroll_layout.addWidget(self.preview_text)

        # Update preview button
        update_preview_btn = QPushButton("🔄 Update Preview")
        update_preview_btn.clicked.connect(self._update_preview)
        scroll_layout.addWidget(update_preview_btn)

        scroll_layout.addStretch()

        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)

        # === BUTTONS ===
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        button_layout.addStretch()

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setMinimumWidth(100)
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)

        self.save_btn = QPushButton("Save Source")
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

        layout.addLayout(button_layout)

    def load_source(self, source: Source):
        """
        Load a source for editing

        Args:
            source: Source to edit
        """
        self._current_source = source

        # Load basic info
        self.title_input.setText(source.title)
        self.author_input.setText(source.author)
        self.year_input.setText(source.year)

        # Set type
        index = self.type_combo.findData(source.source_type)
        if index >= 0:
            self.type_combo.setCurrentIndex(index)

        # Load publication info
        self.publisher_input.setText(source.publisher)
        self.url_input.setText(source.url)
        self.doi_input.setText(source.doi)
        self.accessed_date_input.setText(source.accessed_date)

        # Load notes
        self.notes_input.setPlainText(source.notes)

        # Update preview
        self._update_preview()

    def clear_form(self):
        """Clear the form for new source"""
        self._current_source = None

        self.title_input.clear()
        self.author_input.clear()
        self.year_input.clear()
        self.type_combo.setCurrentIndex(0)
        self.publisher_input.clear()
        self.url_input.clear()
        self.doi_input.clear()
        self.accessed_date_input.clear()
        self.notes_input.clear()
        self.preview_text.clear()

    def _update_preview(self):
        """Update citation preview"""
        # Create temporary source with current values
        temp_source = Source(
            title=self.title_input.text().strip() or "Untitled",
            author=self.author_input.text().strip(),
            source_type=self.type_combo.currentData(),
            year=self.year_input.text().strip(),
            publisher=self.publisher_input.text().strip(),
            url=self.url_input.text().strip(),
            doi=self.doi_input.text().strip(),
            accessed_date=self.accessed_date_input.text().strip()
        )

        # Generate citations
        apa = temp_source.generate_apa_citation()
        mla = temp_source.generate_mla_citation()

        preview = f"APA Format:\n{apa}\n\nMLA Format:\n{mla}"
        self.preview_text.setPlainText(preview)

    def _on_save_clicked(self):
        """Validate and save source"""
        # Validate title
        title = self.title_input.text().strip()
        if not title:
            QMessageBox.warning(
                self,
                "Invalid Title",
                "Please enter a source title."
            )
            self.title_input.setFocus()
            return

        # Create/update source
        if self._current_source:
            # Update existing
            self._current_source.title = title
            self._current_source.author = self.author_input.text().strip()
            self._current_source.source_type = self.type_combo.currentData()
            self._current_source.year = self.year_input.text().strip()
            self._current_source.publisher = self.publisher_input.text().strip()
            self._current_source.url = self.url_input.text().strip()
            self._current_source.doi = self.doi_input.text().strip()
            self._current_source.accessed_date = self.accessed_date_input.text().strip()
            self._current_source.notes = self.notes_input.toPlainText()
        else:
            # Create new
            self._current_source = Source(
                title=title,
                author=self.author_input.text().strip(),
                source_type=self.type_combo.currentData(),
                year=self.year_input.text().strip(),
                publisher=self.publisher_input.text().strip(),
                url=self.url_input.text().strip(),
                doi=self.doi_input.text().strip(),
                accessed_date=self.accessed_date_input.text().strip(),
                notes=self.notes_input.toPlainText()
            )

        # Accept dialog
        self.accept()

    def get_source(self) -> Source:
        """
        Get the created/edited source

        Returns:
            Source object
        """
        return self._current_source
