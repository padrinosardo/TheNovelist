"""
Characters List View - Grid of character cards
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                               QScrollArea, QFrame, QLabel, QGridLayout)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QPixmap, QFont
from typing import List
from models.character import Character
import os


class CharactersListView(QWidget):
    """
    Grid view showing all characters as clickable cards
    """

    # Signals
    character_clicked = Signal(str)  # character_id
    add_character_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._characters = []
        self._images_dir = None
        self._setup_ui()

    def _setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)

        # Header with title and add button
        header = self._create_header()
        layout.addWidget(header)

        # Scroll area for character cards
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #fafafa;
            }
        """)

        # Container for cards
        self.cards_container = QWidget()
        self.cards_layout = QGridLayout(self.cards_container)
        self.cards_layout.setSpacing(20)
        self.cards_layout.setContentsMargins(20, 20, 20, 20)
        self.cards_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        scroll.setWidget(self.cards_container)
        layout.addWidget(scroll)

    def _create_header(self):
        """Create the header with title and buttons"""
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background-color: white;
                border-bottom: 2px solid #e0e0e0;
                padding: 15px;
            }
        """)

        layout = QHBoxLayout(header)

        # Title
        title = QLabel("Characters")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        layout.addStretch()

        # Add Character button
        self.add_btn = QPushButton("+ New Character")
        self.add_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 14px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        self.add_btn.clicked.connect(self.add_character_requested.emit)
        layout.addWidget(self.add_btn)

        return header

    def load_characters(self, characters: List[Character], images_dir: str = None):
        """
        Load and display characters

        Args:
            characters: List of Character objects
            images_dir: Directory containing character images
        """
        self._characters = characters
        self._images_dir = images_dir

        # Clear existing cards
        self._clear_cards()

        # Create card for each character
        row = 0
        col = 0
        max_cols = 3  # 3 cards per row

        for character in characters:
            card = CharacterCard(character, images_dir)
            card.clicked.connect(self.character_clicked.emit)

            self.cards_layout.addWidget(card, row, col)

            col += 1
            if col >= max_cols:
                col = 0
                row += 1

    def _clear_cards(self):
        """Remove all character cards"""
        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def set_images_directory(self, images_dir: str):
        """
        Set the images directory

        Args:
            images_dir: Path to images directory
        """
        self._images_dir = images_dir


class CharacterCard(QFrame):
    """
    Single character card widget
    Shows thumbnail image, name, and truncated description
    """

    clicked = Signal(str)  # character_id

    def __init__(self, character: Character, images_dir: str = None, parent=None):
        super().__init__(parent)
        self.character = character
        self.images_dir = images_dir
        self._setup_ui()

    def _setup_ui(self):
        """Setup the card UI"""
        self.setFixedSize(250, 300)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        self.setStyleSheet("""
            CharacterCard {
                background-color: white;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
            }
            CharacterCard:hover {
                border: 2px solid #2196F3;
                background-color: #f5f5f5;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Image area
        image_container = QFrame()
        image_container.setFixedHeight(180)
        image_container.setStyleSheet("""
            QFrame {
                background-color: #f0f0f0;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
            }
        """)

        image_layout = QVBoxLayout(image_container)
        image_layout.setContentsMargins(0, 0, 0, 0)

        # Load image or show placeholder
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._load_image()

        image_layout.addWidget(self.image_label)
        layout.addWidget(image_container)

        # Info area
        info_container = QFrame()
        info_container.setStyleSheet("background-color: white;")
        info_layout = QVBoxLayout(info_container)
        info_layout.setContentsMargins(15, 10, 15, 10)

        # Name
        name_label = QLabel(self.character.name)
        name_font = QFont()
        name_font.setPointSize(14)
        name_font.setBold(True)
        name_label.setFont(name_font)
        name_label.setWordWrap(True)
        info_layout.addWidget(name_label)

        # Description (truncated)
        desc_text = self.character.description[:60] + "..." if len(self.character.description) > 60 else self.character.description
        if desc_text.strip():
            desc_label = QLabel(desc_text)
            desc_label.setWordWrap(True)
            desc_label.setStyleSheet("color: #666; font-size: 12px;")
            info_layout.addWidget(desc_label)

        info_layout.addStretch()

        layout.addWidget(info_container)

    def _load_image(self):
        """Load character image or show placeholder"""
        if self.character.images and self.images_dir:
            # Try to load first image
            image_path = os.path.join(self.images_dir, self.character.images[0])
            if os.path.exists(image_path):
                pixmap = QPixmap(image_path)
                if not pixmap.isNull():
                    # Scale to fit
                    scaled = pixmap.scaled(
                        250, 180,
                        Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                        Qt.TransformationMode.SmoothTransformation
                    )
                    self.image_label.setPixmap(scaled)
                    return

        # Show placeholder
        self.image_label.setText("📷\n\nNo Image")
        self.image_label.setStyleSheet("""
            font-size: 40px;
            color: #bbb;
        """)

    def mousePressEvent(self, event):
        """Handle mouse click"""
        self.clicked.emit(self.character.id)
        super().mousePressEvent(event)
