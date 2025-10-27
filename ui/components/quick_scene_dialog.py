"""
Quick Scene Switcher Dialog - Fast navigation between scenes
"""
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLineEdit,
                               QListWidget, QListWidgetItem, QPushButton, QLabel)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from typing import List, Optional
from models.manuscript_structure import ManuscriptStructure, Scene


class QuickSceneDialog(QDialog):
    """
    Quick scene switcher dialog with search functionality
    Similar to "Go to File" in IDEs
    """

    scene_selected = Signal(str)  # scene_id

    def __init__(self, manuscript_structure: ManuscriptStructure,
                 current_scene_id: Optional[str] = None, parent=None):
        """
        Initialize the quick scene switcher

        Args:
            manuscript_structure: Current manuscript structure
            current_scene_id: Currently selected scene ID
            parent: Parent widget
        """
        super().__init__(parent)
        self.manuscript_structure = manuscript_structure
        self.current_scene_id = current_scene_id
        self.all_scenes = []  # List of (scene, chapter_title) tuples
        self._setup_ui()
        self._populate_scenes()

    def _setup_ui(self):
        """Setup the user interface"""
        self.setWindowTitle("Go to Scene")
        self.setModal(True)
        self.setMinimumSize(600, 400)

        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # Search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Type to search scenes...")
        self.search_input.setStyleSheet("""
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
        self.search_input.textChanged.connect(self._filter_scenes)
        layout.addWidget(self.search_input)

        # Info label
        info_label = QLabel("↑↓ Navigate  •  Enter Select  •  Esc Cancel")
        info_label.setStyleSheet("color: #6c757d; font-size: 11px; padding: 5px;")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info_label)

        # Scene list
        self.scene_list = QListWidget()
        self.scene_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 13px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #f0f0f0;
            }
            QListWidget::item:selected {
                background-color: #2196F3;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #e3f2fd;
            }
        """)
        self.scene_list.itemDoubleClicked.connect(self._on_scene_double_clicked)
        layout.addWidget(self.scene_list)

        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()

        cancel_button = QPushButton("Cancel")
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                padding: 8px 20px;
                border-radius: 4px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_button)

        go_button = QPushButton("Go to Scene")
        go_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 8px 20px;
                border-radius: 4px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        go_button.clicked.connect(self._on_go_clicked)
        go_button.setDefault(True)
        buttons_layout.addWidget(go_button)

        layout.addLayout(buttons_layout)

        # Focus on search input
        self.search_input.setFocus()

    def _populate_scenes(self):
        """Populate the scene list with all scenes"""
        self.all_scenes.clear()

        # Collect all scenes with their chapter information
        for chapter in sorted(self.manuscript_structure.chapters, key=lambda c: c.order):
            for scene in sorted(chapter.scenes, key=lambda s: s.order):
                self.all_scenes.append((scene, chapter.title))

        # Display all scenes initially
        self._display_scenes(self.all_scenes)

    def _display_scenes(self, scenes: List[tuple]):
        """
        Display scenes in the list

        Args:
            scenes: List of (scene, chapter_title) tuples
        """
        self.scene_list.clear()

        for scene, chapter_title in scenes:
            # Create list item with scene info
            item_text = f"📝 {scene.title}"
            item_subtitle = f"   {chapter_title} • {scene.word_count} words"
            full_text = f"{item_text}\n{item_subtitle}"

            item = QListWidgetItem(full_text)
            item.setData(Qt.ItemDataRole.UserRole, scene.id)

            # Highlight current scene
            if scene.id == self.current_scene_id:
                font = QFont()
                font.setBold(True)
                item.setFont(font)
                item.setText(f"📝 {scene.title} (current)\n{item_subtitle}")

            self.scene_list.addItem(item)

        # Select first item if available
        if self.scene_list.count() > 0:
            self.scene_list.setCurrentRow(0)

    def _filter_scenes(self, search_text: str):
        """
        Filter scenes based on search text

        Args:
            search_text: Search query
        """
        if not search_text:
            # Show all scenes if search is empty
            self._display_scenes(self.all_scenes)
            return

        # Filter scenes by title or chapter title (case-insensitive)
        search_lower = search_text.lower()
        filtered_scenes = [
            (scene, chapter_title)
            for scene, chapter_title in self.all_scenes
            if search_lower in scene.title.lower() or search_lower in chapter_title.lower()
        ]

        self._display_scenes(filtered_scenes)

    def _on_scene_double_clicked(self, item: QListWidgetItem):
        """
        Handle scene double-click

        Args:
            item: Clicked list item
        """
        scene_id = item.data(Qt.ItemDataRole.UserRole)
        if scene_id:
            self.scene_selected.emit(scene_id)
            self.accept()

    def _on_go_clicked(self):
        """Handle Go button click"""
        current_item = self.scene_list.currentItem()
        if current_item:
            scene_id = current_item.data(Qt.ItemDataRole.UserRole)
            if scene_id:
                self.scene_selected.emit(scene_id)
                self.accept()

    def keyPressEvent(self, event):
        """Handle keyboard shortcuts"""
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            # Enter key - select scene
            if self.scene_list.currentItem():
                self._on_go_clicked()
        elif event.key() == Qt.Key.Key_Escape:
            # Escape key - cancel
            self.reject()
        elif event.key() == Qt.Key.Key_Down:
            # Down arrow - move to list if in search box
            if self.search_input.hasFocus():
                self.scene_list.setFocus()
        else:
            super().keyPressEvent(event)
