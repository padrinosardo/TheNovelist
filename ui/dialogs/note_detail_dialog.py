"""
Note Detail Dialog - Edit/create generic notes
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel,
    QLineEdit, QTextEdit, QComboBox, QPushButton, QCheckBox,
    QMessageBox, QScrollArea, QFrame, QGroupBox, QWidget
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QFont, QColor
from typing import List, Optional
from models.note import Note
from models.character import Character
from models.location import Location


class NoteDetailDialog(QDialog):
    """
    Dialog for creating/editing generic notes
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Note Details")
        self.setMinimumWidth(600)
        self.setMinimumHeight(700)

        self._current_note: Optional[Note] = None
        self._all_characters: List[Character] = []
        self._all_locations: List[Location] = []
        self._all_scenes: List[tuple] = []  # (scene_id, scene_title)

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
        header = QLabel("📝 Note Details")
        header.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        scroll_layout.addWidget(header)

        # === BASIC INFO ===
        basic_group = QGroupBox("Basic Information")
        basic_layout = QFormLayout()
        basic_layout.setSpacing(10)

        # Title
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Enter note title...")
        basic_layout.addRow("Title *:", self.title_input)

        # Pinned checkbox
        self.pinned_checkbox = QCheckBox("Pin this note")
        self.pinned_checkbox.setToolTip("Pinned notes appear at the top of the list")
        basic_layout.addRow("", self.pinned_checkbox)

        # Color
        color_layout = QHBoxLayout()
        color_layout.setSpacing(10)

        self.color_combo = QComboBox()
        self.color_combo.addItem("No Color", "")
        self.color_combo.addItem("🟡 Yellow", "#FFF9C4")
        self.color_combo.addItem("🟢 Green", "#C8E6C9")
        self.color_combo.addItem("🔵 Blue", "#BBDEFB")
        self.color_combo.addItem("🟣 Purple", "#E1BEE7")
        self.color_combo.addItem("🔴 Red", "#FFCDD2")
        self.color_combo.addItem("🟠 Orange", "#FFE0B2")
        color_layout.addWidget(self.color_combo)

        self.color_preview = QLabel("     ")
        self.color_preview.setStyleSheet("background-color: white; border: 1px solid #ccc;")
        self.color_preview.setFixedSize(50, 25)
        color_layout.addWidget(self.color_preview)
        color_layout.addStretch()

        self.color_combo.currentIndexChanged.connect(self._update_color_preview)

        basic_layout.addRow("Color:", color_layout)

        basic_group.setLayout(basic_layout)
        scroll_layout.addWidget(basic_group)

        # Content
        content_label = QLabel("Content:")
        content_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        scroll_layout.addWidget(content_label)

        self.content_input = QTextEdit()
        self.content_input.setPlaceholderText("Write your note here...")
        self.content_input.setMinimumHeight(200)
        scroll_layout.addWidget(self.content_input)

        # === TAGS ===
        tags_label = QLabel("Tags:")
        tags_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        scroll_layout.addWidget(tags_label)

        self.tags_input = QLineEdit()
        self.tags_input.setPlaceholderText("Enter tags separated by commas (e.g., important, idea, todo)")
        scroll_layout.addWidget(self.tags_input)

        # === LINKS ===
        links_group = QGroupBox("Link to Entities (Optional)")
        links_layout = QFormLayout()
        links_layout.setSpacing(10)

        # Link to scene
        self.scene_combo = QComboBox()
        self.scene_combo.addItem("(No scene)", "")
        links_layout.addRow("Link to Scene:", self.scene_combo)

        # Link to character
        self.character_combo = QComboBox()
        self.character_combo.addItem("(No character)", "")
        links_layout.addRow("Link to Character:", self.character_combo)

        # Link to location
        self.location_combo = QComboBox()
        self.location_combo.addItem("(No location)", "")
        links_layout.addRow("Link to Location:", self.location_combo)

        links_group.setLayout(links_layout)
        scroll_layout.addWidget(links_group)

        links_hint = QLabel("💡 Tip: Linking notes to entities helps organize and find related information")
        links_hint.setStyleSheet("color: #666; font-style: italic; font-size: 11px;")
        scroll_layout.addWidget(links_hint)

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

        self.save_btn = QPushButton("Save Note")
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

    def load_context(self, characters: List[Character], locations: List[Location], scenes: List[tuple]):
        """
        Load context data (characters, locations, scenes)

        Args:
            characters: All characters in project
            locations: All locations in project
            scenes: List of (scene_id, scene_title) tuples
        """
        self._all_characters = characters
        self._all_locations = locations
        self._all_scenes = scenes

        # Update character combo
        self.character_combo.clear()
        self.character_combo.addItem("(No character)", "")
        for char in characters:
            self.character_combo.addItem(f"👤 {char.name}", char.id)

        # Update location combo
        self.location_combo.clear()
        self.location_combo.addItem("(No location)", "")
        for loc in locations:
            self.location_combo.addItem(f"📍 {loc.name}", loc.id)

        # Update scene combo
        self.scene_combo.clear()
        self.scene_combo.addItem("(No scene)", "")
        for scene_id, scene_title in scenes:
            self.scene_combo.addItem(f"📝 {scene_title}", scene_id)

    def load_note(self, note: Note):
        """
        Load a note for editing

        Args:
            note: Note to edit
        """
        self._current_note = note

        # Load basic info
        self.title_input.setText(note.title)
        self.content_input.setPlainText(note.content)
        self.pinned_checkbox.setChecked(note.pinned)

        # Load color
        if note.color:
            index = self.color_combo.findData(note.color)
            if index >= 0:
                self.color_combo.setCurrentIndex(index)

        # Load tags
        self.tags_input.setText(", ".join(note.tags))

        # Load links
        if note.linked_to_scene:
            index = self.scene_combo.findData(note.linked_to_scene)
            if index >= 0:
                self.scene_combo.setCurrentIndex(index)

        if note.linked_to_character:
            index = self.character_combo.findData(note.linked_to_character)
            if index >= 0:
                self.character_combo.setCurrentIndex(index)

        if note.linked_to_location:
            index = self.location_combo.findData(note.linked_to_location)
            if index >= 0:
                self.location_combo.setCurrentIndex(index)

        self._update_color_preview()

    def clear_form(self):
        """Clear the form for new note"""
        self._current_note = None

        self.title_input.clear()
        self.content_input.clear()
        self.pinned_checkbox.setChecked(False)
        self.color_combo.setCurrentIndex(0)
        self.tags_input.clear()

        self.scene_combo.setCurrentIndex(0)
        self.character_combo.setCurrentIndex(0)
        self.location_combo.setCurrentIndex(0)

        self._update_color_preview()

    def _update_color_preview(self):
        """Update color preview"""
        color = self.color_combo.currentData()
        if color:
            self.color_preview.setStyleSheet(f"background-color: {color}; border: 1px solid #ccc;")
        else:
            self.color_preview.setStyleSheet("background-color: white; border: 1px solid #ccc;")

    def _on_save_clicked(self):
        """Validate and save note"""
        # Validate title
        title = self.title_input.text().strip()
        if not title:
            QMessageBox.warning(
                self,
                "Invalid Title",
                "Please enter a note title."
            )
            self.title_input.setFocus()
            return

        # Get tags
        tags_text = self.tags_input.text().strip()
        tags = [tag.strip() for tag in tags_text.split(",") if tag.strip()]

        # Get links
        linked_scene = self.scene_combo.currentData() or ""
        linked_character = self.character_combo.currentData() or ""
        linked_location = self.location_combo.currentData() or ""

        # Create/update note
        if self._current_note:
            # Update existing
            self._current_note.title = title
            self._current_note.content = self.content_input.toPlainText()
            self._current_note.pinned = self.pinned_checkbox.isChecked()
            self._current_note.color = self.color_combo.currentData()
            self._current_note.tags = tags
            self._current_note.linked_to_scene = linked_scene
            self._current_note.linked_to_character = linked_character
            self._current_note.linked_to_location = linked_location
        else:
            # Create new
            self._current_note = Note(
                title=title,
                content=self.content_input.toPlainText(),
                pinned=self.pinned_checkbox.isChecked(),
                color=self.color_combo.currentData(),
                tags=tags,
                linked_to_scene=linked_scene,
                linked_to_character=linked_character,
                linked_to_location=linked_location
            )

        # Accept dialog
        self.accept()

    def get_note(self) -> Note:
        """
        Get the created/edited note

        Returns:
            Note object
        """
        return self._current_note
