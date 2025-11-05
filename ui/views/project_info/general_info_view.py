"""
General Info View - Project details and story context with auto-save
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel,
                               QLineEdit, QComboBox, QTextEdit, QScrollArea, QFrame, QPushButton)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QFont
from typing import Optional
from models.project import Project
from models.project_type import ProjectType
from datetime import datetime
from utils.auto_save_manager import AutoSaveManager


class GeneralInfoView(QWidget):
    """General project information with auto-save - left-aligned layout"""

    # Signal emesso quando i dati devono essere salvati
    auto_save_requested = Signal(dict)  # {field_name: value, ...}

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_project: Optional[Project] = None
        self._auto_save_manager = None
        self._setup_ui()

    def _setup_ui(self):
        """Setup UI with left alignment"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Header with status indicator
        header_layout = QHBoxLayout()

        title_label = QLabel("📝 General Information")
        title_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        self.status_label = QLabel("✓ Saved")
        self.status_label.setStyleSheet("color: #4CAF50; font-size: 12px;")
        header_layout.addWidget(self.status_label)

        main_layout.addLayout(header_layout)

        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        scroll_widget = QWidget()
        layout = QVBoxLayout(scroll_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)

        # === PROJECT DETAILS ===
        details_label = QLabel("PROJECT DETAILS")
        details_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(details_label)

        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        form.setFormAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Enter project title...")
        self.title_input.setMinimumWidth(500)
        form.addRow("Title *:", self.title_input)

        self.author_input = QLineEdit()
        self.author_input.setPlaceholderText("Enter author name...")
        form.addRow("Author *:", self.author_input)

        self.language_combo = QComboBox()
        self.language_combo.addItem("🇮🇹 Italiano", "it")
        self.language_combo.addItem("🇬🇧 English", "en")
        self.language_combo.addItem("🇪🇸 Español", "es")
        self.language_combo.addItem("🇫🇷 Français", "fr")
        self.language_combo.addItem("🇩🇪 Deutsch", "de")
        form.addRow("Language *:", self.language_combo)

        # Genre with suggestions
        genre_container = QWidget()
        genre_layout = QVBoxLayout(genre_container)
        genre_layout.setContentsMargins(0, 0, 0, 0)
        genre_layout.setSpacing(3)

        self.genre_input = QLineEdit()
        self.genre_input.setPlaceholderText("e.g., Fantasy, Thriller, Romance...")
        genre_layout.addWidget(self.genre_input)

        self.genre_suggestion_label = QLabel("")
        self.genre_suggestion_label.setStyleSheet("color: #4CAF50; font-size: 10px;")
        self.genre_suggestion_label.setVisible(False)
        genre_layout.addWidget(self.genre_suggestion_label)

        form.addRow("Genre:", genre_container)

        self.project_type_combo = QComboBox()
        for pt in ProjectType:
            self.project_type_combo.addItem(f"{pt.get_icon()} {pt.get_display_name('it')}", pt.value)
        form.addRow("Project Type *:", self.project_type_combo)

        self.tags_input = QLineEdit()
        self.tags_input.setPlaceholderText("Comma-separated tags")
        form.addRow("Tags:", self.tags_input)

        layout.addLayout(form)

        # === STORY CONTEXT ===
        context_label = QLabel("STORY CONTEXT")
        context_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(context_label)

        context_form = QFormLayout()
        context_form.setSpacing(10)
        context_form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        context_form.setFormAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

        # Synopsis - NO LIMITS (OPT #2) - Larger field for novel synopsis
        self.synopsis_input = QTextEdit()
        self.synopsis_input.setPlaceholderText("Brief plot summary...")
        self.synopsis_input.setMinimumHeight(400)  # Force field to be at least 400px tall
        self.synopsis_input.setMinimumWidth(700)   # Force field to be at least 700px wide
        context_form.addRow("Synopsis:", self.synopsis_input)

        self.setting_time_input = QLineEdit()
        self.setting_time_input.setPlaceholderText("e.g., 2024 winter, Medieval times")
        context_form.addRow("Setting (Time):", self.setting_time_input)

        self.setting_location_input = QLineEdit()
        self.setting_location_input.setPlaceholderText("e.g., Milan, Fantasy world")
        context_form.addRow("Setting (Place):", self.setting_location_input)

        # Tone with suggestions + Apply button (OPT #3)
        tone_container = QWidget()
        tone_layout = QHBoxLayout(tone_container)
        tone_layout.setContentsMargins(0, 0, 0, 0)
        tone_layout.setSpacing(5)

        self.narrative_tone_input = QLineEdit()
        self.narrative_tone_input.setPlaceholderText("e.g., dark, ironic, poetic")
        tone_layout.addWidget(self.narrative_tone_input, 1)

        self.tone_apply_btn = QPushButton("Apply Suggestion")
        self.tone_apply_btn.setVisible(False)
        self.tone_apply_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 4px 12px;
                border-radius: 3px;
                font-size: 11px;
            }
            QPushButton:hover { background-color: #45a049; }
        """)
        tone_layout.addWidget(self.tone_apply_btn)

        context_form.addRow("Tone:", tone_container)

        # POV with suggestions + Apply (OPT #3)
        pov_container = QWidget()
        pov_layout = QHBoxLayout(pov_container)
        pov_layout.setContentsMargins(0, 0, 0, 0)
        pov_layout.setSpacing(5)

        self.narrative_pov_combo = QComboBox()
        self.narrative_pov_combo.addItem("-- Not specified --", "")
        self.narrative_pov_combo.addItem("First Person", "first_person")
        self.narrative_pov_combo.addItem("Third Person Limited", "third_limited")
        self.narrative_pov_combo.addItem("Third Person Omniscient", "third_omniscient")
        self.narrative_pov_combo.addItem("Multiple POVs", "multiple")
        pov_layout.addWidget(self.narrative_pov_combo, 1)

        self.pov_apply_btn = QPushButton("Apply Suggestion")
        self.pov_apply_btn.setVisible(False)
        self.pov_apply_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 4px 12px;
                border-radius: 3px;
                font-size: 11px;
            }
            QPushButton:hover { background-color: #45a049; }
        """)
        pov_layout.addWidget(self.pov_apply_btn)

        context_form.addRow("POV:", pov_container)

        self.themes_input = QLineEdit()
        self.themes_input.setPlaceholderText("Comma-separated themes")
        context_form.addRow("Themes:", self.themes_input)

        self.target_audience_input = QLineEdit()
        self.target_audience_input.setPlaceholderText("e.g., Young Adult, Adults 30+")
        context_form.addRow("Target Audience:", self.target_audience_input)

        # Story Notes - NO LIMITS (OPT #2)
        self.story_notes_input = QTextEdit()
        self.story_notes_input.setPlaceholderText("Additional story notes...")
        self.story_notes_input.setMaximumHeight(120)
        context_form.addRow("Story Notes:", self.story_notes_input)

        layout.addLayout(context_form)

        # === PROJECT DATES ===
        dates_label = QLabel("PROJECT DATES (read-only)")
        dates_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(dates_label)

        dates_form = QFormLayout()
        dates_form.setSpacing(5)
        dates_form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        dates_form.setFormAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

        self.created_label = QLabel()
        self.created_label.setStyleSheet("color: #666;")
        dates_form.addRow("Created:", self.created_label)

        self.modified_label = QLabel()
        self.modified_label.setStyleSheet("color: #666;")
        dates_form.addRow("Last Modified:", self.modified_label)

        layout.addLayout(dates_form)

        layout.addStretch()

        scroll.setWidget(scroll_widget)
        main_layout.addWidget(scroll)

        # Connect auto-save signals
        self._setup_auto_save()

    def _setup_auto_save(self):
        """Setup auto-save on all input fields"""
        # Text inputs (1s debounce)
        self.title_input.textChanged.connect(lambda: self._schedule_save())
        self.author_input.textChanged.connect(lambda: self._schedule_save())
        self.genre_input.textChanged.connect(lambda: self._schedule_save())
        self.tags_input.textChanged.connect(lambda: self._schedule_save())
        self.setting_time_input.textChanged.connect(lambda: self._schedule_save())
        self.setting_location_input.textChanged.connect(lambda: self._schedule_save())
        self.narrative_tone_input.textChanged.connect(lambda: self._schedule_save())
        self.themes_input.textChanged.connect(lambda: self._schedule_save())
        self.target_audience_input.textChanged.connect(lambda: self._schedule_save())

        # Text areas (2s debounce)
        self.synopsis_input.textChanged.connect(lambda: self._schedule_save(2000))
        self.story_notes_input.textChanged.connect(lambda: self._schedule_save(2000))

        # Combos (save immediately)
        self.language_combo.currentIndexChanged.connect(lambda: self._save_immediately())
        self.project_type_combo.currentIndexChanged.connect(lambda: self._save_immediately())
        self.narrative_pov_combo.currentIndexChanged.connect(lambda: self._save_immediately())

    def _schedule_save(self, delay=1000):
        """Schedule auto-save with debouncing"""
        if not self._current_project:
            return

        self.status_label.setText("📝 Editing...")
        self.status_label.setStyleSheet("color: #FF9800; font-size: 12px;")

        # Collect data and schedule save
        data = self._collect_form_data()
        if delay > 1000:
            # For text areas, use longer debounce
            pass  # Will be handled by auto_save_manager

        # Trigger auto-save via parent (MainWindow will handle)
        self.auto_save_requested.emit(data)

    def _save_immediately(self):
        """Save immediately without debounce"""
        if not self._current_project:
            return

        data = self._collect_form_data()
        self.auto_save_requested.emit(data)

    def _collect_form_data(self) -> dict:
        """Collect all form data"""
        tags_str = self.tags_input.text().strip()
        tags = [t.strip() for t in tags_str.split(',') if t.strip()] if tags_str else []

        themes_str = self.themes_input.text().strip()
        themes = [t.strip() for t in themes_str.split(',') if t.strip()] if themes_str else []

        return {
            'title': self.title_input.text().strip(),
            'author': self.author_input.text().strip(),
            'language': self.language_combo.currentData(),
            'genre': self.genre_input.text().strip(),
            'project_type': self.project_type_combo.currentData(),
            'tags': tags,
            'synopsis': self.synopsis_input.toPlainText().strip(),
            'setting_time_period': self.setting_time_input.text().strip(),
            'setting_location': self.setting_location_input.text().strip(),
            'narrative_tone': self.narrative_tone_input.text().strip(),
            'narrative_pov': self.narrative_pov_combo.currentData(),
            'themes': themes,
            'target_audience': self.target_audience_input.text().strip(),
            'story_notes': self.story_notes_input.toPlainText().strip()
        }

    def load_project(self, project: Project):
        """Load project data"""
        self._current_project = project

        # Disconnect signals temporarily
        self.title_input.blockSignals(True)
        self.author_input.blockSignals(True)

        # Load data
        self.title_input.setText(project.title)
        self.author_input.setText(project.author)

        lang_idx = self.language_combo.findData(project.language)
        if lang_idx >= 0:
            self.language_combo.setCurrentIndex(lang_idx)

        self.genre_input.setText(project.genre)

        # Handle both enum and string project_type
        pt_value = project.project_type.value if hasattr(project.project_type, 'value') else project.project_type
        pt_idx = self.project_type_combo.findData(pt_value)
        if pt_idx >= 0:
            self.project_type_combo.setCurrentIndex(pt_idx)

        self.tags_input.setText(", ".join(project.tags) if project.tags else "")

        # Story context
        self.synopsis_input.setPlainText(project.synopsis)
        self.setting_time_input.setText(project.setting_time_period)
        self.setting_location_input.setText(project.setting_location)
        self.narrative_tone_input.setText(project.narrative_tone)

        pov_idx = self.narrative_pov_combo.findData(project.narrative_pov)
        if pov_idx >= 0:
            self.narrative_pov_combo.setCurrentIndex(pov_idx)

        self.themes_input.setText(", ".join(project.themes) if project.themes else "")
        self.target_audience_input.setText(project.target_audience)
        self.story_notes_input.setPlainText(project.story_notes)

        # Dates
        self.created_label.setText(self._format_date(project.created_date))
        self.modified_label.setText(self._format_date(project.modified_date))

        # Re-enable signals
        self.title_input.blockSignals(False)
        self.author_input.blockSignals(False)

        # Update status
        self.status_label.setText("✓ Saved")
        self.status_label.setStyleSheet("color: #4CAF50; font-size: 12px;")

    def _format_date(self, date_str: str) -> str:
        """Format ISO date"""
        if not date_str:
            return "N/A"
        try:
            dt = datetime.fromisoformat(date_str)
            return dt.strftime("%d/%m/%Y %H:%M")
        except:
            return date_str

    def on_save_success(self):
        """Called when save completes successfully"""
        from datetime import datetime
        time_str = datetime.now().strftime("%H:%M")
        self.status_label.setText(f"✓ Saved {time_str}")
        self.status_label.setStyleSheet("color: #4CAF50; font-size: 12px;")

    def on_save_error(self, error_msg: str):
        """Called when save fails"""
        self.status_label.setText("⚠️ Error saving")
        self.status_label.setStyleSheet("color: #f44336; font-size: 12px;")
        self.status_label.setToolTip(error_msg)
