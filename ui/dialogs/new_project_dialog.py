"""
New Project Dialog - Advanced project creation with project types and metadata
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox,
    QLineEdit, QComboBox, QSpinBox, QPushButton, QLabel,
    QTextEdit, QWidget, QScrollArea, QFrame, QCheckBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from typing import Optional, Tuple, List
from models.project_type import ProjectType
from models.container_type import ContainerType
from utils.validators import Validators
from ui.components.ai_config_widget import AIConfigWidget
from managers.ai import AIManager


class NewProjectDialog(QDialog):
    """
    Advanced dialog for creating new projects with full metadata and project type selection.

    Features:
    - Basic project info (title, author, language)
    - Project type selection with description
    - Optional metadata (genre, target word count, tags)
    - Preview of available containers based on project type
    - Validation and helpful tooltips
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create New Project")
        self.setMinimumWidth(600)
        self.setMinimumHeight(700)

        # Store values
        self._title = ""
        self._author = ""
        self._language = "it"
        self._project_type = ProjectType.NOVEL
        self._genre = ""
        self._target_word_count = 0
        self._tags = []
        self._use_template = True  # Default: use template

        self._setup_ui()
        self._connect_signals()
        self._update_containers_preview()

    def _setup_ui(self):
        """Setup the dialog UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Main scroll area for long content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(15)

        # === BASIC INFORMATION GROUP ===
        basic_group = QGroupBox("Basic Information")
        basic_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #2196F3;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        basic_layout = QFormLayout()
        basic_layout.setSpacing(10)

        # Title
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Enter your project title...")
        self.title_input.setToolTip("The title of your writing project")
        basic_layout.addRow("Title *:", self.title_input)

        # Author
        self.author_input = QLineEdit()
        self.author_input.setPlaceholderText("Your name")
        self.author_input.setToolTip("The author of this project")
        basic_layout.addRow("Author *:", self.author_input)

        # Language
        self.language_combo = QComboBox()
        self.language_combo.addItems([
            "🇮🇹 Italiano (it)",
            "🇬🇧 English (en)",
            "🇪🇸 Español (es)",
            "🇫🇷 Français (fr)",
            "🇩🇪 Deutsch (de)"
        ])
        self.language_combo.setToolTip("Language for grammar and style analysis")
        basic_layout.addRow("Language *:", self.language_combo)

        # Project Type
        self.project_type_combo = QComboBox()
        for pt in ProjectType:
            icon = pt.get_icon()
            name = pt.get_display_name('it')
            self.project_type_combo.addItem(f"{icon} {name}", pt)
        self.project_type_combo.setToolTip("Type of writing project")
        basic_layout.addRow("Project Type *:", self.project_type_combo)

        # Project type description
        self.type_description = QLabel()
        self.type_description.setWordWrap(True)
        self.type_description.setStyleSheet("""
            QLabel {
                color: #666;
                font-style: italic;
                padding: 5px;
                background-color: #f5f5f5;
                border-radius: 3px;
            }
        """)
        basic_layout.addRow("", self.type_description)

        basic_group.setLayout(basic_layout)
        scroll_layout.addWidget(basic_group)

        # === TEMPLATE OPTION ===
        template_group = QGroupBox("Initial Content")
        template_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #9C27B0;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        template_layout = QVBoxLayout()

        self.use_template_checkbox = QCheckBox("Use base template for this project type")
        self.use_template_checkbox.setChecked(True)
        self.use_template_checkbox.setToolTip(
            "Start with a pre-configured template including sample chapters, "
            "scenes, and characters appropriate for this project type"
        )
        template_layout.addWidget(self.use_template_checkbox)

        template_info = QLabel(
            "📋 Templates provide a helpful starting structure with sample chapters, "
            "scenes, and characters. You can modify or delete them after creation."
        )
        template_info.setWordWrap(True)
        template_info.setStyleSheet("color: #666; font-style: italic; padding: 5px;")
        template_layout.addWidget(template_info)

        template_group.setLayout(template_layout)
        scroll_layout.addWidget(template_group)

        # === OPTIONAL METADATA GROUP ===
        metadata_group = QGroupBox("Optional Metadata")
        metadata_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #4CAF50;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        metadata_layout = QFormLayout()
        metadata_layout.setSpacing(10)

        # Genre
        self.genre_input = QLineEdit()
        self.genre_input.setPlaceholderText("e.g., Fantasy, Sci-Fi, Mystery...")
        self.genre_input.setToolTip("Genre or category (optional)")
        metadata_layout.addRow("Genre:", self.genre_input)

        # Target Word Count
        word_count_widget = QWidget()
        word_count_layout = QHBoxLayout(word_count_widget)
        word_count_layout.setContentsMargins(0, 0, 0, 0)

        self.word_count_spin = QSpinBox()
        self.word_count_spin.setRange(0, 1000000)
        self.word_count_spin.setValue(0)
        self.word_count_spin.setSingleStep(1000)
        self.word_count_spin.setSuffix(" words")
        self.word_count_spin.setSpecialValueText("Not set")
        self.word_count_spin.setToolTip("Target word count for this project (0 = not set)")
        word_count_layout.addWidget(self.word_count_spin)

        self.suggest_word_count_btn = QPushButton("Suggest")
        self.suggest_word_count_btn.setToolTip("Suggest typical word count for this project type")
        self.suggest_word_count_btn.setMaximumWidth(80)
        word_count_layout.addWidget(self.suggest_word_count_btn)

        metadata_layout.addRow("Target Word Count:", word_count_widget)

        # Tags
        self.tags_input = QLineEdit()
        self.tags_input.setPlaceholderText("Enter tags separated by commas: epic, magic, adventure")
        self.tags_input.setToolTip("Tags for organizing projects (comma-separated)")
        metadata_layout.addRow("Tags:", self.tags_input)

        metadata_group.setLayout(metadata_layout)
        scroll_layout.addWidget(metadata_group)

        # === AI CONFIGURATION GROUP ===
        ai_group = QGroupBox("AI Provider Configuration")
        ai_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #E91E63;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        ai_layout = QVBoxLayout()

        ai_info = QLabel("🤖 Configure which AI assistant to use for character development in this project")
        ai_info.setWordWrap(True)
        ai_info.setStyleSheet("color: #666; font-style: italic;")
        ai_layout.addWidget(ai_info)

        # Initialize AI manager and widget
        self.ai_manager = AIManager()
        self.ai_config_widget = AIConfigWidget(self.ai_manager)
        ai_layout.addWidget(self.ai_config_widget)

        ai_group.setLayout(ai_layout)
        scroll_layout.addWidget(ai_group)

        # === CONTAINERS PREVIEW GROUP ===
        containers_group = QGroupBox("Available Containers for this Project Type")
        containers_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #FF9800;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        containers_layout = QVBoxLayout()

        containers_info = QLabel("These content containers will be available in your project:")
        containers_info.setStyleSheet("color: #666; font-style: italic;")
        containers_layout.addWidget(containers_info)

        self.containers_preview = QLabel()
        self.containers_preview.setWordWrap(True)
        self.containers_preview.setStyleSheet("""
            QLabel {
                padding: 10px;
                background-color: #fff3e0;
                border-radius: 5px;
                font-size: 13px;
            }
        """)
        containers_layout.addWidget(self.containers_preview)

        containers_group.setLayout(containers_layout)
        scroll_layout.addWidget(containers_group)

        # Add stretch to push everything to the top
        scroll_layout.addStretch()

        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)

        # === BUTTONS ===
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setMinimumWidth(100)
        button_layout.addWidget(self.cancel_btn)

        self.create_btn = QPushButton("Create Project")
        self.create_btn.setMinimumWidth(120)
        self.create_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                font-weight: bold;
                padding: 8px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
        """)
        button_layout.addWidget(self.create_btn)

        layout.addLayout(button_layout)

        # Update initial description
        self._update_type_description()

    def _connect_signals(self):
        """Connect UI signals"""
        self.project_type_combo.currentIndexChanged.connect(self._on_project_type_changed)
        self.suggest_word_count_btn.clicked.connect(self._suggest_word_count)
        self.cancel_btn.clicked.connect(self.reject)
        self.create_btn.clicked.connect(self._on_create_clicked)

    def _on_project_type_changed(self, index):
        """Handle project type change"""
        self._update_type_description()
        self._update_containers_preview()
        self._update_suggested_word_count_hint()

    def _update_type_description(self):
        """Update the project type description label"""
        project_type = self.project_type_combo.currentData()
        if project_type:
            description = project_type.get_description('it')
            self.type_description.setText(f"ℹ️ {description}")

    def _update_containers_preview(self):
        """Update the containers preview based on selected project type"""
        project_type = self.project_type_combo.currentData()
        if not project_type:
            return

        available_containers = ContainerType.get_available_for_project_type(project_type)

        # Build preview text with icons
        container_items = []
        for container_type in available_containers:
            if container_type in [ContainerType.MANUSCRIPT, ContainerType.CHARACTERS]:
                continue  # Don't show these as they're always present

            icon, name = ContainerType.get_display_info(container_type, 'it')
            container_items.append(f"{icon} <b>{name}</b>")

        if container_items:
            preview_text = " • ".join(container_items)
            self.containers_preview.setText(preview_text)
        else:
            self.containers_preview.setText("Manuscript and Characters (default containers)")

    def _update_suggested_word_count_hint(self):
        """Update tooltip with suggested word count range"""
        project_type = self.project_type_combo.currentData()
        if project_type:
            min_words, max_words = project_type.get_target_word_count_range()
            if min_words > 0:
                self.word_count_spin.setToolTip(
                    f"Typical range for {project_type.get_display_name('it')}: "
                    f"{min_words:,} - {max_words:,} words"
                )

    def _suggest_word_count(self):
        """Suggest a target word count based on project type"""
        project_type = self.project_type_combo.currentData()
        if project_type:
            min_words, max_words = project_type.get_target_word_count_range()
            if min_words > 0:
                # Suggest the midpoint
                suggested = (min_words + max_words) // 2
                self.word_count_spin.setValue(suggested)

    def _on_create_clicked(self):
        """Validate and accept the dialog"""
        # Validate title
        title = self.title_input.text().strip()
        is_valid, error_msg = Validators.validate_project_name(title)
        if not is_valid:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Invalid Title", error_msg)
            self.title_input.setFocus()
            return

        # Validate author
        author = self.author_input.text().strip()
        if not author:
            author = "Unknown"
        else:
            is_valid, error_msg = Validators.validate_text_input(
                author, min_length=1, max_length=100, field_name="Author name"
            )
            if not is_valid:
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.warning(self, "Invalid Author", error_msg)
                self.author_input.setFocus()
                return

        # Parse language
        language_map = {
            "🇮🇹 Italiano (it)": "it",
            "🇬🇧 English (en)": "en",
            "🇪🇸 Español (es)": "es",
            "🇫🇷 Français (fr)": "fr",
            "🇩🇪 Deutsch (de)": "de"
        }
        language_text = self.language_combo.currentText()
        language = language_map.get(language_text, "it")

        # Get project type
        project_type = self.project_type_combo.currentData()

        # Get optional metadata
        genre = self.genre_input.text().strip()
        target_word_count = self.word_count_spin.value()

        # Parse tags
        tags_text = self.tags_input.text().strip()
        tags = [tag.strip() for tag in tags_text.split(",") if tag.strip()]

        # Get template preference
        use_template = self.use_template_checkbox.isChecked()

        # Validate AI configuration (optional - API key not required)
        is_valid, error_msg = self.ai_config_widget.validate(require_api_key=False)
        if not is_valid:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Invalid AI Configuration", error_msg)
            return

        # Get AI configuration
        ai_provider_name = self.ai_config_widget.get_provider_name()
        ai_provider_config = self.ai_config_widget.get_config()

        # Store values
        self._title = title
        self._author = author
        self._language = language
        self._project_type = project_type
        self._genre = genre
        self._target_word_count = target_word_count
        self._tags = tags
        self._use_template = use_template
        self._ai_provider_name = ai_provider_name
        self._ai_provider_config = ai_provider_config

        # Accept dialog
        self.accept()

    def get_project_data(self) -> Tuple[str, str, str, ProjectType, str, int, List[str], bool, str, dict]:
        """
        Get the project data entered by the user.

        Returns:
            Tuple: (title, author, language, project_type, genre, target_word_count, tags, use_template,
                    ai_provider_name, ai_provider_config)
        """
        return (
            self._title,
            self._author,
            self._language,
            self._project_type,
            self._genre,
            self._target_word_count,
            self._tags,
            self._use_template,
            self._ai_provider_name,
            self._ai_provider_config
        )
