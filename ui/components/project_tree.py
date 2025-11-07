"""
Project Tree Widget - Sidebar navigation
"""
from PySide6.QtWidgets import QTreeWidget, QTreeWidgetItem, QMenu
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QAction
from typing import List, Optional
from models.character import Character
from models.manuscript_structure import ManuscriptStructure, Part, Chapter, Scene
from models.project import Project
from models.container_type import ContainerType
from datetime import datetime


class ProjectTree(QTreeWidget):
    """
    Tree widget for project navigation
    Shows: Project -> Manuscript, Characters -> individual characters
    """

    # Signals
    project_info_selected = Signal()  # DEPRECATED: Legacy signal

    # New Info Progetto sub-sections
    general_info_selected = Signal()
    ai_provider_config_selected = Signal()
    ai_writing_guide_selected = Signal()

    manuscript_selected = Signal()
    part_selected = Signal(str)  # part_id
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

    # Part operations
    add_part_requested = Signal()
    rename_part_requested = Signal(str)  # part_id
    delete_part_requested = Signal(str)  # part_id

    # Character operations
    add_character_requested = Signal()
    rename_character_requested = Signal(str)  # character_id
    delete_character_requested = Signal(str)  # character_id

    # Reordering operations
    chapters_reordered = Signal(list)  # list of chapter_ids in new order
    scenes_reordered = Signal(str, list)  # chapter_id, list of scene_ids in new order

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

        # Enable drag & drop for reordering
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDragDropMode(QTreeWidget.DragDropMode.InternalMove)
        self.setDefaultDropAction(Qt.DropAction.MoveAction)

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

        # Get UI labels in project language
        ui_labels = self._get_ui_labels(project.language)

        # Root node - Project title
        root = QTreeWidgetItem(self)
        root.setText(0, f"📁 {project.title}")
        root.setExpanded(True)
        root.setData(0, Qt.ItemDataRole.UserRole, "root")

        # Project Info node - Now expandable with sub-items
        info_item = QTreeWidgetItem(root)
        info_item.setText(0, f"📋 {ui_labels['project_info']}")
        info_item.setExpanded(True)
        info_item.setData(0, Qt.ItemDataRole.UserRole, "project_info_parent")

        # Sub-item 1: General Info
        general_info_item = QTreeWidgetItem(info_item)
        general_info_item.setText(0, f"  📝 {ui_labels['general_info']}")
        general_info_item.setData(0, Qt.ItemDataRole.UserRole, "project_info_general")

        # Sub-item 2: AI Provider Configuration
        ai_provider_item = QTreeWidgetItem(info_item)
        ai_provider_item.setText(0, f"  🤖 {ui_labels['ai_provider']}")
        ai_provider_item.setData(0, Qt.ItemDataRole.UserRole, "project_info_ai_provider")

        # Sub-item 3: AI Writing Guide
        ai_guide_item = QTreeWidgetItem(info_item)
        ai_guide_item.setText(0, f"  ✍️  {ui_labels['ai_writing_guide']}")
        ai_guide_item.setData(0, Qt.ItemDataRole.UserRole, "project_info_ai_guide")

        # Manuscript node with hierarchy
        manuscript_item = QTreeWidgetItem(root)
        manuscript_item.setText(0, f"📄 {ui_labels['manuscript']}")
        manuscript_item.setExpanded(True)
        manuscript_item.setData(0, Qt.ItemDataRole.UserRole, "manuscript")

        # Add chapters and scenes if structure exists
        if manuscript_structure:
            if manuscript_structure.use_parts_structure:
                # Modern 3-level structure: Parts → Chapters → Scenes
                for part in sorted(manuscript_structure.parts, key=lambda p: p.order):
                    part_item = QTreeWidgetItem(manuscript_item)
                    part_item.setText(0, f"  📚 {part.title}")
                    part_item.setExpanded(True)
                    part_item.setData(0, Qt.ItemDataRole.UserRole, f"part:{part.id}")

                    # Add chapters under part
                    for chapter in sorted(part.chapters, key=lambda c: c.order):
                        chapter_item = QTreeWidgetItem(part_item)
                        chapter_item.setText(0, f"    📖 {chapter.title}")
                        chapter_item.setExpanded(True)
                        chapter_item.setData(0, Qt.ItemDataRole.UserRole, f"chapter:{chapter.id}")

                        # Add scenes under chapter
                        for scene in sorted(chapter.scenes, key=lambda s: s.order):
                            scene_item = QTreeWidgetItem(chapter_item)
                            scene_item.setText(0, f"      📝 {scene.title}")
                            scene_item.setData(0, Qt.ItemDataRole.UserRole, f"scene:{scene.id}")
            else:
                # Legacy 2-level structure: Chapters → Scenes
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
        characters_item.setText(0, f"👤 {ui_labels['characters']}")
        characters_item.setExpanded(True)
        characters_item.setData(0, Qt.ItemDataRole.UserRole, "characters")

        # Add individual characters
        for character in characters:
            char_item = QTreeWidgetItem(characters_item)
            char_item.setText(0, f"  📷 {character.name}")
            char_item.setData(0, Qt.ItemDataRole.UserRole, f"character:{character.id}")

        # Statistics node
        statistics_item = QTreeWidgetItem(root)
        statistics_item.setText(0, f"📊 {ui_labels['statistics']}")
        statistics_item.setData(0, Qt.ItemDataRole.UserRole, "statistics")

        # Dynamic containers based on project type
        available_containers = ContainerType.get_available_for_project_type(project.project_type)

        for container_type in available_containers:
            # Skip manuscript and characters (already added above)
            if container_type in [ContainerType.MANUSCRIPT, ContainerType.CHARACTERS]:
                continue

            # Get display info for this container using project language
            icon, name = ContainerType.get_display_info(container_type, project.language)

            # Create tree item
            container_item = QTreeWidgetItem(root)
            container_item.setText(0, f"{icon} {name}")
            container_item.setData(0, Qt.ItemDataRole.UserRole, container_type.value)
            container_item.setExpanded(False)

    def _get_ui_labels(self, language: str) -> dict:
        """
        Get UI labels translated to the specified language

        Args:
            language: Language code (it, en, es, fr, de)

        Returns:
            dict: Dictionary of translated labels
        """
        labels = {
            'it': {
                'project_info': 'Info Progetto',
                'general_info': 'Info Generali',
                'ai_provider': 'Configurazione AI',
                'ai_writing_guide': 'Guida Scrittura AI',
                'manuscript': 'Manoscritto',
                'characters': 'Personaggi',
                'statistics': 'Statistiche'
            },
            'en': {
                'project_info': 'Project Info',
                'general_info': 'General Info',
                'ai_provider': 'AI Configuration',
                'ai_writing_guide': 'AI Writing Guide',
                'manuscript': 'Manuscript',
                'characters': 'Characters',
                'statistics': 'Statistics'
            },
            'es': {
                'project_info': 'Info del Proyecto',
                'general_info': 'Info General',
                'ai_provider': 'Configuración IA',
                'ai_writing_guide': 'Guía de Escritura IA',
                'manuscript': 'Manuscrito',
                'characters': 'Personajes',
                'statistics': 'Estadísticas'
            },
            'fr': {
                'project_info': 'Info Projet',
                'general_info': 'Info Générales',
                'ai_provider': 'Configuration IA',
                'ai_writing_guide': 'Guide d\'Écriture IA',
                'manuscript': 'Manuscrit',
                'characters': 'Personnages',
                'statistics': 'Statistiques'
            },
            'de': {
                'project_info': 'Projektinfo',
                'general_info': 'Allgemeine Info',
                'ai_provider': 'KI-Konfiguration',
                'ai_writing_guide': 'KI-Schreibanleitung',
                'manuscript': 'Manuskript',
                'characters': 'Charaktere',
                'statistics': 'Statistiken'
            }
        }
        return labels.get(language, labels['en'])

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

        # Handle new sub-sections of Info Progetto
        if item_type == "project_info_general":
            self.general_info_selected.emit()
        elif item_type == "project_info_ai_provider":
            self.ai_provider_config_selected.emit()
        elif item_type == "project_info_ai_guide":
            self.ai_writing_guide_selected.emit()
        # Legacy fallback (if clicked on parent node)
        elif item_type == "project_info" or item_type == "project_info_parent":
            # Default to General Info when clicking parent
            self.general_info_selected.emit()
        elif item_type == "manuscript":
            self.manuscript_selected.emit()
        elif isinstance(item_type, str) and item_type.startswith("part:"):
            part_id = item_type.split(":", 1)[1]
            self.part_selected.emit(part_id)
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
            if self._manuscript_structure and self._manuscript_structure.use_parts_structure:
                # 3-level structure: add Part
                add_part_action = QAction("Add New Part", self)
                add_part_action.triggered.connect(self.add_part_requested.emit)
                menu.addAction(add_part_action)
            else:
                # 2-level structure: add Chapter (legacy)
                add_chapter_action = QAction("Add New Chapter", self)
                add_chapter_action.triggered.connect(self.add_chapter_requested.emit)
                menu.addAction(add_chapter_action)

        elif isinstance(item_type, str) and item_type.startswith("part:"):
            # Context menu for Part
            part_id = item_type.split(":", 1)[1]

            add_chapter_action = QAction("Add New Chapter", self)
            add_chapter_action.triggered.connect(
                lambda: self.add_chapter_requested.emit()
            )
            menu.addAction(add_chapter_action)

            menu.addSeparator()

            rename_action = QAction("Rename Part", self)
            rename_action.triggered.connect(
                lambda: self.rename_part_requested.emit(part_id)
            )
            menu.addAction(rename_action)

            menu.addSeparator()

            delete_action = QAction("Delete Part", self)
            delete_action.triggered.connect(
                lambda: self.delete_part_requested.emit(part_id)
            )
            menu.addAction(delete_action)

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

            menu.addSeparator()

            # Submenu Sposta
            move_menu = QMenu("Sposta", self)

            move_up_action = QAction("⬆️ Sposta Su", self)
            move_up_action.triggered.connect(lambda: self._move_chapter(chapter_id, "up"))
            move_menu.addAction(move_up_action)

            move_down_action = QAction("⬇️ Sposta Giù", self)
            move_down_action.triggered.connect(lambda: self._move_chapter(chapter_id, "down"))
            move_menu.addAction(move_down_action)

            move_menu.addSeparator()

            move_top_action = QAction("⏫ Sposta all'Inizio", self)
            move_top_action.triggered.connect(lambda: self._move_chapter(chapter_id, "top"))
            move_menu.addAction(move_top_action)

            move_bottom_action = QAction("⏬ Sposta alla Fine", self)
            move_bottom_action.triggered.connect(lambda: self._move_chapter(chapter_id, "bottom"))
            move_menu.addAction(move_bottom_action)

            menu.addMenu(move_menu)

            menu.addSeparator()

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

            menu.addSeparator()

            # Submenu Sposta
            move_menu = QMenu("Sposta", self)

            move_up_action = QAction("⬆️ Sposta Su", self)
            move_up_action.triggered.connect(lambda: self._move_scene(scene_id, "up"))
            move_menu.addAction(move_up_action)

            move_down_action = QAction("⬇️ Sposta Giù", self)
            move_down_action.triggered.connect(lambda: self._move_scene(scene_id, "down"))
            move_menu.addAction(move_down_action)

            move_menu.addSeparator()

            move_top_action = QAction("⏫ Sposta all'Inizio", self)
            move_top_action.triggered.connect(lambda: self._move_scene(scene_id, "top"))
            move_menu.addAction(move_top_action)

            move_bottom_action = QAction("⏬ Sposta alla Fine", self)
            move_bottom_action.triggered.connect(lambda: self._move_scene(scene_id, "bottom"))
            move_menu.addAction(move_bottom_action)

            menu.addMenu(move_menu)

            menu.addSeparator()

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

            rename_action = QAction("Rename Character", self)
            rename_action.triggered.connect(
                lambda: self.rename_character_requested.emit(character_id)
            )
            menu.addAction(rename_action)

            menu.addSeparator()

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

    def dropEvent(self, event):
        """Handle drop event for reordering chapters and scenes"""
        # Get dragged item and target
        dragged_item = self.currentItem()
        if not dragged_item:
            event.ignore()
            return

        drop_indicator = self.dropIndicatorPosition()
        target_item = self.itemAt(event.position().toPoint())

        if not target_item:
            event.ignore()
            return

        # Get item types
        dragged_type = dragged_item.data(0, Qt.ItemDataRole.UserRole)
        target_type = target_item.data(0, Qt.ItemDataRole.UserRole)

        if not dragged_type or not target_type:
            event.ignore()
            return

        # CASE 1: Moving a chapter
        if isinstance(dragged_type, str) and dragged_type.startswith("chapter:") and \
           isinstance(target_type, str) and target_type.startswith("chapter:"):
            # Calculate new chapter order
            new_order = self._calculate_chapters_order(dragged_item, target_item, drop_indicator)
            if new_order:
                self.chapters_reordered.emit(new_order)
                event.accept()
                return

        # CASE 2: Moving a scene (only within same chapter)
        if isinstance(dragged_type, str) and dragged_type.startswith("scene:") and \
           isinstance(target_type, str) and target_type.startswith("scene:"):
            # Check if they belong to the same chapter
            dragged_parent = dragged_item.parent()
            target_parent = target_item.parent()

            if dragged_parent == target_parent:
                chapter_id = dragged_parent.data(0, Qt.ItemDataRole.UserRole).split(":")[1]
                new_order = self._calculate_scenes_order(dragged_item, target_item, drop_indicator, dragged_parent)
                if new_order:
                    self.scenes_reordered.emit(chapter_id, new_order)
                    event.accept()
                    return

        # If we get here, the drop is not allowed
        event.ignore()

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

        # Rebuild structure based on mode
        if manuscript_structure.use_parts_structure:
            # 3-level: Parts → Chapters → Scenes
            for part in sorted(manuscript_structure.parts, key=lambda p: p.order):
                part_item = QTreeWidgetItem(manuscript_node)
                part_item.setText(0, f"  📚 {part.title}")
                part_item.setExpanded(True)
                part_item.setData(0, Qt.ItemDataRole.UserRole, f"part:{part.id}")

                # Add chapters under part
                for chapter in sorted(part.chapters, key=lambda c: c.order):
                    chapter_item = QTreeWidgetItem(part_item)
                    chapter_item.setText(0, f"    📖 {chapter.title}")
                    chapter_item.setExpanded(True)
                    chapter_item.setData(0, Qt.ItemDataRole.UserRole, f"chapter:{chapter.id}")

                    # Add scenes under chapter
                    for scene in sorted(chapter.scenes, key=lambda s: s.order):
                        scene_item = QTreeWidgetItem(chapter_item)
                        scene_item.setText(0, f"      📝 {scene.title}")
                        scene_item.setData(0, Qt.ItemDataRole.UserRole, f"scene:{scene.id}")
        else:
            # 2-level: Chapters → Scenes (legacy)
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

    def _calculate_chapters_order(self, dragged_item, target_item, drop_indicator):
        """Calculate new chapter order after drop"""
        manuscript_node = dragged_item.parent()
        if not manuscript_node:
            return None

        chapter_ids = []

        for i in range(manuscript_node.childCount()):
            chapter_item = manuscript_node.child(i)
            if chapter_item == dragged_item:
                continue

            chapter_type = chapter_item.data(0, Qt.ItemDataRole.UserRole)
            if not chapter_type or not isinstance(chapter_type, str):
                continue

            chapter_id = chapter_type.split(":")[1]

            # Insert dragged_item at the correct position
            if chapter_item == target_item:
                if drop_indicator == QTreeWidget.DropIndicatorPosition.AboveItem:
                    dragged_id = dragged_item.data(0, Qt.ItemDataRole.UserRole).split(":")[1]
                    chapter_ids.append(dragged_id)
                    chapter_ids.append(chapter_id)
                else:
                    chapter_ids.append(chapter_id)
                    dragged_id = dragged_item.data(0, Qt.ItemDataRole.UserRole).split(":")[1]
                    chapter_ids.append(dragged_id)
            else:
                chapter_ids.append(chapter_id)

        return chapter_ids if chapter_ids else None

    def _calculate_scenes_order(self, dragged_item, target_item, drop_indicator, chapter_node):
        """Calculate new scene order after drop"""
        if not chapter_node:
            return None

        scene_ids = []

        for i in range(chapter_node.childCount()):
            scene_item = chapter_node.child(i)
            if scene_item == dragged_item:
                continue

            scene_type = scene_item.data(0, Qt.ItemDataRole.UserRole)
            if not scene_type or not isinstance(scene_type, str):
                continue

            scene_id = scene_type.split(":")[1]

            # Insert dragged_item at the correct position
            if scene_item == target_item:
                if drop_indicator == QTreeWidget.DropIndicatorPosition.AboveItem:
                    dragged_id = dragged_item.data(0, Qt.ItemDataRole.UserRole).split(":")[1]
                    scene_ids.append(dragged_id)
                    scene_ids.append(scene_id)
                else:
                    scene_ids.append(scene_id)
                    dragged_id = dragged_item.data(0, Qt.ItemDataRole.UserRole).split(":")[1]
                    scene_ids.append(dragged_id)
            else:
                scene_ids.append(scene_id)

        return scene_ids if scene_ids else None

    def _move_chapter(self, chapter_id: str, direction: str):
        """Move chapter in a specific direction"""
        if not self._manuscript_structure:
            return

        # Find current index
        current_index = -1
        for i, chapter in enumerate(self._manuscript_structure.chapters):
            if chapter.id == chapter_id:
                current_index = i
                break

        if current_index == -1:
            return

        # Calculate new index
        total = len(self._manuscript_structure.chapters)
        new_index = current_index

        if direction == "up" and current_index > 0:
            new_index = current_index - 1
        elif direction == "down" and current_index < total - 1:
            new_index = current_index + 1
        elif direction == "top":
            new_index = 0
        elif direction == "bottom":
            new_index = total - 1

        if new_index == current_index:
            return

        # Create new order
        chapters = self._manuscript_structure.chapters.copy()
        chapters.insert(new_index, chapters.pop(current_index))
        new_order = [ch.id for ch in chapters]

        self.chapters_reordered.emit(new_order)

    def _move_scene(self, scene_id: str, direction: str):
        """Move scene in a specific direction (within same chapter)"""
        if not self._manuscript_structure:
            return

        # Find chapter and scene
        chapter = self._manuscript_structure.get_chapter_for_scene(scene_id)
        if not chapter:
            return

        current_index = -1
        for i, scene in enumerate(chapter.scenes):
            if scene.id == scene_id:
                current_index = i
                break

        if current_index == -1:
            return

        # Calculate new index
        total = len(chapter.scenes)
        new_index = current_index

        if direction == "up" and current_index > 0:
            new_index = current_index - 1
        elif direction == "down" and current_index < total - 1:
            new_index = current_index + 1
        elif direction == "top":
            new_index = 0
        elif direction == "bottom":
            new_index = total - 1

        if new_index == current_index:
            return

        # Create new order
        scenes = chapter.scenes.copy()
        scenes.insert(new_index, scenes.pop(current_index))
        new_order = [sc.id for sc in scenes]

        self.scenes_reordered.emit(chapter.id, new_order)
