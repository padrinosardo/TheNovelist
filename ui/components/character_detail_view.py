"""
Character Detail View - Form for editing a single character
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QLineEdit, QTextEdit, QPushButton, QScrollArea,
                               QFrame, QMessageBox)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QFont
from .image_gallery import ImageGalleryWidget
from managers.character_manager import CharacterManager


class CharacterDetailView(QWidget):
    """
    Detailed form for viewing and editing a single character
    """

    # Signals
    character_updated = Signal()
    character_deleted = Signal(str)  # character_id
    back_requested = Signal()

    def __init__(self, character_manager: CharacterManager = None, parent=None):
        super().__init__(parent)
        self.character_manager = character_manager
        self._current_character_id = None
        self._setup_ui()

    def _setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Scroll area for form
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: white;
            }
        """)

        # Form container
        form_container = QWidget()
        form_layout = QVBoxLayout(form_container)
        form_layout.setContentsMargins(30, 20, 30, 20)
        form_layout.setSpacing(20)

        # Back button
        back_btn = QPushButton("← Back to Characters")
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #2196F3;
                border: none;
                text-align: left;
                padding: 5px;
                font-size: 13px;
            }
            QPushButton:hover {
                color: #1976D2;
                text-decoration: underline;
            }
        """)
        back_btn.clicked.connect(self.back_requested.emit)
        form_layout.addWidget(back_btn)

        # Title
        title = QLabel("Character Details")
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title.setFont(title_font)
        form_layout.addWidget(title)

        # Name field
        name_label = QLabel("Name")
        name_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        form_layout.addWidget(name_label)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter character name...")
        self.name_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                font-size: 14px;
                border: 2px solid #ddd;
                border-radius: 4px;
            }
            QLineEdit:focus {
                border: 2px solid #2196F3;
            }
        """)
        form_layout.addWidget(self.name_input)

        # Description field
        desc_label = QLabel("Description")
        desc_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        form_layout.addWidget(desc_label)

        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText(
            "Write a detailed description of the character...\n\n"
            "You can include:\n"
            "- Physical appearance\n"
            "- Personality traits\n"
            "- Background and history\n"
            "- Goals and motivations\n"
            "- Relationships with other characters\n"
            "- Any other relevant details"
        )
        self.description_input.setMinimumHeight(300)
        self.description_input.setStyleSheet("""
            QTextEdit {
                padding: 10px;
                font-size: 13px;
                border: 2px solid #ddd;
                border-radius: 4px;
                line-height: 1.6;
            }
            QTextEdit:focus {
                border: 2px solid #2196F3;
            }
        """)
        form_layout.addWidget(self.description_input)

        # Image gallery
        self.image_gallery = ImageGalleryWidget()
        self.image_gallery.image_added.connect(self._on_image_added)
        self.image_gallery.image_removed.connect(self._on_image_removed)
        form_layout.addWidget(self.image_gallery)

        # Action buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()

        # Delete button
        self.delete_btn = QPushButton("🗑️ Delete Character")
        self.delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                padding: 12px 24px;
                font-size: 14px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        self.delete_btn.clicked.connect(self._on_delete)
        buttons_layout.addWidget(self.delete_btn)

        # Save button
        self.save_btn = QPushButton("💾 Save Changes")
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 12px 24px;
                font-size: 14px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.save_btn.clicked.connect(self._on_save)
        buttons_layout.addWidget(self.save_btn)

        form_layout.addLayout(buttons_layout)

        scroll.setWidget(form_container)
        layout.addWidget(scroll)

    def set_character_manager(self, character_manager: CharacterManager):
        """
        Set the character manager

        Args:
            character_manager: CharacterManager instance
        """
        self.character_manager = character_manager

    def load_character(self, character_id: str):
        """
        Load character data into the form

        Args:
            character_id: Character ID to load
        """
        if not self.character_manager:
            return

        character = self.character_manager.get_character(character_id)
        if not character:
            return

        self._current_character_id = character_id

        # Load data into form
        self.name_input.setText(character.name)
        self.description_input.setPlainText(character.description)

        # Load images
        image_paths = self.character_manager.get_character_image_paths(character_id)
        self.image_gallery.load_images(image_paths)

    def clear_form(self):
        """Clear all form fields"""
        self._current_character_id = None
        self.name_input.clear()
        self.description_input.clear()
        self.image_gallery.load_images([])

    def _on_save(self):
        """Handle save button click"""
        if not self.character_manager or not self._current_character_id:
            return

        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(
                self,
                "Invalid Input",
                "Please enter a character name."
            )
            return

        description = self.description_input.toPlainText().strip()

        # Update character
        self.character_manager.update_character(
            self._current_character_id,
            name=name,
            description=description
        )

        self.character_updated.emit()

        QMessageBox.information(
            self,
            "Saved",
            "Character updated successfully!"
        )

    def _on_delete(self):
        """Handle delete button click"""
        if not self._current_character_id:
            return

        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            "Are you sure you want to delete this character?\n"
            "This action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            character_id = self._current_character_id
            self.character_deleted.emit(character_id)

    def _on_image_added(self, source_path: str):
        """
        Handle image addition

        Args:
            source_path: Source image file path
        """
        if not self.character_manager or not self._current_character_id:
            return

        filename = self.character_manager.add_image_to_character(
            self._current_character_id,
            source_path
        )

        if filename:
            # Reload images
            image_paths = self.character_manager.get_character_image_paths(
                self._current_character_id
            )
            self.image_gallery.load_images(image_paths)

            self.character_updated.emit()
        else:
            QMessageBox.warning(
                self,
                "Error",
                "Could not add image to character."
            )

    def _on_image_removed(self, filename: str):
        """
        Handle image removal

        Args:
            filename: Image filename to remove
        """
        if not self.character_manager or not self._current_character_id:
            return

        success = self.character_manager.remove_image_from_character(
            self._current_character_id,
            filename
        )

        if success:
            # Reload images
            image_paths = self.character_manager.get_character_image_paths(
                self._current_character_id
            )
            self.image_gallery.load_images(image_paths)

            self.character_updated.emit()
