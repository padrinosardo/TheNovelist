"""
Project Info Detail View - Edit project information
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel,
    QLineEdit, QComboBox, QPushButton, QScrollArea,
    QFrame, QMessageBox, QTextEdit, QCheckBox
)
from PySide6.QtCore import Signal, Qt, QTimer
from PySide6.QtGui import QFont, QShortcut, QKeySequence
from typing import Optional
from models.project import Project
from models.project_type import ProjectType
from datetime import datetime
from ui.components.markdown_editor import MarkdownEditor
from managers.ai.template_manager import TemplateManager
from ui.dialogs.context_preview_dialog import ContextPreviewDialog
from managers.ai.context_builder import CharacterContextBuilder
from managers.character_manager import CharacterManager
from ui.utils.project_utils import ProjectUtils


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
        self._recent_templates = []  # List of recent template IDs
        self._debounce_timer = None  # For performance optimization
        self._setup_ui()
        self._load_recent_templates()
        self._setup_keyboard_shortcuts()  # Step 8: Accessibility

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
        self.genre_input.textChanged.connect(self._on_genre_changed)
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

        # === STORY CONTEXT (AI Integration) ===
        layout.addSpacing(15)
        story_context_label = QLabel("🎭 Story Context (for AI)")
        story_context_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(story_context_label)

        story_context_hint = QLabel("ℹ️  These fields help AI understand your story better. All fields are optional.")
        story_context_hint.setStyleSheet("color: #666; font-style: italic; font-size: 11px;")
        layout.addWidget(story_context_hint)

        story_form = QFormLayout()
        story_form.setSpacing(10)

        # Synopsis
        synopsis_container = QWidget()
        synopsis_layout = QVBoxLayout(synopsis_container)
        synopsis_layout.setContentsMargins(0, 0, 0, 0)
        synopsis_layout.setSpacing(3)

        self.synopsis_input = QTextEdit()
        self.synopsis_input.setPlaceholderText(
            "Brief plot summary (max 1000 characters)\n"
            "Example: 'Detective Julie investigates her ex-partner's disappearance...'"
        )
        self.synopsis_input.setMaximumHeight(100)
        self.synopsis_input.textChanged.connect(self._on_synopsis_changed)
        synopsis_layout.addWidget(self.synopsis_input)

        self.synopsis_counter_label = QLabel("0 / 1000 characters")
        self.synopsis_counter_label.setStyleSheet("color: #666; font-size: 11px;")
        synopsis_layout.addWidget(self.synopsis_counter_label)

        story_form.addRow("Synopsis:", synopsis_container)

        # Setting - Time Period
        self.setting_time_input = QLineEdit()
        self.setting_time_input.setPlaceholderText("e.g., 2024 winter, Medieval times, Dystopian future")
        story_form.addRow("Setting (Time):", self.setting_time_input)

        # Setting - Location
        self.setting_location_input = QLineEdit()
        self.setting_location_input.setPlaceholderText("e.g., Milan, Fantasy world Eldoria, Mars colony")
        story_form.addRow("Setting (Place):", self.setting_location_input)

        # Narrative Tone (with suggestion)
        tone_container = QWidget()
        tone_layout = QVBoxLayout(tone_container)
        tone_layout.setContentsMargins(0, 0, 0, 0)
        tone_layout.setSpacing(2)

        self.narrative_tone_input = QLineEdit()
        self.narrative_tone_input.setPlaceholderText("e.g., dark, ironic, poetic, humorous")
        self.narrative_tone_input.textChanged.connect(self._check_field_conflicts)
        tone_layout.addWidget(self.narrative_tone_input)

        self.tone_suggestion_label = QLabel("")
        self.tone_suggestion_label.setStyleSheet("color: #2196F3; font-style: italic; font-size: 10px;")
        self.tone_suggestion_label.setVisible(False)
        tone_layout.addWidget(self.tone_suggestion_label)

        story_form.addRow("Tone:", tone_container)

        # Narrative POV (with suggestion)
        pov_container = QWidget()
        pov_layout = QVBoxLayout(pov_container)
        pov_layout.setContentsMargins(0, 0, 0, 0)
        pov_layout.setSpacing(2)

        self.narrative_pov_combo = QComboBox()
        self.narrative_pov_combo.addItem("-- Not specified --", "")
        self.narrative_pov_combo.addItem("First Person", "first_person")
        self.narrative_pov_combo.addItem("Third Person Limited", "third_limited")
        self.narrative_pov_combo.addItem("Third Person Omniscient", "third_omniscient")
        self.narrative_pov_combo.addItem("Multiple POVs", "multiple")
        pov_layout.addWidget(self.narrative_pov_combo)

        self.pov_suggestion_label = QLabel("")
        self.pov_suggestion_label.setStyleSheet("color: #2196F3; font-style: italic; font-size: 10px;")
        self.pov_suggestion_label.setVisible(False)
        pov_layout.addWidget(self.pov_suggestion_label)

        story_form.addRow("Point of View:", pov_container)

        # Themes
        self.themes_input = QLineEdit()
        self.themes_input.setPlaceholderText("Comma-separated: revenge, redemption, identity, trauma")
        story_form.addRow("Themes:", self.themes_input)

        # Target Audience (with conflict warning)
        audience_container = QWidget()
        audience_layout = QVBoxLayout(audience_container)
        audience_layout.setContentsMargins(0, 0, 0, 0)
        audience_layout.setSpacing(2)

        self.target_audience_input = QLineEdit()
        self.target_audience_input.setPlaceholderText("e.g., Young Adult, Adults 30+, Children 8-12")
        self.target_audience_input.textChanged.connect(self._check_field_conflicts)
        audience_layout.addWidget(self.target_audience_input)

        self.field_conflict_warning = QLabel("")
        self.field_conflict_warning.setWordWrap(True)
        self.field_conflict_warning.setStyleSheet("color: #f44336; font-size: 10px; font-weight: bold;")
        self.field_conflict_warning.setVisible(False)
        audience_layout.addWidget(self.field_conflict_warning)

        story_form.addRow("Target Audience:", audience_container)

        # Story Notes
        story_notes_container = QWidget()
        story_notes_layout = QVBoxLayout(story_notes_container)
        story_notes_layout.setContentsMargins(0, 0, 0, 0)
        story_notes_layout.setSpacing(3)

        self.story_notes_input = QTextEdit()
        self.story_notes_input.setPlaceholderText(
            "Additional notes about your story, atmosphere, key messages, etc.\n"
            "This is a free-form field for any context you want AI to know."
        )
        self.story_notes_input.setMaximumHeight(120)
        self.story_notes_input.textChanged.connect(self._on_story_notes_changed)
        story_notes_layout.addWidget(self.story_notes_input)

        self.story_notes_counter_label = QLabel("0 / 2000 characters")
        self.story_notes_counter_label.setStyleSheet("color: #666; font-size: 11px;")
        story_notes_layout.addWidget(self.story_notes_counter_label)

        story_form.addRow("Story Notes:", story_notes_container)

        layout.addLayout(story_form)

        # Action buttons for Story Context
        story_actions_layout = QHBoxLayout()
        story_actions_layout.setSpacing(10)

        preview_story_context_btn = QPushButton("👁️ Preview")
        preview_story_context_btn.clicked.connect(self._on_preview_story_context)
        preview_story_context_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {background-color: #45a049;}
        """)
        story_actions_layout.addWidget(preview_story_context_btn)

        export_story_btn = QPushButton("📤 Export")
        export_story_btn.clicked.connect(self._on_export_story_context)
        export_story_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {background-color: #1976D2;}
        """)
        story_actions_layout.addWidget(export_story_btn)

        copy_to_guide_btn = QPushButton("📋 Copy to Writing Guide")
        copy_to_guide_btn.clicked.connect(self._on_copy_to_writing_guide)
        copy_to_guide_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {background-color: #F57C00;}
        """)
        story_actions_layout.addWidget(copy_to_guide_btn)

        story_actions_layout.addStretch()
        layout.addLayout(story_actions_layout)

        # === AI WRITING GUIDE (Advanced) ===
        layout.addSpacing(15)
        ai_guide_separator = QFrame()
        ai_guide_separator.setFrameShape(QFrame.Shape.HLine)
        ai_guide_separator.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(ai_guide_separator)

        ai_guide_label = QLabel("🤖 AI Writing Guide (Advanced)")
        ai_guide_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(ai_guide_label)

        ai_guide_desc = QLabel(
            "For advanced users: Create a custom Markdown guide that AI will use instead of Story Context fields. "
            "Load a template for your genre or write your own from scratch."
        )
        ai_guide_desc.setWordWrap(True)
        ai_guide_desc.setStyleSheet("color: #666; font-size: 11px; padding: 5px 0;")
        layout.addWidget(ai_guide_desc)

        # Enable/Disable checkbox
        self.ai_guide_enabled_checkbox = QCheckBox("Enable AI Writing Guide (overrides Story Context)")
        self.ai_guide_enabled_checkbox.stateChanged.connect(self._on_ai_guide_toggled)
        layout.addWidget(self.ai_guide_enabled_checkbox)

        # Conflict warning (shown when both systems have data)
        self.conflict_warning = QLabel(
            "⚠️  AI Writing Guide is enabled and will override Story Context fields above. "
            "The AI will only see the Writing Guide content, not the Story Context."
        )
        self.conflict_warning.setWordWrap(True)
        self.conflict_warning.setStyleSheet("""
            QLabel {
                background-color: #fff3cd;
                border: 1px solid #ffc107;
                border-radius: 4px;
                padding: 10px;
                color: #856404;
                font-size: 11px;
                margin: 10px 0;
            }
        """)
        self.conflict_warning.setVisible(False)  # Hidden by default
        layout.addWidget(self.conflict_warning)

        # Empty state message for Writing Guide
        self.guide_empty_state = QLabel(
            "💡 Tip: Load a template below to get started, or write your own custom guide from scratch. "
            "The Writing Guide helps you create consistent, genre-appropriate content."
        )
        self.guide_empty_state.setWordWrap(True)
        self.guide_empty_state.setStyleSheet("""
            QLabel {
                background-color: #e3f2fd;
                border: 1px solid #2196F3;
                border-radius: 4px;
                padding: 10px;
                color: #0d47a1;
                font-size: 11px;
                margin: 10px 0;
            }
        """)
        self.guide_empty_state.setVisible(False)  # Hidden by default
        layout.addWidget(self.guide_empty_state)

        # Template controls (template selector + load button)
        template_controls_layout = QHBoxLayout()
        template_controls_layout.setSpacing(10)

        template_label = QLabel("Template:")
        template_controls_layout.addWidget(template_label)

        self.template_selector = QComboBox()
        self.template_selector.setMinimumWidth(200)
        # Will be populated in __init__
        template_controls_layout.addWidget(self.template_selector)

        # Template suggestion label
        self.template_suggestion_label = QLabel("")
        self.template_suggestion_label.setStyleSheet("color: #4CAF50; font-style: italic; font-size: 11px;")
        self.template_suggestion_label.setVisible(False)
        template_controls_layout.addWidget(self.template_suggestion_label)

        # Preview Template button
        self.preview_template_btn = QPushButton("👁️ Preview")
        self.preview_template_btn.clicked.connect(self._on_preview_template)
        self.preview_template_btn.setToolTip("Preview template before loading")
        self.preview_template_btn.setStyleSheet("""
            QPushButton {
                background-color: #9C27B0;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #7B1FA2;
            }
        """)
        template_controls_layout.addWidget(self.preview_template_btn)

        self.load_template_btn = QPushButton("📥 Load")
        self.load_template_btn.clicked.connect(self._on_load_template)
        self.load_template_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        template_controls_layout.addWidget(self.load_template_btn)

        self.import_guide_btn = QPushButton("📄 Import")
        self.import_guide_btn.clicked.connect(self._on_import_writing_guide)
        self.import_guide_btn.setToolTip("Import Writing Guide from file")
        self.import_guide_btn.setStyleSheet("""
            QPushButton {
                background-color: #607D8B;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #455A64;
            }
        """)
        template_controls_layout.addWidget(self.import_guide_btn)

        self.clear_guide_btn = QPushButton("🗑️ Clear")
        self.clear_guide_btn.clicked.connect(self._on_clear_guide)
        self.clear_guide_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        template_controls_layout.addWidget(self.clear_guide_btn)

        template_controls_layout.addSpacing(20)

        self.preview_guide_btn = QPushButton("👁️ Preview")
        self.preview_guide_btn.clicked.connect(self._on_preview_writing_guide)
        self.preview_guide_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        template_controls_layout.addWidget(self.preview_guide_btn)

        self.export_guide_btn = QPushButton("📤 Export")
        self.export_guide_btn.clicked.connect(self._on_export_writing_guide)
        self.export_guide_btn.setToolTip("Export Writing Guide to file")
        self.export_guide_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        template_controls_layout.addWidget(self.export_guide_btn)

        template_controls_layout.addStretch()

        layout.addLayout(template_controls_layout)

        # Recent templates quick access
        self.recent_templates_widget = QWidget()
        recent_layout = QHBoxLayout(self.recent_templates_widget)
        recent_layout.setContentsMargins(0, 5, 0, 5)
        recent_layout.setSpacing(5)

        recent_label = QLabel("📌 Recent:")
        recent_label.setStyleSheet("color: #666; font-size: 11px;")
        recent_layout.addWidget(recent_label)

        self.recent_template_buttons = []
        for i in range(3):  # Max 3 recent templates
            btn = QPushButton("")
            btn.setVisible(False)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #E0E0E0;
                    border: 1px solid #BDBDBD;
                    border-radius: 3px;
                    padding: 4px 8px;
                    font-size: 10px;
                }
                QPushButton:hover {
                    background-color: #BDBDBD;
                }
            """)
            btn.clicked.connect(lambda checked, idx=i: self._on_recent_template_clicked(idx))
            self.recent_template_buttons.append(btn)
            recent_layout.addWidget(btn)

        recent_layout.addStretch()
        self.recent_templates_widget.setVisible(False)
        layout.addWidget(self.recent_templates_widget)

        # Markdown Editor
        self.ai_guide_editor = MarkdownEditor()
        self.ai_guide_editor.setMinimumHeight(400)
        self.ai_guide_editor.content_changed.connect(self._update_guidance_warnings)
        layout.addWidget(self.ai_guide_editor)

        # Initialize template manager and populate templates
        self.template_manager = TemplateManager()
        self._populate_templates()

        # Initially disable until checkbox is checked
        self._on_ai_guide_toggled(Qt.CheckState.Unchecked.value)

        # === AI CUSTOM COMMANDS ===
        layout.addSpacing(15)
        commands_separator = QFrame()
        commands_separator.setFrameShape(QFrame.Shape.HLine)
        commands_separator.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(commands_separator)

        commands_label = QLabel("⚡ AI Custom Commands")
        commands_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(commands_label)

        commands_desc = QLabel(
            "Define custom AI commands (like #sinossi, #dialoghi) that you can use in the AI Chat. "
            "Each command has a custom prompt template with variables."
        )
        commands_desc.setWordWrap(True)
        commands_desc.setStyleSheet("color: #666; font-size: 11px; padding: 5px 0;")
        layout.addWidget(commands_desc)

        # Commands info
        commands_count = len(self._current_project.ai_commands) if self._current_project else 0
        self.commands_info_label = QLabel(f"Current commands: {commands_count}")
        self.commands_info_label.setStyleSheet("color: #666; font-size: 11px; font-style: italic;")
        layout.addWidget(self.commands_info_label)

        # Manage commands button
        commands_button_layout = QHBoxLayout()

        self.manage_commands_btn = QPushButton("🛠️ Gestisci Comandi AI")
        self.manage_commands_btn.clicked.connect(self._on_manage_commands)
        self.manage_commands_btn.setStyleSheet("""
            QPushButton {
                background-color: #9C27B0;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7B1FA2;
            }
            QPushButton:pressed {
                background-color: #6A1B9A;
            }
        """)
        commands_button_layout.addWidget(self.manage_commands_btn)
        commands_button_layout.addStretch()

        layout.addLayout(commands_button_layout)

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

        # Story Context fields
        self.synopsis_input.setPlainText(project.synopsis)
        self.setting_time_input.setText(project.setting_time_period)
        self.setting_location_input.setText(project.setting_location)
        self.narrative_tone_input.setText(project.narrative_tone)

        # POV
        pov_idx = self.narrative_pov_combo.findData(project.narrative_pov)
        if pov_idx >= 0:
            self.narrative_pov_combo.setCurrentIndex(pov_idx)
        else:
            self.narrative_pov_combo.setCurrentIndex(0)  # Not specified

        # Themes
        themes_str = ", ".join(project.themes) if project.themes else ""
        self.themes_input.setText(themes_str)

        # Target audience
        self.target_audience_input.setText(project.target_audience)

        # Story notes
        self.story_notes_input.setPlainText(project.story_notes)

        # AI Writing Guide
        self.ai_guide_enabled_checkbox.setChecked(project.ai_writing_guide_enabled)
        self.ai_guide_editor.set_content(project.ai_writing_guide_content)

        # Dates (read-only)
        self.created_label.setText(self._format_date(project.created_date))
        self.modified_label.setText(self._format_date(project.modified_date))

        # Update description
        self._update_project_type_description()

        # Update guidance warnings based on loaded data
        self._update_guidance_warnings()

        # Update AI commands count
        commands_count = len(project.ai_commands)
        self.commands_info_label.setText(f"Current commands: {commands_count}")

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

        # Parse themes
        themes_str = self.themes_input.text().strip()
        themes = [theme.strip() for theme in themes_str.split(',') if theme.strip()] if themes_str else []

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
            tags=tags,
            # Story context fields
            synopsis=self.synopsis_input.toPlainText().strip(),
            setting_time_period=self.setting_time_input.text().strip(),
            setting_location=self.setting_location_input.text().strip(),
            narrative_tone=self.narrative_tone_input.text().strip(),
            narrative_pov=self.narrative_pov_combo.currentData(),
            themes=themes,
            target_audience=self.target_audience_input.text().strip(),
            story_notes=self.story_notes_input.toPlainText().strip(),
            # AI Writing Guide
            ai_writing_guide_enabled=self.ai_guide_enabled_checkbox.isChecked(),
            ai_writing_guide_content=self.ai_guide_editor.get_content(),
            # AI Custom Commands
            ai_commands=self._current_project.ai_commands
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

    # === AI WRITING GUIDE METHODS ===

    def _populate_templates(self):
        """Populate template selector with available templates"""
        templates = self.template_manager.get_available_templates()

        for template in templates:
            self.template_selector.addItem(template['name'], template['id'])

    def _on_ai_guide_toggled(self, state: int):
        """Handle AI Writing Guide checkbox toggle"""
        enabled = state == Qt.CheckState.Checked.value

        # Enable/disable editor and controls
        self.template_selector.setEnabled(enabled)
        self.preview_template_btn.setEnabled(enabled)
        self.load_template_btn.setEnabled(enabled)
        self.import_guide_btn.setEnabled(enabled)
        self.clear_guide_btn.setEnabled(enabled)
        self.preview_guide_btn.setEnabled(enabled)
        self.export_guide_btn.setEnabled(enabled)
        self.ai_guide_editor.setEnabled(enabled)

        # Show/hide recent templates
        if enabled and self._recent_templates:
            self.recent_templates_widget.setVisible(True)
        else:
            self.recent_templates_widget.setVisible(False)

        # Update warnings and guidance
        self._update_guidance_warnings()

    def _on_load_template(self):
        """Load selected template"""
        if not self._current_project:
            return

        # Get selected template ID
        template_id = self.template_selector.currentData()
        if not template_id:
            return

        # Load and fill template
        filled_template = self.template_manager.get_template_with_project_data(
            template_id,
            self._current_project
        )

        if filled_template:
            self.ai_guide_editor.set_content(filled_template)

            # Add to recent templates
            self._add_to_recent_templates(template_id)

            QMessageBox.information(
                self,
                "Template Loaded",
                f"Template '{self.template_selector.currentText()}' loaded successfully!\n\n"
                "You can now edit it to customize for your project."
            )
        else:
            QMessageBox.warning(
                self,
                "Error",
                "Could not load template. Please check the template files."
            )

    def _on_clear_guide(self):
        """Clear Writing Guide editor"""
        reply = QMessageBox.question(
            self,
            "Clear Writing Guide",
            "Are you sure you want to clear the entire Writing Guide?\n\n"
            "This action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.ai_guide_editor.clear()

    # === INPUT VALIDATION & CHARACTER COUNTERS ===

    def _on_synopsis_changed(self):
        """Update synopsis character counter and validate"""
        text = self.synopsis_input.toPlainText()
        length = len(text)
        max_length = 1000

        # Update counter
        self.synopsis_counter_label.setText(f"{length} / {max_length} characters")

        # Change color if exceeded
        if length > max_length:
            self.synopsis_counter_label.setStyleSheet("color: #f44336; font-size: 11px; font-weight: bold;")
        elif length > max_length * 0.9:  # Warning at 90%
            self.synopsis_counter_label.setStyleSheet("color: #ff9800; font-size: 11px;")
        else:
            self.synopsis_counter_label.setStyleSheet("color: #666; font-size: 11px;")

    def _on_story_notes_changed(self):
        """Update story notes character counter and validate"""
        text = self.story_notes_input.toPlainText()
        length = len(text)
        max_length = 2000

        # Update counter
        self.story_notes_counter_label.setText(f"{length} / {max_length} characters")

        # Change color if exceeded
        if length > max_length:
            self.story_notes_counter_label.setStyleSheet("color: #f44336; font-size: 11px; font-weight: bold;")
        elif length > max_length * 0.9:  # Warning at 90%
            self.story_notes_counter_label.setStyleSheet("color: #ff9800; font-size: 11px;")
        else:
            self.story_notes_counter_label.setStyleSheet("color: #666; font-size: 11px;")

    def _on_preview_story_context(self):
        """Preview Story Context as AI will receive it"""
        # Create temporary project with current form values
        temp_project = self._create_temp_project()

        # Build Story Context using ContextBuilder
        # Create a minimal builder just to get story context
        class StoryContextBuilder(CharacterContextBuilder):
            """Minimal builder just for previewing story context"""
            def _build_entity_context(self, entity):
                return ""

            def _build_relations_context(self, entity, **kwargs):
                return ""

        builder = StoryContextBuilder(temp_project, CharacterManager())

        # Get only the story context part
        story_context = builder._build_story_context()

        if not story_context:
            QMessageBox.information(
                self,
                "Empty Context",
                "Story Context is empty. Fill in at least one field to see the preview."
            )
            return

        # Show preview dialog
        dialog = ContextPreviewDialog(story_context, "Story Context", self)
        dialog.exec()

    def _on_preview_writing_guide(self):
        """Preview AI Writing Guide as AI will receive it"""
        guide_content = self.ai_guide_editor.get_content().strip()

        if not guide_content:
            QMessageBox.information(
                self,
                "Empty Guide",
                "AI Writing Guide is empty. Load a template or write content to preview."
            )
            return

        # Show preview dialog
        dialog = ContextPreviewDialog(guide_content, "AI Writing Guide", self)
        dialog.exec()

    def _create_temp_project(self) -> Project:
        """Create a temporary Project from current form values for preview"""
        # Parse themes from comma-separated string
        themes_text = self.themes_input.text().strip()
        themes = [t.strip() for t in themes_text.split(',') if t.strip()] if themes_text else []

        return Project(
            title=self.title_input.text() or "Untitled",
            author=self.author_input.text() or "Unknown",
            genre=self.genre_input.text(),
            language=self.language_combo.currentData() or "it",
            project_type=self.project_type_combo.currentData() or ProjectType.NOVEL,
            synopsis=self.synopsis_input.toPlainText(),
            setting_time_period=self.setting_time_input.text(),
            setting_location=self.setting_location_input.text(),
            narrative_tone=self.narrative_tone_input.text(),
            narrative_pov=self.narrative_pov_combo.currentData() or "",
            themes=themes,
            target_audience=self.target_audience_input.text(),
            story_notes=self.story_notes_input.toPlainText(),
            ai_writing_guide_enabled=self.ai_guide_enabled_checkbox.isChecked(),
            ai_writing_guide_content=self.ai_guide_editor.get_content()
        )

    def _update_guidance_warnings(self):
        """Update warning and guidance messages based on current state"""
        # Check if Writing Guide is enabled
        guide_enabled = self.ai_guide_enabled_checkbox.isChecked()
        guide_has_content = bool(self.ai_guide_editor.get_content().strip())

        # Check if Story Context has data
        story_context_has_data = any([
            self.synopsis_input.toPlainText().strip(),
            self.setting_time_input.text().strip(),
            self.setting_location_input.text().strip(),
            self.narrative_tone_input.text().strip(),
            self.narrative_pov_combo.currentData(),
            self.themes_input.text().strip(),
            self.target_audience_input.text().strip(),
            self.story_notes_input.toPlainText().strip()
        ])

        # Show conflict warning if both systems have data
        show_conflict = guide_enabled and guide_has_content and story_context_has_data
        self.conflict_warning.setVisible(show_conflict)

        # Show empty state tip if Writing Guide is enabled but empty
        show_empty_tip = guide_enabled and not guide_has_content
        self.guide_empty_state.setVisible(show_empty_tip)

    # === STEP 2: ENHANCED TEMPLATE SYSTEM ===

    def _on_genre_changed(self, text: str):
        """Auto-suggest template, POV, and tone when genre changes"""
        genre = text.strip().lower()

        if not genre:
            self.template_suggestion_label.setVisible(False)
            self.pov_suggestion_label.setVisible(False)
            self.tone_suggestion_label.setVisible(False)
            return

        # 1. Template suggestion
        suggested_id = self.template_manager.suggest_template_for_genre(text)
        for i in range(self.template_selector.count()):
            if self.template_selector.itemData(i) == suggested_id:
                template_name = self.template_selector.itemText(i)
                self.template_suggestion_label.setText(f"💡 Suggested: {template_name}")
                self.template_suggestion_label.setVisible(True)
                if self.ai_guide_enabled_checkbox.isChecked():
                    self.template_selector.setCurrentIndex(i)
                break
        else:
            self.template_suggestion_label.setVisible(False)

        # 2. POV suggestion
        pov_suggestions = self._suggest_pov_for_genre(genre)
        if pov_suggestions:
            self.pov_suggestion_label.setText(f"💡 Suggested: {', '.join(pov_suggestions)}")
            self.pov_suggestion_label.setVisible(True)
        else:
            self.pov_suggestion_label.setVisible(False)

        # 3. Tone suggestion
        tone_suggestions = self._suggest_tone_for_genre(genre)
        if tone_suggestions:
            self.tone_suggestion_label.setText(f"💡 Suggested: {', '.join(tone_suggestions)}")
            self.tone_suggestion_label.setVisible(True)
        else:
            self.tone_suggestion_label.setVisible(False)

    def _on_preview_template(self):
        """Preview template before loading"""
        template_id = self.template_selector.currentData()
        if not template_id or not self._current_project:
            return

        # Load and fill template
        filled_template = self.template_manager.get_template_with_project_data(
            template_id,
            self._current_project
        )

        if not filled_template:
            QMessageBox.warning(self, "Error", "Could not load template preview.")
            return

        # Show preview dialog
        dialog = ContextPreviewDialog(
            filled_template,
            f"Template Preview: {self.template_selector.currentText()}",
            self
        )
        dialog.exec()

    def _on_recent_template_clicked(self, index: int):
        """Load template from recent templates"""
        if index >= len(self._recent_templates):
            return

        template_id = self._recent_templates[index]

        # Find and select the template in combobox
        for i in range(self.template_selector.count()):
            if self.template_selector.itemData(i) == template_id:
                self.template_selector.setCurrentIndex(i)
                # Auto-load the template
                self._on_load_template()
                return

    def _load_recent_templates(self):
        """Load recent templates from settings"""
        import json
        import os

        settings_file = os.path.expanduser("~/.thenovelist/recent_templates.json")

        if os.path.exists(settings_file):
            try:
                with open(settings_file, 'r') as f:
                    self._recent_templates = json.load(f)
            except Exception as e:
                print(f"Could not load recent templates: {e}")
                self._recent_templates = []
        else:
            self._recent_templates = []

        self._update_recent_templates_ui()

    def _save_recent_templates(self):
        """Save recent templates to settings"""
        import json
        import os

        settings_dir = os.path.expanduser("~/.thenovelist")
        os.makedirs(settings_dir, exist_ok=True)

        settings_file = os.path.join(settings_dir, "recent_templates.json")

        try:
            with open(settings_file, 'w') as f:
                json.dump(self._recent_templates, f)
        except Exception as e:
            print(f"Could not save recent templates: {e}")

    def _add_to_recent_templates(self, template_id: str):
        """Add template to recent templates list"""
        # Remove if already exists (to move it to front)
        if template_id in self._recent_templates:
            self._recent_templates.remove(template_id)

        # Add to front
        self._recent_templates.insert(0, template_id)

        # Keep max 3
        self._recent_templates = self._recent_templates[:3]

        # Save and update UI
        self._save_recent_templates()
        self._update_recent_templates_ui()

    def _update_recent_templates_ui(self):
        """Update recent templates buttons"""
        # Get template names
        template_map = {tmpl['id']: tmpl['name'] for tmpl in self.template_manager.get_available_templates()}

        # Update buttons
        for i, btn in enumerate(self.recent_template_buttons):
            if i < len(self._recent_templates):
                template_id = self._recent_templates[i]
                template_name = template_map.get(template_id, template_id)
                btn.setText(template_name)
                btn.setVisible(True)
            else:
                btn.setVisible(False)

        # Show/hide widget
        if self._recent_templates and self.ai_guide_enabled_checkbox.isChecked():
            self.recent_templates_widget.setVisible(True)
        else:
            self.recent_templates_widget.setVisible(False)

    # === STEP 4: SMART FIELD DEPENDENCIES ===

    def _suggest_pov_for_genre(self, genre: str) -> list:
        """Suggest POV based on genre"""
        genre = genre.lower()

        if any(word in genre for word in ['thriller', 'noir', 'mystery', 'detective']):
            return ["First Person", "Third Person Limited"]
        elif any(word in genre for word in ['fantasy', 'epic', 'high fantasy']):
            return ["Third Person Omniscient", "Multiple POVs"]
        elif any(word in genre for word in ['romance', 'contemporary']):
            return ["First Person", "Multiple POVs"]
        elif any(word in genre for word in ['sci-fi', 'science fiction', 'cyberpunk']):
            return ["Third Person Limited", "First Person"]
        elif any(word in genre for word in ['horror', 'psychological']):
            return ["First Person"]
        else:
            return []

    def _suggest_tone_for_genre(self, genre: str) -> list:
        """Suggest narrative tone based on genre"""
        genre = genre.lower()

        if any(word in genre for word in ['thriller', 'noir', 'mystery']):
            return ["dark", "tense", "suspenseful"]
        elif any(word in genre for word in ['fantasy', 'epic']):
            return ["epic", "adventurous", "mystical"]
        elif any(word in genre for word in ['romance']):
            return ["emotional", "intimate", "hopeful"]
        elif any(word in genre for word in ['comedy', 'humor']):
            return ["humorous", "lighthearted", "witty"]
        elif any(word in genre for word in ['horror']):
            return ["dark", "eerie", "unsettling"]
        elif any(word in genre for word in ['sci-fi', 'cyberpunk']):
            return ["futuristic", "clinical", "philosophical"]
        elif any(word in genre for word in ['literary']):
            return ["introspective", "poetic", "contemplative"]
        else:
            return []

    def _check_field_conflicts(self):
        """Check for conflicts between tone and target audience"""
        tone = self.narrative_tone_input.text().lower()
        audience = self.target_audience_input.text().lower()

        if not tone or not audience:
            self.field_conflict_warning.setVisible(False)
            return

        # Detect children audience
        is_children = any(word in audience for word in ['children', 'kids', '8-12', 'elementary'])

        # Detect dark/mature tone
        is_dark_tone = any(word in tone for word in ['dark', 'violent', 'explicit', 'mature', 'graphic', 'disturbing'])

        if is_children and is_dark_tone:
            self.field_conflict_warning.setText("⚠️ Warning: Dark tone may not be appropriate for children audience")
            self.field_conflict_warning.setVisible(True)
        else:
            self.field_conflict_warning.setVisible(False)

    # === STEP 6: EXPORT/IMPORT CONTEXT ===

    def _on_export_story_context(self):
        """Export Story Context to Markdown file"""
        if not self._current_project:
            return

        content = ProjectUtils.story_context_to_markdown(self._current_project)
        file_path = ProjectUtils.export_to_markdown(
            content,
            f"Story Context - {self._current_project.title}",
            f"story_context_{self._current_project.title.replace(' ', '_')}"
        )

        if file_path:
            QMessageBox.information(self, "Export Successful", f"Story Context exported to:\n{file_path}")

    def _on_export_writing_guide(self):
        """Export Writing Guide to Markdown file"""
        content = self.ai_guide_editor.get_content().strip()

        if not content:
            QMessageBox.warning(self, "Empty Guide", "Writing Guide is empty. Nothing to export.")
            return

        title = self._current_project.title if self._current_project else "Writing Guide"
        file_path = ProjectUtils.export_to_markdown(
            content,
            f"AI Writing Guide - {title}",
            f"writing_guide_{title.replace(' ', '_')}"
        )

        if file_path:
            QMessageBox.information(self, "Export Successful", f"Writing Guide exported to:\n{file_path}")

    def _on_import_writing_guide(self):
        """Import Writing Guide from Markdown file"""
        content = ProjectUtils.import_from_markdown()

        if content:
            # Ask for confirmation if current content exists
            if self.ai_guide_editor.get_content().strip():
                reply = QMessageBox.question(
                    self,
                    "Replace Content?",
                    "Current Writing Guide content will be replaced. Continue?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply != QMessageBox.StandardButton.Yes:
                    return

            self.ai_guide_editor.set_content(content)
            QMessageBox.information(self, "Import Successful", "Writing Guide imported successfully!")

    # === STEP 7: QUICK ACTIONS MENU ===

    def _on_copy_to_writing_guide(self):
        """Copy Story Context fields to Writing Guide as Markdown"""
        if not self._current_project:
            return

        # Convert Story Context to Markdown
        content = ProjectUtils.story_context_to_markdown(self._current_project)

        # Ask for confirmation if Writing Guide has content
        if self.ai_guide_editor.get_content().strip():
            reply = QMessageBox.question(
                self,
                "Replace Writing Guide?",
                "Current Writing Guide content will be replaced with Story Context. Continue?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return

        # Set content and enable Writing Guide
        self.ai_guide_editor.set_content(content)
        self.ai_guide_enabled_checkbox.setChecked(True)

        QMessageBox.information(
            self,
            "Copied Successfully",
            "Story Context copied to Writing Guide!\n\n"
            "You can now edit it to add custom commands and guidelines."
        )

    # === AI COMMANDS MANAGEMENT ===

    def _on_manage_commands(self):
        """Open dialog to manage AI commands"""
        if not self._current_project:
            QMessageBox.warning(
                self,
                "No Project",
                "Please load a project first."
            )
            return

        from ui.dialogs.ai_commands_dialog import AICommandsDialog

        # Open dialog with current commands
        dialog = AICommandsDialog(self._current_project.ai_commands, self)

        # If user accepted changes, update project
        if dialog.exec():
            updated_commands = dialog.get_commands()
            self._current_project.ai_commands = updated_commands

            # Update info label
            self.commands_info_label.setText(f"Current commands: {len(updated_commands)}")

            QMessageBox.information(
                self,
                "Commands Updated",
                f"AI commands updated successfully!\n\n"
                f"Total commands: {len(updated_commands)}\n\n"
                f"Remember to save the project to persist the changes."
            )

    # === STEP 8: ACCESSIBILITY - KEYBOARD SHORTCUTS ===

    def _setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts for quick actions"""
        # Ctrl/Cmd + P: Preview Context
        QShortcut(QKeySequence("Ctrl+P"), self, self._shortcut_preview)

        # Ctrl/Cmd + E: Toggle Writing Guide
        QShortcut(QKeySequence("Ctrl+E"), self, self._shortcut_toggle_guide)

        # Ctrl/Cmd + T: Load Template
        QShortcut(QKeySequence("Ctrl+T"), self, self._shortcut_load_template)

        # Ctrl/Cmd + Shift + E: Export
        QShortcut(QKeySequence("Ctrl+Shift+E"), self, self._shortcut_export)

        # Ctrl/Cmd + S: Save (delegates to parent)
        QShortcut(QKeySequence("Ctrl+S"), self, self._on_save)

    def _shortcut_preview(self):
        """Keyboard shortcut: Preview context"""
        if self.ai_guide_enabled_checkbox.isChecked():
            self._on_preview_writing_guide()
        else:
            self._on_preview_story_context()

    def _shortcut_toggle_guide(self):
        """Keyboard shortcut: Toggle Writing Guide"""
        self.ai_guide_enabled_checkbox.setChecked(
            not self.ai_guide_enabled_checkbox.isChecked()
        )

    def _shortcut_load_template(self):
        """Keyboard shortcut: Load template"""
        if self.ai_guide_enabled_checkbox.isChecked():
            self._on_load_template()

    def _shortcut_export(self):
        """Keyboard shortcut: Export"""
        if self.ai_guide_enabled_checkbox.isChecked():
            self._on_export_writing_guide()
        else:
            self._on_export_story_context()

    # === STEP 9: PERFORMANCE OPTIMIZATION ===

    def _on_genre_changed_debounced(self, text: str):
        """Debounced version of genre changed handler"""
        # Cancel existing timer
        if self._debounce_timer is not None:
            self._debounce_timer.stop()

        # Create new timer
        self._debounce_timer = QTimer()
        self._debounce_timer.setSingleShot(True)
        self._debounce_timer.timeout.connect(lambda: self._on_genre_changed(text))
        self._debounce_timer.start(300)  # 300ms debounce
