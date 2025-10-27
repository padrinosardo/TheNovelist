"""
Manuscript Structure Manager - Manages the hierarchical structure of the manuscript
"""
from typing import Optional, List, Tuple
from models.manuscript_structure import ManuscriptStructure, Chapter, Scene
from utils.logger import AppLogger


class ManuscriptStructureManager:
    """
    Manages manuscript structure with chapters and scenes

    Provides CRUD operations for chapters and scenes, maintaining order and consistency
    """

    def __init__(self, structure: ManuscriptStructure = None):
        """
        Initialize the manager

        Args:
            structure: Existing structure or None to create default
        """
        self.structure = structure if structure else ManuscriptStructure.create_default()

    def get_structure(self) -> ManuscriptStructure:
        """Get the manuscript structure"""
        return self.structure

    def set_structure(self, structure: ManuscriptStructure):
        """Set a new manuscript structure"""
        self.structure = structure

    # ==================== Chapter Operations ====================

    def add_chapter(self, title: str, order: int = None) -> Chapter:
        """
        Add a new chapter to the manuscript

        Args:
            title: Chapter title
            order: Chapter order (None = append at end)

        Returns:
            Chapter: The created chapter
        """
        if order is None:
            order = len(self.structure.chapters)

        chapter = Chapter.create_new(title, order)

        # Create default first scene
        scene = Scene.create_new("Scene 1", order=0)
        chapter.add_scene(scene)

        self.structure.add_chapter(chapter)

        # Reorder if needed
        if order < len(self.structure.chapters) - 1:
            self._reorder_chapters()

        AppLogger.debug(f"Added chapter: {title} (ID: {chapter.id})")
        return chapter

    def rename_chapter(self, chapter_id: str, new_title: str) -> bool:
        """
        Rename a chapter

        Args:
            chapter_id: Chapter ID
            new_title: New title

        Returns:
            bool: True if successful
        """
        chapter = self.structure.get_chapter(chapter_id)
        if chapter:
            old_title = chapter.title
            chapter.title = new_title
            AppLogger.debug(f"Renamed chapter: {old_title} -> {new_title}")
            return True

        AppLogger.warning(f"Chapter not found for rename: {chapter_id}")
        return False

    def delete_chapter(self, chapter_id: str) -> bool:
        """
        Delete a chapter and all its scenes

        Args:
            chapter_id: Chapter ID

        Returns:
            bool: True if successful
        """
        chapter = self.structure.get_chapter(chapter_id)
        if not chapter:
            AppLogger.warning(f"Chapter not found for delete: {chapter_id}")
            return False

        # If this was the current scene's chapter, clear current scene
        if self.structure.current_scene_id:
            for scene in chapter.scenes:
                if scene.id == self.structure.current_scene_id:
                    self.structure.current_scene_id = None
                    break

        success = self.structure.remove_chapter(chapter_id)
        if success:
            self._reorder_chapters()
            AppLogger.info(f"Deleted chapter: {chapter.title} ({len(chapter.scenes)} scenes)")

        return success

    def reorder_chapters(self, chapter_ids_order: List[str]) -> bool:
        """
        Reorder chapters based on list of IDs

        Args:
            chapter_ids_order: List of chapter IDs in desired order

        Returns:
            bool: True if successful
        """
        if len(chapter_ids_order) != len(self.structure.chapters):
            AppLogger.error("Chapter reorder failed: ID count mismatch")
            return False

        # Create new ordered list
        new_chapters = []
        for chapter_id in chapter_ids_order:
            chapter = self.structure.get_chapter(chapter_id)
            if not chapter:
                AppLogger.error(f"Chapter reorder failed: Invalid ID {chapter_id}")
                return False
            new_chapters.append(chapter)

        # Update structure
        self.structure.chapters = new_chapters
        self._reorder_chapters()

        AppLogger.debug("Chapters reordered successfully")
        return True

    def _reorder_chapters(self):
        """Internal: Fix chapter order numbers"""
        for i, chapter in enumerate(self.structure.chapters):
            chapter.order = i

    def get_all_chapters(self) -> List[Chapter]:
        """Get all chapters in order"""
        return sorted(self.structure.chapters, key=lambda c: c.order)

    def get_chapter(self, chapter_id: str) -> Optional[Chapter]:
        """Get a chapter by ID"""
        return self.structure.get_chapter(chapter_id)

    # ==================== Scene Operations ====================

    def add_scene(self, chapter_id: str, title: str, order: int = None) -> Optional[Scene]:
        """
        Add a new scene to a chapter

        Args:
            chapter_id: Chapter ID
            title: Scene title
            order: Scene order within chapter (None = append at end)

        Returns:
            Optional[Scene]: The created scene or None if chapter not found
        """
        chapter = self.structure.get_chapter(chapter_id)
        if not chapter:
            AppLogger.warning(f"Chapter not found for add scene: {chapter_id}")
            return None

        if order is None:
            order = len(chapter.scenes)

        scene = Scene.create_new(title, order)
        chapter.add_scene(scene)

        # Reorder if needed
        if order < len(chapter.scenes) - 1:
            self._reorder_scenes(chapter_id)

        AppLogger.debug(f"Added scene: {title} to chapter {chapter.title}")
        return scene

    def rename_scene(self, scene_id: str, new_title: str) -> bool:
        """
        Rename a scene

        Args:
            scene_id: Scene ID
            new_title: New title

        Returns:
            bool: True if successful
        """
        scene = self.structure.get_scene(scene_id)
        if scene:
            old_title = scene.title
            scene.title = new_title
            AppLogger.debug(f"Renamed scene: {old_title} -> {new_title}")
            return True

        AppLogger.warning(f"Scene not found for rename: {scene_id}")
        return False

    def delete_scene(self, scene_id: str) -> bool:
        """
        Delete a scene

        Args:
            scene_id: Scene ID

        Returns:
            bool: True if successful
        """
        # Find the chapter containing this scene
        chapter = self.structure.get_chapter_for_scene(scene_id)
        if not chapter:
            AppLogger.warning(f"Scene not found for delete: {scene_id}")
            return False

        # Don't allow deleting the last scene in a chapter
        if len(chapter.scenes) <= 1:
            AppLogger.warning(f"Cannot delete last scene in chapter: {chapter.title}")
            return False

        # Clear current scene if it's being deleted
        if self.structure.current_scene_id == scene_id:
            self.structure.current_scene_id = None

        scene = self.structure.get_scene(scene_id)
        success = chapter.remove_scene(scene_id)

        if success:
            self._reorder_scenes(chapter.id)
            AppLogger.info(f"Deleted scene: {scene.title}")

        return success

    def reorder_scenes(self, chapter_id: str, scene_ids_order: List[str]) -> bool:
        """
        Reorder scenes within a chapter

        Args:
            chapter_id: Chapter ID
            scene_ids_order: List of scene IDs in desired order

        Returns:
            bool: True if successful
        """
        chapter = self.structure.get_chapter(chapter_id)
        if not chapter:
            AppLogger.error(f"Chapter not found for reorder: {chapter_id}")
            return False

        if len(scene_ids_order) != len(chapter.scenes):
            AppLogger.error("Scene reorder failed: ID count mismatch")
            return False

        # Create new ordered list
        new_scenes = []
        for scene_id in scene_ids_order:
            scene = chapter.get_scene(scene_id)
            if not scene:
                AppLogger.error(f"Scene reorder failed: Invalid ID {scene_id}")
                return False
            new_scenes.append(scene)

        # Update chapter
        chapter.scenes = new_scenes
        self._reorder_scenes(chapter_id)

        AppLogger.debug(f"Scenes reordered in chapter: {chapter.title}")
        return True

    def _reorder_scenes(self, chapter_id: str):
        """Internal: Fix scene order numbers in a chapter"""
        chapter = self.structure.get_chapter(chapter_id)
        if chapter:
            for i, scene in enumerate(chapter.scenes):
                scene.order = i

    def get_scenes_in_chapter(self, chapter_id: str) -> List[Scene]:
        """
        Get all scenes in a chapter

        Args:
            chapter_id: Chapter ID

        Returns:
            List[Scene]: Scenes in order
        """
        chapter = self.structure.get_chapter(chapter_id)
        if chapter:
            return sorted(chapter.scenes, key=lambda s: s.order)
        return []

    def get_scene(self, scene_id: str) -> Optional[Scene]:
        """Get a scene by ID"""
        return self.structure.get_scene(scene_id)

    def update_scene_content(self, scene_id: str, content: str) -> bool:
        """
        Update the content of a scene

        Args:
            scene_id: Scene ID
            content: New content

        Returns:
            bool: True if successful
        """
        scene = self.structure.get_scene(scene_id)
        if scene:
            scene.update_content(content)
            AppLogger.debug(f"Updated scene content: {scene.title} ({scene.word_count} words)")
            return True

        AppLogger.warning(f"Scene not found for content update: {scene_id}")
        return False

    # ==================== Navigation Operations ====================

    def get_next_scene(self, current_scene_id: str) -> Optional[Scene]:
        """
        Get the next scene in the manuscript

        Args:
            current_scene_id: Current scene ID

        Returns:
            Optional[Scene]: Next scene or None if at end
        """
        all_scenes = self.structure.get_all_scenes()

        for i, scene in enumerate(all_scenes):
            if scene.id == current_scene_id:
                if i < len(all_scenes) - 1:
                    return all_scenes[i + 1]
                break

        return None

    def get_previous_scene(self, current_scene_id: str) -> Optional[Scene]:
        """
        Get the previous scene in the manuscript

        Args:
            current_scene_id: Current scene ID

        Returns:
            Optional[Scene]: Previous scene or None if at beginning
        """
        all_scenes = self.structure.get_all_scenes()

        for i, scene in enumerate(all_scenes):
            if scene.id == current_scene_id:
                if i > 0:
                    return all_scenes[i - 1]
                break

        return None

    def get_first_scene_in_chapter(self, chapter_id: str) -> Optional[Scene]:
        """
        Get the first scene in a chapter

        Args:
            chapter_id: Chapter ID

        Returns:
            Optional[Scene]: First scene or None
        """
        scenes = self.get_scenes_in_chapter(chapter_id)
        return scenes[0] if scenes else None

    def set_current_scene(self, scene_id: str):
        """
        Set the current scene being edited

        Args:
            scene_id: Scene ID
        """
        if self.structure.get_scene(scene_id):
            self.structure.current_scene_id = scene_id
            AppLogger.debug(f"Current scene set to: {scene_id}")

    def get_current_scene(self) -> Optional[Scene]:
        """Get the current scene being edited"""
        if self.structure.current_scene_id:
            return self.structure.get_scene(self.structure.current_scene_id)
        return None

    # ==================== Statistics ====================

    def get_total_word_count(self) -> int:
        """Get total word count for entire manuscript"""
        return self.structure.get_total_word_count()

    def get_chapter_word_count(self, chapter_id: str) -> int:
        """
        Get word count for a chapter

        Args:
            chapter_id: Chapter ID

        Returns:
            int: Word count
        """
        chapter = self.structure.get_chapter(chapter_id)
        return chapter.get_total_word_count() if chapter else 0

    def get_scene_word_count(self, scene_id: str) -> int:
        """
        Get word count for a scene

        Args:
            scene_id: Scene ID

        Returns:
            int: Word count
        """
        scene = self.structure.get_scene(scene_id)
        return scene.word_count if scene else 0

    # ==================== Serialization ====================

    def to_dict(self) -> dict:
        """Convert structure to dictionary for saving"""
        return self.structure.to_dict()

    def from_dict(self, data: dict):
        """Load structure from dictionary"""
        self.structure = ManuscriptStructure.from_dict(data)

    # ==================== Utility ====================

    def get_full_manuscript_text(self) -> str:
        """
        Get the complete manuscript as a single text string

        Returns:
            str: Complete manuscript text
        """
        return self.structure.get_full_text()
