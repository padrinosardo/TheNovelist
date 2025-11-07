"""
Manuscript Structure Models - Hierarchical organization of manuscript content
"""
from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime
import uuid
import re


def _strip_html_tags(text: str) -> str:
    """
    Remove HTML tags from text for word counting

    Args:
        text: Text potentially containing HTML tags

    Returns:
        str: Plain text without HTML tags
    """
    if not text:
        return ""

    # Remove HTML tags using regex
    clean = re.sub(r'<[^>]+>', '', text)
    # Remove extra whitespace
    clean = re.sub(r'\s+', ' ', clean)
    return clean.strip()


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
    synopsis: str = ""  # Scene synopsis/summary
    notes: str = ""  # Scene notes

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
        # Calculate word count from plain text (strip HTML tags)
        plain_text = _strip_html_tags(content)
        word_count = len(plain_text.split()) if plain_text else 0

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
            content: New content (may contain HTML formatting)
        """
        self.content = content
        # Calculate word count from plain text (strip HTML tags)
        plain_text = _strip_html_tags(content)
        self.word_count = len(plain_text.split()) if plain_text else 0
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
            'modified_date': self.modified_date,
            'synopsis': self.synopsis,
            'notes': self.notes
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
            modified_date=data.get('modified_date', datetime.now().isoformat()),
            synopsis=data.get('synopsis', ''),
            notes=data.get('notes', '')
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
    synopsis: str = ""  # Chapter synopsis/summary
    notes: str = ""  # Chapter notes

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
            'scenes': [scene.to_dict() for scene in self.scenes],
            'synopsis': self.synopsis,
            'notes': self.notes
        }

    @staticmethod
    def from_dict(data: dict) -> 'Chapter':
        """Create Chapter from dictionary"""
        chapter = Chapter(
            id=data.get('id', str(uuid.uuid4())),
            title=data.get('title', 'Untitled Chapter'),
            order=data.get('order', 0),
            scenes=[],
            synopsis=data.get('synopsis', ''),
            notes=data.get('notes', '')
        )

        # Load scenes
        for scene_data in data.get('scenes', []):
            scene = Scene.from_dict(scene_data)
            chapter.scenes.append(scene)

        return chapter


@dataclass
class Part:
    """
    Represents a part (section) of the manuscript containing multiple chapters

    A part is a higher-level organizational unit above chapters,
    commonly used in novels (e.g., "Part I", "Part II", etc.)
    """
    id: str
    title: str
    chapters: List[Chapter] = field(default_factory=list)
    order: int = 0
    synopsis: str = ""  # Part synopsis/summary
    notes: str = ""  # Part notes

    @staticmethod
    def create_new(title: str, order: int) -> 'Part':
        """
        Create a new part with generated ID

        Args:
            title: Part title
            order: Order within manuscript

        Returns:
            Part: New part instance
        """
        return Part(
            id=str(uuid.uuid4()),
            title=title,
            chapters=[],
            order=order
        )

    def add_chapter(self, chapter: Chapter):
        """Add a chapter to this part"""
        self.chapters.append(chapter)

    def remove_chapter(self, chapter_id: str) -> bool:
        """
        Remove a chapter from this part

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

    def get_total_word_count(self) -> int:
        """Calculate total word count for all chapters in part"""
        return sum(chapter.get_total_word_count() for chapter in self.chapters)

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization"""
        return {
            'id': self.id,
            'title': self.title,
            'order': self.order,
            'chapters': [chapter.to_dict() for chapter in self.chapters],
            'synopsis': self.synopsis,
            'notes': self.notes
        }

    @staticmethod
    def from_dict(data: dict) -> 'Part':
        """Create Part from dictionary"""
        part = Part(
            id=data.get('id', str(uuid.uuid4())),
            title=data.get('title', 'Untitled Part'),
            order=data.get('order', 0),
            chapters=[],
            synopsis=data.get('synopsis', ''),
            notes=data.get('notes', '')
        )

        # Load chapters
        for chapter_data in data.get('chapters', []):
            chapter = Chapter.from_dict(chapter_data)
            part.chapters.append(chapter)

        return part


@dataclass
class ManuscriptStructure:
    """
    Root structure containing all parts, chapters and scenes

    This represents the complete hierarchical organization of the manuscript

    Supports two structures:
    1. Legacy (2-level): chapters directly in structure
    2. Modern (3-level): parts containing chapters containing scenes
    """
    parts: List[Part] = field(default_factory=list)
    chapters: List[Chapter] = field(default_factory=list)  # Legacy: direct chapters
    current_scene_id: Optional[str] = None
    use_parts_structure: bool = False  # Toggle between 2-level and 3-level

    def add_part(self, part: Part):
        """Add a part to the manuscript"""
        self.parts.append(part)

    def remove_part(self, part_id: str) -> bool:
        """
        Remove a part from the manuscript

        Args:
            part_id: ID of part to remove

        Returns:
            bool: True if part was found and removed
        """
        for i, part in enumerate(self.parts):
            if part.id == part_id:
                self.parts.pop(i)
                return True
        return False

    def get_part(self, part_id: str) -> Optional[Part]:
        """
        Get a part by ID

        Args:
            part_id: Part ID

        Returns:
            Optional[Part]: Part if found, None otherwise
        """
        for part in self.parts:
            if part.id == part_id:
                return part
        return None

    def get_part_for_chapter(self, chapter_id: str) -> Optional[Part]:
        """
        Get the part that contains a specific chapter

        Args:
            chapter_id: Chapter ID

        Returns:
            Optional[Part]: Part containing the chapter, or None
        """
        for part in self.parts:
            if part.get_chapter(chapter_id):
                return part
        return None

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
        Get a chapter by ID (searches all parts or direct chapters)

        Args:
            chapter_id: Chapter ID

        Returns:
            Optional[Chapter]: Chapter if found, None otherwise
        """
        if self.use_parts_structure:
            # Search in parts
            for part in self.parts:
                chapter = part.get_chapter(chapter_id)
                if chapter:
                    return chapter
        else:
            # Search in direct chapters (legacy)
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
        if self.use_parts_structure:
            # Search in parts
            for part in self.parts:
                for chapter in part.chapters:
                    scene = chapter.get_scene(scene_id)
                    if scene:
                        return scene
        else:
            # Search in direct chapters (legacy)
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
        if self.use_parts_structure:
            # Search in parts
            for part in self.parts:
                for chapter in part.chapters:
                    if chapter.get_scene(scene_id):
                        return chapter
        else:
            # Search in direct chapters (legacy)
            for chapter in self.chapters:
                if chapter.get_scene(scene_id):
                    return chapter
        return None

    def get_all_chapters(self) -> List[Chapter]:
        """
        Get all chapters in order (from parts or direct)

        Returns:
            List[Chapter]: All chapters sorted by order
        """
        if self.use_parts_structure:
            all_chapters = []
            for part in sorted(self.parts, key=lambda p: p.order):
                for chapter in sorted(part.chapters, key=lambda c: c.order):
                    all_chapters.append(chapter)
            return all_chapters
        else:
            return sorted(self.chapters, key=lambda c: c.order)

    def get_all_scenes(self) -> List[Scene]:
        """
        Get all scenes from all chapters in all parts (or direct chapters)

        Returns:
            List[Scene]: All scenes sorted by order
        """
        all_scenes = []

        if self.use_parts_structure:
            # Traverse: Parts → Chapters → Scenes
            for part in sorted(self.parts, key=lambda p: p.order):
                for chapter in sorted(part.chapters, key=lambda c: c.order):
                    for scene in sorted(chapter.scenes, key=lambda s: s.order):
                        all_scenes.append(scene)
        else:
            # Traverse: Chapters → Scenes (legacy)
            for chapter in sorted(self.chapters, key=lambda c: c.order):
                for scene in sorted(chapter.scenes, key=lambda s: s.order):
                    all_scenes.append(scene)

        return all_scenes

    def get_total_word_count(self) -> int:
        """Calculate total word count for entire manuscript"""
        if self.use_parts_structure:
            return sum(part.get_total_word_count() for part in self.parts)
        else:
            return sum(chapter.get_total_word_count() for chapter in self.chapters)

    def get_full_text(self) -> str:
        """
        Get the complete manuscript text (all scenes concatenated)

        Returns:
            str: Complete manuscript text with part/chapter/scene hierarchy
        """
        text_parts = []

        if self.use_parts_structure:
            for part in sorted(self.parts, key=lambda p: p.order):
                # Add part title (markdown level 2)
                text_parts.append(f"\n\n## {part.title}\n\n")

                for chapter in sorted(part.chapters, key=lambda c: c.order):
                    # Add chapter title (markdown level 3)
                    text_parts.append(f"\n\n### {chapter.title}\n\n")

                    for scene in sorted(chapter.scenes, key=lambda s: s.order):
                        if scene.content:
                            text_parts.append(scene.content)
                            text_parts.append("\n\n")
        else:
            # Legacy structure
            for chapter in sorted(self.chapters, key=lambda c: c.order):
                text_parts.append(f"\n\n# {chapter.title}\n\n")

                for scene in sorted(chapter.scenes, key=lambda s: s.order):
                    if scene.content:
                        text_parts.append(scene.content)
                        text_parts.append("\n\n")

        return ''.join(text_parts).strip()

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization"""
        return {
            'use_parts_structure': self.use_parts_structure,
            'parts': [part.to_dict() for part in self.parts],
            'chapters': [chapter.to_dict() for chapter in self.chapters],  # Legacy
            'current_scene_id': self.current_scene_id
        }

    @staticmethod
    def from_dict(data: dict) -> 'ManuscriptStructure':
        """Create ManuscriptStructure from dictionary"""
        use_parts = data.get('use_parts_structure', False)

        structure = ManuscriptStructure(
            use_parts_structure=use_parts,
            current_scene_id=data.get('current_scene_id')
        )

        if use_parts:
            # Load parts (modern structure)
            for part_data in data.get('parts', []):
                part = Part.from_dict(part_data)
                structure.parts.append(part)
        else:
            # Load direct chapters (legacy structure)
            for chapter_data in data.get('chapters', []):
                chapter = Chapter.from_dict(chapter_data)
                structure.chapters.append(chapter)

        return structure

    @staticmethod
    def create_default(use_parts: bool = False) -> 'ManuscriptStructure':
        """
        Create a default manuscript structure

        Args:
            use_parts: If True, create Part 1 → Chapter 1 → Scene 1
                       If False, create Chapter 1 → Scene 1 (legacy)

        Returns:
            ManuscriptStructure: Default structure
        """
        structure = ManuscriptStructure(use_parts_structure=use_parts)

        # Create Scene 1
        scene = Scene.create_new("Scene 1", order=0, content="")

        # Create Chapter 1
        chapter = Chapter.create_new("Chapter 1", order=0)
        chapter.add_scene(scene)

        if use_parts:
            # Modern: Part 1 → Chapter 1 → Scene 1
            part = Part.create_new("Part 1", order=0)
            part.add_chapter(chapter)
            structure.add_part(part)
        else:
            # Legacy: Chapter 1 → Scene 1
            structure.add_chapter(chapter)

        structure.current_scene_id = scene.id

        return structure
