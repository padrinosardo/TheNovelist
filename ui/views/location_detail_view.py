"""
Location Detail View - Edit/view a single location
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel,
    QLineEdit, QTextEdit, QComboBox, QPushButton, QScrollArea,
    QFrame, QListWidget, QListWidgetItem, QFileDialog, QMessageBox
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QFont, QPixmap, QTextCursor
from typing import List, Optional
from models.location import Location
from models.character import Character
from ui.components.context_sidebar import ContextSidebar, CollapsibleSidebarContainer
from ui.components.ai_chat_widget import AIChatWidget
import os


class LocationDetailView(QWidget):
    """
    Detail view for editing/viewing a location
    """

    # Signals
    save_requested = Signal(Location)  # Updated location
    cancel_requested = Signal()

    def __init__(self, location_manager=None, project_manager=None, ai_manager=None, parent=None):
        super().__init__(parent)
        self._current_location: Optional[Location] = None
        self._all_locations: List[Location] = []
        self._all_characters: List[Character] = []
        self._images_to_add: List[str] = []  # Paths to new images
        self.location_manager = location_manager
        self.project_manager = project_manager
        self.ai_manager = ai_manager
        self._setup_ui()

    def _setup_ui(self):
        """Setup the UI"""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Create the main form widget
        main_form_widget = self._create_main_form()

        # Create the context sidebar with AI chat
        self.sidebar = ContextSidebar(
            sidebar_id="location_sidebar",
            default_width=350,
            parent=self
        )

        # Create and add AI Chat Widget
        self.ai_chat = AIChatWidget(
            context_type="Location",
            ai_manager=self.ai_manager,
            project_manager=self.project_manager,
            entity_manager=self.location_manager,
            parent=self
        )
        self.ai_chat.text_to_insert.connect(self._on_insert_ai_text)
        self.sidebar.add_tab(self.ai_chat, "AI Assistant", "🤖")

        # Create container with main form and sidebar
        container = CollapsibleSidebarContainer(main_form_widget, self.sidebar, parent=self)
        main_layout.addWidget(container)

    def _create_main_form(self) -> QWidget:
        """Create the main form widget"""
        # Scroll area for long content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        scroll_widget = QWidget()
        layout = QVBoxLayout(scroll_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Header
        header = QLabel("📍 Location Details")
        header.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        layout.addWidget(header)

        # === BASIC INFO ===
        form_layout = QFormLayout()
        form_layout.setSpacing(10)

        # Name
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter location name...")
        form_layout.addRow("Name *:", self.name_input)

        # Type
        self.type_input = QLineEdit()
        self.type_input.setPlaceholderText("e.g., city, building, room, forest...")
        form_layout.addRow("Type:", self.type_input)

        # Parent location (hierarchy)
        self.parent_combo = QComboBox()
        self.parent_combo.addItem("(None - Top Level)", "")
        form_layout.addRow("Parent Location:", self.parent_combo)

        layout.addLayout(form_layout)

        # Description
        desc_label = QLabel("Description:")
        desc_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        layout.addWidget(desc_label)

        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Describe this location...")
        self.description_input.setMaximumHeight(150)
        self.description_input.setStyleSheet("""
            QTextEdit {
                background-color: white;
                color: #333;
                border: 1px solid #ccc;
                border-radius: 3px;
                padding: 5px;
            }
        """)
        layout.addWidget(self.description_input)

        # === IMAGES SECTION ===
        images_label = QLabel("Images:")
        images_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        layout.addWidget(images_label)

        self.images_list = QListWidget()
        self.images_list.setMaximumHeight(120)
        self.images_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #ccc;
                border-radius: 5px;
                background-color: #f9f9f9;
            }
        """)
        layout.addWidget(self.images_list)

        images_btn_layout = QHBoxLayout()
        images_btn_layout.setSpacing(10)

        self.add_image_btn = QPushButton("Add Image")
        self.add_image_btn.clicked.connect(self._add_image)
        images_btn_layout.addWidget(self.add_image_btn)

        self.remove_image_btn = QPushButton("Remove Selected")
        self.remove_image_btn.clicked.connect(self._remove_image)
        images_btn_layout.addWidget(self.remove_image_btn)

        images_btn_layout.addStretch()
        layout.addLayout(images_btn_layout)

        # === CHARACTERS SECTION ===
        characters_label = QLabel("Characters Present:")
        characters_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        layout.addWidget(characters_label)

        self.characters_list = QListWidget()
        self.characters_list.setMaximumHeight(120)
        self.characters_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self.characters_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #ccc;
                border-radius: 5px;
                background-color: #f9f9f9;
            }
            QListWidget::item:selected {
                background-color: #2196F3;
                color: white;
            }
        """)
        layout.addWidget(self.characters_list)

        chars_hint = QLabel("💡 Tip: Select characters that are associated with this location")
        chars_hint.setStyleSheet("color: #666; font-style: italic; font-size: 11px;")
        layout.addWidget(chars_hint)

        # === NOTES SECTION ===
        notes_label = QLabel("Notes:")
        notes_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        layout.addWidget(notes_label)

        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText("Additional notes about this location...")
        self.notes_input.setMaximumHeight(100)
        self.notes_input.setStyleSheet("""
            QTextEdit {
                background-color: white;
                color: #333;
                border: 1px solid #ccc;
                border-radius: 3px;
                padding: 5px;
            }
        """)
        layout.addWidget(self.notes_input)

        # Add stretch
        layout.addStretch()

        scroll.setWidget(scroll_widget)

        # Container widget for scroll + buttons
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)

        container_layout.addWidget(scroll)

        # === BUTTONS ===
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(20, 10, 20, 20)
        button_layout.setSpacing(10)

        button_layout.addStretch()

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setMinimumWidth(100)
        self.cancel_btn.clicked.connect(self.cancel_requested.emit)
        button_layout.addWidget(self.cancel_btn)

        self.save_btn = QPushButton("Save Location")
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

        container_layout.addLayout(button_layout)

        return container

    def load_context(self, all_locations: List[Location], all_characters: List[Character]):
        """
        Load context data (other locations for parent selection, characters)

        Args:
            all_locations: All locations in project
            all_characters: All characters in project
        """
        self._all_locations = all_locations
        self._all_characters = all_characters

        # Update parent combo (will be filtered when loading location)
        self._update_parent_combo()

        # Update characters list
        self._update_characters_list()

    def load_location(self, location: Location):
        """
        Load a location for editing

        Args:
            location: Location to edit
        """
        self._current_location = location
        self._images_to_add = []

        # Load basic info
        self.name_input.setText(location.name)
        self.type_input.setText(location.location_type or "")
        self.description_input.setPlainText(location.description)
        self.notes_input.setPlainText(location.notes)

        # Load parent location
        self._update_parent_combo(exclude_id=location.id)
        if location.parent_location_id:
            index = self.parent_combo.findData(location.parent_location_id)
            if index >= 0:
                self.parent_combo.setCurrentIndex(index)

        # Load images
        self.images_list.clear()
        for image_path in location.images:
            item = QListWidgetItem(f"🖼️ {os.path.basename(image_path)}")
            item.setData(Qt.ItemDataRole.UserRole, image_path)
            self.images_list.addItem(item)

        # Load characters
        self._update_characters_list()
        for i in range(self.characters_list.count()):
            item = self.characters_list.item(i)
            char_id = item.data(Qt.ItemDataRole.UserRole)
            if char_id in location.characters_present:
                item.setSelected(True)

        # Set context for AI chat widget
        context_data = {
            'location_id': location.id,
            'name': location.name,
            'type': location.location_type or '',
            'description': location.description
        }
        self.ai_chat.set_context(context_data, entity=location)

    def clear_form(self):
        """Clear the form for new location"""
        self._current_location = None
        self._images_to_add = []

        self.name_input.clear()
        self.type_input.clear()
        self.description_input.clear()
        self.notes_input.clear()
        self.images_list.clear()

        self.parent_combo.setCurrentIndex(0)

        # Clear character selection
        for i in range(self.characters_list.count()):
            self.characters_list.item(i).setSelected(False)

    def _on_insert_ai_text(self, text: str):
        """
        Insert text from AI chat into description field

        Args:
            text: Text to insert
        """
        # Get current cursor position in description field
        cursor = self.description_input.textCursor()

        # If there's selected text, replace it
        if cursor.hasSelection():
            cursor.removeSelectedText()

        # Insert new text at cursor position
        cursor.insertText(text)

        # Set focus back to description field
        self.description_input.setFocus()

    def _update_parent_combo(self, exclude_id: str = None):
        """
        Update parent location combo box

        Args:
            exclude_id: Location ID to exclude (to prevent circular reference)
        """
        self.parent_combo.clear()
        self.parent_combo.addItem("(None - Top Level)", "")

        for loc in self._all_locations:
            if exclude_id and loc.id == exclude_id:
                continue  # Don't allow location to be its own parent

            location_type = f" ({loc.location_type})" if loc.location_type else ""
            self.parent_combo.addItem(f"{loc.name}{location_type}", loc.id)

    def _update_characters_list(self):
        """Update characters list"""
        self.characters_list.clear()

        for char in self._all_characters:
            item = QListWidgetItem(f"👤 {char.name}")
            item.setData(Qt.ItemDataRole.UserRole, char.id)
            self.characters_list.addItem(item)

    def _add_image(self):
        """Add image to location"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Image",
            "",
            "Images (*.png *.jpg *.jpeg *.gif *.bmp)"
        )

        if file_path:
            # Add to list
            item = QListWidgetItem(f"🖼️ {os.path.basename(file_path)}")
            item.setData(Qt.ItemDataRole.UserRole, file_path)
            self.images_list.addItem(item)

            # Track new image
            self._images_to_add.append(file_path)

    def _remove_image(self):
        """Remove selected image"""
        current_item = self.images_list.currentItem()
        if current_item:
            image_path = current_item.data(Qt.ItemDataRole.UserRole)

            # Remove from new images list if present
            if image_path in self._images_to_add:
                self._images_to_add.remove(image_path)

            # Remove from list widget
            row = self.images_list.row(current_item)
            self.images_list.takeItem(row)

    def _on_save_clicked(self):
        """Validate and save location"""
        # Validate name
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(
                self,
                "Invalid Name",
                "Please enter a location name."
            )
            self.name_input.setFocus()
            return

        # Get parent location
        parent_location_id = self.parent_combo.currentData() or ""

        # Get selected characters
        selected_characters = []
        for i in range(self.characters_list.count()):
            item = self.characters_list.item(i)
            if item.isSelected():
                char_id = item.data(Qt.ItemDataRole.UserRole)
                selected_characters.append(char_id)

        # Get all images (existing + new)
        all_images = []
        for i in range(self.images_list.count()):
            item = self.images_list.item(i)
            image_path = item.data(Qt.ItemDataRole.UserRole)
            all_images.append(image_path)

        # Create/update location
        if self._current_location:
            # Update existing
            location = self._current_location
            location.name = name
            location.description = self.description_input.toPlainText()
            location.location_type = self.type_input.text().strip()
            location.parent_location_id = parent_location_id
            location.characters_present = selected_characters
            location.images = all_images
            location.notes = self.notes_input.toPlainText()
        else:
            # Create new
            location = Location(
                name=name,
                description=self.description_input.toPlainText(),
                location_type=self.type_input.text().strip(),
                parent_location_id=parent_location_id,
                characters_present=selected_characters,
                images=all_images,
                notes=self.notes_input.toPlainText()
            )

        # Emit save signal
        self.save_requested.emit(location)
