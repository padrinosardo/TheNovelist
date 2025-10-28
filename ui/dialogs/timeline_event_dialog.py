"""
Timeline Event Dialog - Edit/create timeline events
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel,
    QLineEdit, QTextEdit, QPushButton, QListWidget, QListWidgetItem,
    QMessageBox, QScrollArea, QFrame
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QFont
from typing import List, Optional
from models.timeline_event import TimelineEvent
from models.character import Character
from models.location import Location


class TimelineEventDialog(QDialog):
    """
    Dialog for creating/editing timeline events
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Timeline Event")
        self.setMinimumWidth(600)
        self.setMinimumHeight(600)

        self._current_event: Optional[TimelineEvent] = None
        self._all_characters: List[Character] = []
        self._all_locations: List[Location] = []

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
        header = QLabel("📅 Timeline Event Details")
        header.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        scroll_layout.addWidget(header)

        # === BASIC INFO ===
        form_layout = QFormLayout()
        form_layout.setSpacing(10)

        # Title
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Enter event title...")
        form_layout.addRow("Title *:", self.title_input)

        # Date (in-story date)
        self.date_input = QLineEdit()
        self.date_input.setPlaceholderText("e.g., January 1250, Day 5, Year 3...")
        form_layout.addRow("Date:", self.date_input)

        scroll_layout.addLayout(form_layout)

        # Description
        desc_label = QLabel("Description:")
        desc_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        scroll_layout.addWidget(desc_label)

        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Describe what happens in this event...")
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
        scroll_layout.addWidget(self.description_input)

        # === CHARACTERS SECTION ===
        characters_label = QLabel("Related Characters:")
        characters_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        scroll_layout.addWidget(characters_label)

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
        scroll_layout.addWidget(self.characters_list)

        # === LOCATIONS SECTION ===
        locations_label = QLabel("Related Locations:")
        locations_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        scroll_layout.addWidget(locations_label)

        self.locations_list = QListWidget()
        self.locations_list.setMaximumHeight(120)
        self.locations_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self.locations_list.setStyleSheet("""
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
        scroll_layout.addWidget(self.locations_list)

        # === NOTES SECTION ===
        notes_label = QLabel("Notes:")
        notes_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        scroll_layout.addWidget(notes_label)

        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText("Additional notes...")
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
        scroll_layout.addWidget(self.notes_input)

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

        self.save_btn = QPushButton("Save Event")
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

    def load_context(self, characters: List[Character], locations: List[Location]):
        """
        Load context data (characters and locations)

        Args:
            characters: All characters in project
            locations: All locations in project
        """
        self._all_characters = characters
        self._all_locations = locations

        # Update characters list
        self.characters_list.clear()
        for char in characters:
            item = QListWidgetItem(f"👤 {char.name}")
            item.setData(Qt.ItemDataRole.UserRole, char.id)
            self.characters_list.addItem(item)

        # Update locations list
        self.locations_list.clear()
        for loc in locations:
            item = QListWidgetItem(f"📍 {loc.name}")
            item.setData(Qt.ItemDataRole.UserRole, loc.id)
            self.locations_list.addItem(item)

    def load_event(self, event: TimelineEvent):
        """
        Load an event for editing

        Args:
            event: TimelineEvent to edit
        """
        self._current_event = event

        # Load basic info
        self.title_input.setText(event.title)
        self.date_input.setText(event.date)
        self.description_input.setPlainText(event.description)
        self.notes_input.setPlainText(event.notes)

        # Select related characters
        for i in range(self.characters_list.count()):
            item = self.characters_list.item(i)
            char_id = item.data(Qt.ItemDataRole.UserRole)
            if char_id in event.characters:
                item.setSelected(True)

        # Select related locations
        for i in range(self.locations_list.count()):
            item = self.locations_list.item(i)
            loc_id = item.data(Qt.ItemDataRole.UserRole)
            if loc_id in event.locations:
                item.setSelected(True)

    def clear_form(self):
        """Clear the form for new event"""
        self._current_event = None

        self.title_input.clear()
        self.date_input.clear()
        self.description_input.clear()
        self.notes_input.clear()

        # Clear selections
        for i in range(self.characters_list.count()):
            self.characters_list.item(i).setSelected(False)

        for i in range(self.locations_list.count()):
            self.locations_list.item(i).setSelected(False)

    def _on_save_clicked(self):
        """Validate and save event"""
        # Validate title
        title = self.title_input.text().strip()
        if not title:
            QMessageBox.warning(
                self,
                "Invalid Title",
                "Please enter an event title."
            )
            self.title_input.setFocus()
            return

        # Get selected characters
        selected_characters = []
        for i in range(self.characters_list.count()):
            item = self.characters_list.item(i)
            if item.isSelected():
                char_id = item.data(Qt.ItemDataRole.UserRole)
                selected_characters.append(char_id)

        # Get selected locations
        selected_locations = []
        for i in range(self.locations_list.count()):
            item = self.locations_list.item(i)
            if item.isSelected():
                loc_id = item.data(Qt.ItemDataRole.UserRole)
                selected_locations.append(loc_id)

        # Create/update event
        if self._current_event:
            # Update existing
            self._current_event.title = title
            self._current_event.date = self.date_input.text().strip()
            self._current_event.description = self.description_input.toPlainText()
            self._current_event.characters = selected_characters
            self._current_event.locations = selected_locations
            self._current_event.notes = self.notes_input.toPlainText()
        else:
            # Create new
            self._current_event = TimelineEvent(
                title=title,
                date=self.date_input.text().strip(),
                description=self.description_input.toPlainText(),
                characters=selected_characters,
                locations=selected_locations,
                notes=self.notes_input.toPlainText()
            )

        # Accept dialog
        self.accept()

    def get_event(self) -> TimelineEvent:
        """
        Get the created/edited event

        Returns:
            TimelineEvent object
        """
        return self._current_event
