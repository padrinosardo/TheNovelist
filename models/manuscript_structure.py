"""
Manuscript Structure Models - Hierarchical organization of manuscript content
"""
from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime
import uuid


@dataclass
class Scene:
    """
    Represents a single scene in the manuscript

    A scene is the smallest unit of content, containing the actual text
    """
    id: str
    title: str
    content: str
    order: int
    word_count: int = 0
    created_date: str = ""
    modified_date: str = ""

    @staticmethod
    def create_new(title: str, order: int, content: str = "") -> 'Scene':
        """
        Create a new scene with generated ID and timestamps

        Args:
            title: Scene title
            order: Order within chapter
            content: Initial content (optional)

        Returns:
            Scene: New scene instance
        """
        now = datetime.now().isoformat()
        word_count = len(content.split()) if content else 0

        return Scene(
            id=str(uuid.uuid4()),
            title=title,
            content=content,
            order=order,
            word_count=word_count,
            created_date=now,
            modified_date=now
        )

    def update_content(self, content: str):
        """
        Update scene content and recalculate word count

        Args:
            content: New content
        """
        self.content = content
        self.word_count = len(content.split()) if content else 0
        self.modified_date = datetime.now().isoformat()

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization"""
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'order': self.order,
            'word_count': self.word_count,
            'created_date': self.created_date,
            'modified_date': self.modified_date
        }

    @staticmethod
    def from_dict(data: dict) -> 'Scene':
        """Create Scene from dictionary"""
        return Scene(
            id=data.get('id', str(uuid.uuid4())),
            title=data.get('title', 'Untitled Scene'),
            content=data.get('content', ''),
            order=data.get('order', 0),
            word_count=data.get('word_count', 0),
            created_date=data.get('created_date', datetime.now().isoformat()),
            modified_date=data.get('modified_date', datetime.now().isoformat())
        )


@dataclass
class Chapter:
    """
    Represents a chapter containing multiple scenes

    A chapter organizes scenes into logical groups
    """
    id: str
    title: str
    scenes: List[Scene] = field(default_factory=list)
    order: int = 0

    @staticmethod
    def create_new(title: str, order: int) -> 'Chapter':
        """
        Create a new chapter with generated ID

        Args:
            title: Chapter title
            order: Order within manuscript

        Returns:
            Chapter: New chapter instance
        """
        return Chapter(
            id=str(uuid.uuid4()),
            title=title,
            scenes=[],
            order=order
        )

    def add_scene(self, scene: Scene):
        """Add a scene to this chapter"""
        self.scenes.append(scene)

    def remove_scene(self, scene_id: str) -> bool:
        """
        Remove a scene from this chapter

        Args:
            scene_id: ID of scene to remove

        Returns:
            bool: True if scene was found and removed
        """
        for i, scene in enumerate(self.scenes):
            if scene.id == scene_id:
                self.scenes.pop(i)
                return True
        return False

    def get_scene(self, scene_id: str) -> Optional[Scene]:
        """
        Get a scene by ID

        Args:
            scene_id: Scene ID

        Returns:
            Optional[Scene]: Scene if found, None otherwise
        """
        for scene in self.scenes:
            if scene.id == scene_id:
                return scene
        return None

    def get_total_word_count(self) -> int:
        """Calculate total word count for all scenes in chapter"""
        return sum(scene.word_count for scene in self.scenes)

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization"""
        return {
            'id': self.id,
            'title': self.title,
            'order': self.order,
            'scenes': [scene.to_dict() for scene in self.scenes]
        }

    @staticmethod
    def from_dict(data: dict) -> 'Chapter':
        """Create Chapter from dictionary"""
        chapter = Chapter(
            id=data.get('id', str(uuid.uuid4())),
            title=data.get('title', 'Untitled Chapter'),
            order=data.get('order', 0),
            scenes=[]
        )

        # Load scenes
        for scene_data in data.get('scenes', []):
            scene = Scene.from_dict(scene_data)
            chapter.scenes.append(scene)

        return chapter


@dataclass
class ManuscriptStructure:
    """
    Root structure containing all chapters and scenes

    This represents the complete hierarchical organization of the manuscript
    """
    chapters: List[Chapter] = field(default_factory=list)
    current_scene_id: Optional[str] = None  # Last opened scene

    def add_chapter(self, chapter: Chapter):
        """Add a chapter to the manuscript"""
        self.chapters.append(chapter)

    def remove_chapter(self, chapter_id: str) -> bool:
        """
        Remove a chapter from the manuscript

        Args:
            chapter_id: ID of chapter to remove

        Returns:
            bool: True if chapter was found and removed
        """
        for i, chapter in enumerate(self.chapters):
            if chapter.id == chapter_id:
                self.chapters.pop(i)
                return True
        return False

    def get_chapter(self, chapter_id: str) -> Optional[Chapter]:
        """
        Get a chapter by ID

        Args:
            chapter_id: Chapter ID

        Returns:
            Optional[Chapter]: Chapter if found, None otherwise
        """
        for chapter in self.chapters:
            if chapter.id == chapter_id:
                return chapter
        return None

    def get_scene(self, scene_id: str) -> Optional[Scene]:
        """
        Get a scene by ID (searches all chapters)

        Args:
            scene_id: Scene ID

        Returns:
            Optional[Scene]: Scene if found, None otherwise
        """
        for chapter in self.chapters:
            scene = chapter.get_scene(scene_id)
            if scene:
                return scene
        return None

    def get_chapter_for_scene(self, scene_id: str) -> Optional[Chapter]:
        """
        Get the chapter that contains a specific scene

        Args:
            scene_id: Scene ID

        Returns:
            Optional[Chapter]: Chapter containing the scene, or None
        """
        for chapter in self.chapters:
            if chapter.get_scene(scene_id):
                return chapter
        return None

    def get_all_scenes(self) -> List[Scene]:
        """
        Get all scenes from all chapters in order

        Returns:
            List[Scene]: All scenes
        """
        all_scenes = []
        for chapter in sorted(self.chapters, key=lambda c: c.order):
            for scene in sorted(chapter.scenes, key=lambda s: s.order):
                all_scenes.append(scene)
        return all_scenes

    def get_total_word_count(self) -> int:
        """Calculate total word count for entire manuscript"""
        return sum(chapter.get_total_word_count() for chapter in self.chapters)

    def get_full_text(self) -> str:
        """
        Get the complete manuscript text (all scenes concatenated)

        Returns:
            str: Complete manuscript text
        """
        text_parts = []

        for chapter in sorted(self.chapters, key=lambda c: c.order):
            # Add chapter title
            text_parts.append(f"\n\n# {chapter.title}\n\n")

            # Add all scenes in chapter
            for scene in sorted(chapter.scenes, key=lambda s: s.order):
                if scene.content:
                    text_parts.append(scene.content)
                    text_parts.append("\n\n")

        return ''.join(text_parts).strip()

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization"""
        return {
            'chapters': [chapter.to_dict() for chapter in self.chapters],
            'current_scene_id': self.current_scene_id
        }

    @staticmethod
    def from_dict(data: dict) -> 'ManuscriptStructure':
        """Create ManuscriptStructure from dictionary"""
        structure = ManuscriptStructure(
            chapters=[],
            current_scene_id=data.get('current_scene_id')
        )

        # Load chapters
        for chapter_data in data.get('chapters', []):
            chapter = Chapter.from_dict(chapter_data)
            structure.chapters.append(chapter)

        return structure

    @staticmethod
    def create_default() -> 'ManuscriptStructure':
        """
        Create a default manuscript structure with Chapter 1 / Scene 1

        Returns:
            ManuscriptStructure: Default structure
        """
        structure = ManuscriptStructure()

        # Create Chapter 1
        chapter = Chapter.create_new("Chapter 1", order=0)

        # Create Scene 1
        scene = Scene.create_new("Scene 1", order=0, content="")
        chapter.add_scene(scene)

        structure.add_chapter(chapter)
        structure.current_scene_id = scene.id

        return structure
