"""
Project Tree Widget - Sidebar navigation
"""
from PySide6.QtWidgets import QTreeWidget, QTreeWidgetItem, QMenu
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QAction
from typing import List, Optional
from models.character import Character
from models.manuscript_structure import ManuscriptStructure
from models.project import Project
from models.container_type import ContainerType
from datetime import datetime


class ProjectTree(QTreeWidget):
    """
    Tree widget for project navigation
    Shows: Project -> Manuscript, Characters -> individual characters
    """

    # Signals
    project_info_selected = Signal()  # NEW: Project info clicked
    manuscript_selected = Signal()
    chapter_selected = Signal(str)  # chapter_id
    scene_selected = Signal(str)  # scene_id
    characters_list_selected = Signal()
    character_selected = Signal(str)  # character_id
    statistics_selected = Signal()

    # Dynamic container signals
    locations_selected = Signal()
    research_selected = Signal()
    timeline_selected = Signal()
    worldbuilding_selected = Signal()
    sources_selected = Signal()
    keywords_selected = Signal()
    notes_selected = Signal()

    # Manuscript structure operations
    add_chapter_requested = Signal()
    add_scene_requested = Signal(str)  # chapter_id
    rename_chapter_requested = Signal(str)  # chapter_id
    rename_scene_requested = Signal(str)  # scene_id
    delete_chapter_requested = Signal(str)  # chapter_id
    delete_scene_requested = Signal(str)  # scene_id

    # Character operations
    add_character_requested = Signal()
    delete_character_requested = Signal(str)  # character_id

    # Dynamic container operations
    add_location_requested = Signal()
    add_research_note_requested = Signal()
    add_timeline_event_requested = Signal()
    add_worldbuilding_entry_requested = Signal()
    add_source_requested = Signal()
    add_keyword_requested = Signal()
    add_note_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._current_characters = []
        self._manuscript_structure: Optional[ManuscriptStructure] = None

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
                color: #212121;
            }
            QTreeWidget::item {
                padding: 5px;
                color: #212121;
            }
            QTreeWidget::item:selected {
                background-color: #2196F3;
                color: white;
            }
            QTreeWidget::item:hover {
                background-color: #e3f2fd;
                color: #212121;
            }
        """)

    def load_project(self, project: Project, characters: List[Character],
                     manuscript_structure: ManuscriptStructure = None):
        """
        Load project data into tree

        Args:
            project: Project object with all metadata
            characters: List of characters
            manuscript_structure: Manuscript structure with chapters and scenes
        """
        self.clear()
        self._current_characters = characters
        self._manuscript_structure = manuscript_structure

        # Root node - Project title
        root = QTreeWidgetItem(self)
        root.setText(0, f"📁 {project.title}")
        root.setExpanded(True)
        root.setData(0, Qt.ItemDataRole.UserRole, "root")

        # Project Info node - NEW!
        info_item = QTreeWidgetItem(root)
        info_item.setText(0, "📋 Project Info")
        info_item.setExpanded(True)
        info_item.setData(0, Qt.ItemDataRole.UserRole, "project_info")

        # Author
        author_item = QTreeWidgetItem(info_item)
        author_item.setText(0, f"  ✍️  Author: {project.author}")
        author_item.setData(0, Qt.ItemDataRole.UserRole, "info_detail")
        author_item.setFlags(Qt.ItemFlag.ItemIsEnabled)  # Non-selectable

        # Language
        language_names = {
            'it': 'Italiano (IT)',
            'en': 'English (EN)',
            'es': 'Español (ES)',
            'fr': 'Français (FR)',
            'de': 'Deutsch (DE)'
        }
        language_display = language_names.get(project.language, project.language.upper())
        language_item = QTreeWidgetItem(info_item)
        language_item.setText(0, f"  🌍 Language: {language_display}")
        language_item.setData(0, Qt.ItemDataRole.UserRole, "info_detail")
        language_item.setFlags(Qt.ItemFlag.ItemIsEnabled)  # Non-selectable

        # Project Type (for now, default to "Novel" - will be implemented in Milestone 2)
        type_item = QTreeWidgetItem(info_item)
        type_display = getattr(project, 'project_type', 'Novel')  # Default if not exists yet
        type_item.setText(0, f"  📚 Type: {type_display}")
        type_item.setData(0, Qt.ItemDataRole.UserRole, "info_detail")
        type_item.setFlags(Qt.ItemFlag.ItemIsEnabled)  # Non-selectable

        # Created Date
        try:
            created_date = datetime.fromisoformat(project.created_date)
            date_display = created_date.strftime("%b %d, %Y")
        except:
            date_display = project.created_date[:10] if len(project.created_date) >= 10 else project.created_date

        date_item = QTreeWidgetItem(info_item)
        date_item.setText(0, f"  📅 Created: {date_display}")
        date_item.setData(0, Qt.ItemDataRole.UserRole, "info_detail")
        date_item.setFlags(Qt.ItemFlag.ItemIsEnabled)  # Non-selectable

        # Manuscript node with hierarchy
        manuscript_item = QTreeWidgetItem(root)
        manuscript_item.setText(0, "📄 Manuscript")
        manuscript_item.setExpanded(True)
        manuscript_item.setData(0, Qt.ItemDataRole.UserRole, "manuscript")

        # Add chapters and scenes if structure exists
        if manuscript_structure:
            for chapter in sorted(manuscript_structure.chapters, key=lambda c: c.order):
                chapter_item = QTreeWidgetItem(manuscript_item)
                chapter_item.setText(0, f"  📖 {chapter.title}")
                chapter_item.setExpanded(True)
                chapter_item.setData(0, Qt.ItemDataRole.UserRole, f"chapter:{chapter.id}")

                # Add scenes under chapter
                for scene in sorted(chapter.scenes, key=lambda s: s.order):
                    scene_item = QTreeWidgetItem(chapter_item)
                    scene_item.setText(0, f"    📝 {scene.title}")
                    scene_item.setData(0, Qt.ItemDataRole.UserRole, f"scene:{scene.id}")

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

        # Statistics node
        statistics_item = QTreeWidgetItem(root)
        statistics_item.setText(0, "📊 Statistics")
        statistics_item.setData(0, Qt.ItemDataRole.UserRole, "statistics")

        # Dynamic containers based on project type
        available_containers = ContainerType.get_available_for_project_type(project.project_type)

        for container_type in available_containers:
            # Skip manuscript and characters (already added above)
            if container_type in [ContainerType.MANUSCRIPT, ContainerType.CHARACTERS]:
                continue

            # Get display info for this container
            icon, name = ContainerType.get_display_info(container_type, 'it')

            # Create tree item
            container_item = QTreeWidgetItem(root)
            container_item.setText(0, f"{icon} {name}")
            container_item.setData(0, Qt.ItemDataRole.UserRole, container_type.value)
            container_item.setExpanded(False)

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

        if item_type == "project_info":
            self.project_info_selected.emit()
        elif item_type == "manuscript":
            self.manuscript_selected.emit()
        elif isinstance(item_type, str) and item_type.startswith("chapter:"):
            chapter_id = item_type.split(":", 1)[1]
            self.chapter_selected.emit(chapter_id)
        elif isinstance(item_type, str) and item_type.startswith("scene:"):
            scene_id = item_type.split(":", 1)[1]
            self.scene_selected.emit(scene_id)
        elif item_type == "characters":
            self.characters_list_selected.emit()
        elif item_type == "statistics":
            self.statistics_selected.emit()
        elif isinstance(item_type, str) and item_type.startswith("character:"):
            character_id = item_type.split(":", 1)[1]
            self.character_selected.emit(character_id)
        # Dynamic containers
        elif item_type == ContainerType.LOCATIONS.value:
            self.locations_selected.emit()
        elif item_type == ContainerType.RESEARCH.value:
            self.research_selected.emit()
        elif item_type == ContainerType.TIMELINE.value:
            self.timeline_selected.emit()
        elif item_type == ContainerType.WORLDBUILDING.value:
            self.worldbuilding_selected.emit()
        elif item_type == ContainerType.SOURCES.value:
            self.sources_selected.emit()
        elif item_type == ContainerType.KEYWORDS.value:
            self.keywords_selected.emit()
        elif item_type == ContainerType.NOTES.value:
            self.notes_selected.emit()

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

        if item_type == "manuscript":
            # Context menu for Manuscript node
            add_chapter_action = QAction("Add New Chapter", self)
            add_chapter_action.triggered.connect(self.add_chapter_requested.emit)
            menu.addAction(add_chapter_action)

        elif isinstance(item_type, str) and item_type.startswith("chapter:"):
            # Context menu for Chapter
            chapter_id = item_type.split(":", 1)[1]

            add_scene_action = QAction("Add New Scene", self)
            add_scene_action.triggered.connect(
                lambda: self.add_scene_requested.emit(chapter_id)
            )
            menu.addAction(add_scene_action)

            menu.addSeparator()

            rename_action = QAction("Rename Chapter", self)
            rename_action.triggered.connect(
                lambda: self.rename_chapter_requested.emit(chapter_id)
            )
            menu.addAction(rename_action)

            delete_action = QAction("Delete Chapter", self)
            delete_action.triggered.connect(
                lambda: self.delete_chapter_requested.emit(chapter_id)
            )
            menu.addAction(delete_action)

        elif isinstance(item_type, str) and item_type.startswith("scene:"):
            # Context menu for Scene
            scene_id = item_type.split(":", 1)[1]

            rename_action = QAction("Rename Scene", self)
            rename_action.triggered.connect(
                lambda: self.rename_scene_requested.emit(scene_id)
            )
            menu.addAction(rename_action)

            delete_action = QAction("Delete Scene", self)
            delete_action.triggered.connect(
                lambda: self.delete_scene_requested.emit(scene_id)
            )
            menu.addAction(delete_action)

        elif item_type == "characters":
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

        # Dynamic container context menus
        elif item_type == ContainerType.LOCATIONS.value:
            add_action = QAction("Add New Location", self)
            add_action.triggered.connect(self.add_location_requested.emit)
            menu.addAction(add_action)

        elif item_type == ContainerType.RESEARCH.value:
            add_action = QAction("Add New Research Note", self)
            add_action.triggered.connect(self.add_research_note_requested.emit)
            menu.addAction(add_action)

        elif item_type == ContainerType.TIMELINE.value:
            add_action = QAction("Add New Timeline Event", self)
            add_action.triggered.connect(self.add_timeline_event_requested.emit)
            menu.addAction(add_action)

        elif item_type == ContainerType.WORLDBUILDING.value:
            add_action = QAction("Add New Worldbuilding Entry", self)
            add_action.triggered.connect(self.add_worldbuilding_entry_requested.emit)
            menu.addAction(add_action)

        elif item_type == ContainerType.SOURCES.value:
            add_action = QAction("Add New Source", self)
            add_action.triggered.connect(self.add_source_requested.emit)
            menu.addAction(add_action)

        elif item_type == ContainerType.KEYWORDS.value:
            add_action = QAction("Add New Keyword", self)
            add_action.triggered.connect(self.add_keyword_requested.emit)
            menu.addAction(add_action)

        elif item_type == ContainerType.NOTES.value:
            add_action = QAction("Add New Note", self)
            add_action.triggered.connect(self.add_note_requested.emit)
            menu.addAction(add_action)

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

    def select_scene(self, scene_id: str):
        """
        Programmatically select a scene

        Args:
            scene_id: Scene ID to select
        """
        root = self.topLevelItem(0)
        if not root:
            return

        # Find Manuscript node
        manuscript_node = None
        for i in range(root.childCount()):
            child = root.child(i)
            if child.data(0, Qt.ItemDataRole.UserRole) == "manuscript":
                manuscript_node = child
                break

        if not manuscript_node:
            return

        # Search through chapters and scenes
        for i in range(manuscript_node.childCount()):
            chapter_node = manuscript_node.child(i)
            for j in range(chapter_node.childCount()):
                scene_node = chapter_node.child(j)
                item_data = scene_node.data(0, Qt.ItemDataRole.UserRole)
                if item_data == f"scene:{scene_id}":
                    self.setCurrentItem(scene_node)
                    self.scene_selected.emit(scene_id)
                    return

    def update_manuscript_structure(self, manuscript_structure: ManuscriptStructure):
        """
        Update the manuscript structure in the tree (refresh chapters/scenes)

        Args:
            manuscript_structure: Updated manuscript structure
        """
        self._manuscript_structure = manuscript_structure

        # Find the root and manuscript nodes
        root = self.topLevelItem(0)
        if not root:
            return

        manuscript_node = None
        for i in range(root.childCount()):
            child = root.child(i)
            if child.data(0, Qt.ItemDataRole.UserRole) == "manuscript":
                manuscript_node = child
                break

        if not manuscript_node:
            return

        # Clear existing chapters/scenes
        manuscript_node.takeChildren()

        # Rebuild chapters and scenes
        for chapter in sorted(manuscript_structure.chapters, key=lambda c: c.order):
            chapter_item = QTreeWidgetItem(manuscript_node)
            chapter_item.setText(0, f"  📖 {chapter.title}")
            chapter_item.setExpanded(True)
            chapter_item.setData(0, Qt.ItemDataRole.UserRole, f"chapter:{chapter.id}")

            # Add scenes under chapter
            for scene in sorted(chapter.scenes, key=lambda s: s.order):
                scene_item = QTreeWidgetItem(chapter_item)
                scene_item.setText(0, f"    📝 {scene.title}")
                scene_item.setData(0, Qt.ItemDataRole.UserRole, f"scene:{scene.id}")

        manuscript_node.setExpanded(True)
