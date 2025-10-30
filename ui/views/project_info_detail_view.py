"""
Project Info Detail View - Edit project information
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel,
    QLineEdit, QComboBox, QPushButton, QScrollArea,
    QFrame, QMessageBox
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QFont
from typing import Optional
from models.project import Project
from models.project_type import ProjectType
from datetime import datetime


class ProjectInfoDetailView(QWidget):
    """
    Detail view for editing project information
    """

    # Signals
    save_requested = Signal(Project)  # Updated project
    cancel_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_project: Optional[Project] = None
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
        header = QLabel("📋 Project Information")
        header.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        layout.addWidget(header)

        # === BASIC INFO ===
        form_layout = QFormLayout()
        form_layout.setSpacing(10)

        # Title
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Enter project title...")
        self.title_input.setMinimumWidth(500)
        form_layout.addRow("Title *:", self.title_input)

        # Author
        self.author_input = QLineEdit()
        self.author_input.setPlaceholderText("Enter author name...")
        form_layout.addRow("Author *:", self.author_input)

        # Language
        self.language_combo = QComboBox()
        self.language_combo.addItem("🇮🇹 Italiano", "it")
        self.language_combo.addItem("🇬🇧 English", "en")
        self.language_combo.addItem("🇪🇸 Español", "es")
        self.language_combo.addItem("🇫🇷 Français", "fr")
        self.language_combo.addItem("🇩🇪 Deutsch", "de")
        form_layout.addRow("Language *:", self.language_combo)

        # Genre
        self.genre_input = QLineEdit()
        self.genre_input.setPlaceholderText("e.g., Fantasy, Thriller, Romance...")
        form_layout.addRow("Genre:", self.genre_input)

        layout.addLayout(form_layout)

        # === PROJECT TYPE ===
        project_type_label = QLabel("Project Type *:")
        project_type_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        layout.addWidget(project_type_label)

        self.project_type_combo = QComboBox()
        # Populate with all project types
        for pt in ProjectType:
            icon = pt.get_icon()
            name = pt.get_display_name('it')  # Default to Italian, will update on load
            self.project_type_combo.addItem(f"{icon} {name}", pt.value)

        self.project_type_combo.currentIndexChanged.connect(self._update_project_type_description)
        layout.addWidget(self.project_type_combo)

        # Project type description (dynamic)
        self.project_type_desc = QLabel()
        self.project_type_desc.setWordWrap(True)
        self.project_type_desc.setStyleSheet("""
            QLabel {
                color: #666;
                font-style: italic;
                font-size: 11px;
                padding: 5px;
                background-color: #f9f9f9;
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.project_type_desc)

        # === TAGS ===
        tags_label = QLabel("Tags:")
        tags_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        layout.addWidget(tags_label)

        self.tags_input = QLineEdit()
        self.tags_input.setPlaceholderText("Enter tags separated by commas (e.g., fantasy, adventure, magic)")
        layout.addWidget(self.tags_input)

        tags_hint = QLabel("💡 Tip: Use tags to organize and categorize your projects")
        tags_hint.setStyleSheet("color: #666; font-style: italic; font-size: 11px;")
        layout.addWidget(tags_hint)

        # === PROJECT DATES (Read-Only) ===
        layout.addSpacing(10)
        dates_separator = QFrame()
        dates_separator.setFrameShape(QFrame.Shape.HLine)
        dates_separator.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(dates_separator)

        dates_label = QLabel("Project Dates")
        dates_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(dates_label)

        dates_form = QFormLayout()
        dates_form.setSpacing(5)

        self.created_label = QLabel()
        self.created_label.setStyleSheet("color: #666;")
        dates_form.addRow("Created:", self.created_label)

        self.modified_label = QLabel()
        self.modified_label.setStyleSheet("color: #666;")
        dates_form.addRow("Last Modified:", self.modified_label)

        layout.addLayout(dates_form)

        # Spacer
        layout.addStretch()

        # === ACTION BUTTONS ===
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)

        self.save_btn = QPushButton("💾 Save")
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px 24px;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        self.save_btn.clicked.connect(self._on_save)
        buttons_layout.addWidget(self.save_btn)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                padding: 10px 24px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
            QPushButton:pressed {
                background-color: #c41105;
            }
        """)
        self.cancel_btn.clicked.connect(self._on_cancel)
        buttons_layout.addWidget(self.cancel_btn)

        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)

        # Set scroll widget
        scroll.setWidget(scroll_widget)
        main_layout.addWidget(scroll)

    def load_project(self, project: Project):
        """
        Load project data into the form

        Args:
            project: Project to load
        """
        self._current_project = project

        # Basic info
        self.title_input.setText(project.title)
        self.author_input.setText(project.author)
        self.genre_input.setText(project.genre)

        # Language
        language_index = self.language_combo.findData(project.language)
        if language_index >= 0:
            self.language_combo.setCurrentIndex(language_index)

        # Project type
        project_type_index = self.project_type_combo.findData(project.project_type.value)
        if project_type_index >= 0:
            self.project_type_combo.setCurrentIndex(project_type_index)

        # Update project type labels based on current language
        self._update_project_type_combo_labels(project.language)

        # Tags
        tags_str = ", ".join(project.tags) if project.tags else ""
        self.tags_input.setText(tags_str)

        # Dates (read-only)
        self.created_label.setText(self._format_date(project.created_date))
        self.modified_label.setText(self._format_date(project.modified_date))

        # Update description
        self._update_project_type_description()

    def _update_project_type_combo_labels(self, language: str):
        """
        Update project type combo box labels based on language

        Args:
            language: Language code
        """
        current_value = self.project_type_combo.currentData()

        self.project_type_combo.clear()
        for pt in ProjectType:
            icon = pt.get_icon()
            name = pt.get_display_name(language)
            self.project_type_combo.addItem(f"{icon} {name}", pt.value)

        # Restore selection
        index = self.project_type_combo.findData(current_value)
        if index >= 0:
            self.project_type_combo.setCurrentIndex(index)

    def _update_project_type_description(self):
        """Update the project type description label"""
        current_type_value = self.project_type_combo.currentData()
        if current_type_value:
            try:
                project_type = ProjectType(current_type_value)
                language = self.language_combo.currentData() or 'it'
                description = project_type.get_description(language)
                self.project_type_desc.setText(f"📖 {description}")
            except ValueError:
                self.project_type_desc.setText("")

    def _format_date(self, date_str: str) -> str:
        """
        Format ISO date string to readable format

        Args:
            date_str: ISO format date string

        Returns:
            str: Formatted date string
        """
        if not date_str:
            return "N/A"

        try:
            dt = datetime.fromisoformat(date_str)
            return dt.strftime("%d/%m/%Y %H:%M")
        except:
            return date_str

    def get_updated_project(self) -> Project:
        """
        Get updated project from form data

        Returns:
            Project: Updated project instance
        """
        # Parse tags
        tags_str = self.tags_input.text().strip()
        tags = [tag.strip() for tag in tags_str.split(',') if tag.strip()] if tags_str else []

        # Get project type
        project_type_value = self.project_type_combo.currentData()
        project_type = ProjectType(project_type_value)

        # Create updated project
        updated_project = Project(
            title=self.title_input.text().strip(),
            author=self.author_input.text().strip(),
            language=self.language_combo.currentData(),
            project_type=project_type,
            created_date=self._current_project.created_date,
            modified_date=self._current_project.modified_date,
            manuscript_text=self._current_project.manuscript_text,
            genre=self.genre_input.text().strip(),
            target_word_count=self._current_project.target_word_count,  # Keep existing value
            tags=tags
        )

        return updated_project

    def _validate_inputs(self) -> bool:
        """
        Validate form inputs

        Returns:
            bool: True if valid, False otherwise
        """
        # Validate title
        title = self.title_input.text().strip()
        if not title:
            QMessageBox.warning(self, "Validation Error", "Title is required.")
            self.title_input.setFocus()
            return False

        if len(title) > 200:
            QMessageBox.warning(self, "Validation Error", "Title is too long (max 200 characters).")
            self.title_input.setFocus()
            return False

        # Validate author
        author = self.author_input.text().strip()
        if not author:
            QMessageBox.warning(self, "Validation Error", "Author is required.")
            self.author_input.setFocus()
            return False

        if len(author) > 100:
            QMessageBox.warning(self, "Validation Error", "Author name is too long (max 100 characters).")
            self.author_input.setFocus()
            return False

        # Validate genre length
        genre = self.genre_input.text().strip()
        if len(genre) > 50:
            QMessageBox.warning(self, "Validation Error", "Genre is too long (max 50 characters).")
            self.genre_input.setFocus()
            return False

        return True

    def _on_save(self):
        """Handle save button click"""
        # Validate inputs
        if not self._validate_inputs():
            return

        # Get updated project
        updated_project = self.get_updated_project()

        # Emit signal
        self.save_requested.emit(updated_project)

    def _on_cancel(self):
        """Handle cancel button click"""
        self.cancel_requested.emit()
