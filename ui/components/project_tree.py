"""
Project Tree Widget - Sidebar navigation
"""
from PySide6.QtWidgets import QTreeWidget, QTreeWidgetItem, QMenu
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QAction
from typing import List
from models.character import Character


class ProjectTree(QTreeWidget):
    """
    Tree widget for project navigation
    Shows: Project -> Manuscript, Characters -> individual characters
    """

    # Signals
    manuscript_selected = Signal()
    characters_list_selected = Signal()
    character_selected = Signal(str)  # character_id
    add_character_requested = Signal()
    delete_character_requested = Signal(str)  # character_id

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._current_characters = []

    def _setup_ui(self):
        """Setup the tree widget"""
        self.setHeaderHidden(True)
        self.setMinimumWidth(200)
        self.setMaximumWidth(300)

        # Connect signals
        self.itemClicked.connect(self._on_item_clicked)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)

        # Style
        self.setStyleSheet("""
            QTreeWidget {
                background-color: #f5f5f5;
                border: none;
                font-size: 13px;
            }
            QTreeWidget::item {
                padding: 5px;
            }
            QTreeWidget::item:selected {
                background-color: #2196F3;
                color: white;
            }
            QTreeWidget::item:hover {
                background-color: #e3f2fd;
            }
        """)

    def load_project(self, project_title: str, characters: List[Character]):
        """
        Load project data into tree

        Args:
            project_title: Title of the project
            characters: List of characters
        """
        self.clear()
        self._current_characters = characters

        # Root node - Project title
        root = QTreeWidgetItem(self)
        root.setText(0, f"📁 {project_title}")
        root.setExpanded(True)
        root.setData(0, Qt.ItemDataRole.UserRole, "root")

        # Manuscript node
        manuscript_item = QTreeWidgetItem(root)
        manuscript_item.setText(0, "📄 Manuscript")
        manuscript_item.setData(0, Qt.ItemDataRole.UserRole, "manuscript")

        # Characters node
        characters_item = QTreeWidgetItem(root)
        characters_item.setText(0, "👤 Characters")
        characters_item.setExpanded(True)
        characters_item.setData(0, Qt.ItemDataRole.UserRole, "characters")

        # Add individual characters
        for character in characters:
            char_item = QTreeWidgetItem(characters_item)
            char_item.setText(0, f"  📷 {character.name}")
            char_item.setData(0, Qt.ItemDataRole.UserRole, f"character:{character.id}")

    def update_characters(self, characters: List[Character]):
        """
        Update the characters list in the tree

        Args:
            characters: Updated list of characters
        """
        self._current_characters = characters

        # Find the Characters node
        root = self.topLevelItem(0)
        if not root:
            return

        characters_node = None
        for i in range(root.childCount()):
            child = root.child(i)
            if child.data(0, Qt.ItemDataRole.UserRole) == "characters":
                characters_node = child
                break

        if not characters_node:
            return

        # Clear existing character items
        characters_node.takeChildren()

        # Add updated characters
        for character in characters:
            char_item = QTreeWidgetItem(characters_node)
            char_item.setText(0, f"  📷 {character.name}")
            char_item.setData(0, Qt.ItemDataRole.UserRole, f"character:{character.id}")

        characters_node.setExpanded(True)

    def _on_item_clicked(self, item: QTreeWidgetItem, column: int):
        """
        Handle item click

        Args:
            item: Clicked item
            column: Column index
        """
        item_type = item.data(0, Qt.ItemDataRole.UserRole)

        if item_type == "manuscript":
            self.manuscript_selected.emit()
        elif item_type == "characters":
            self.characters_list_selected.emit()
        elif isinstance(item_type, str) and item_type.startswith("character:"):
            character_id = item_type.split(":", 1)[1]
            self.character_selected.emit(character_id)

    def _show_context_menu(self, position):
        """
        Show context menu on right-click

        Args:
            position: Click position
        """
        item = self.itemAt(position)
        if not item:
            return

        item_type = item.data(0, Qt.ItemDataRole.UserRole)

        menu = QMenu(self)

        if item_type == "characters":
            # Context menu for Characters node
            add_action = QAction("Add New Character", self)
            add_action.triggered.connect(self.add_character_requested.emit)
            menu.addAction(add_action)

        elif isinstance(item_type, str) and item_type.startswith("character:"):
            # Context menu for individual character
            character_id = item_type.split(":", 1)[1]

            delete_action = QAction("Delete Character", self)
            delete_action.triggered.connect(
                lambda: self.delete_character_requested.emit(character_id)
            )
            menu.addAction(delete_action)

        if not menu.isEmpty():
            menu.exec(self.viewport().mapToGlobal(position))

    def clear_project(self):
        """Clear the tree (when no project is open)"""
        self.clear()
        no_project_item = QTreeWidgetItem(self)
        no_project_item.setText(0, "No project open")
        no_project_item.setFlags(Qt.ItemFlag.NoItemFlags)

    def select_manuscript(self):
        """Programmatically select the manuscript item"""
        root = self.topLevelItem(0)
        if root:
            for i in range(root.childCount()):
                child = root.child(i)
                if child.data(0, Qt.ItemDataRole.UserRole) == "manuscript":
                    self.setCurrentItem(child)
                    self.manuscript_selected.emit()
                    break

    def select_characters_list(self):
        """Programmatically select the characters list"""
        root = self.topLevelItem(0)
        if root:
            for i in range(root.childCount()):
                child = root.child(i)
                if child.data(0, Qt.ItemDataRole.UserRole) == "characters":
                    self.setCurrentItem(child)
                    self.characters_list_selected.emit()
                    break
