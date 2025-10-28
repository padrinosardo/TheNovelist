"""
Research Manager - Specialized manager for research notes
"""
from typing import List, Optional
from models.research_note import ResearchNote
from models.container_type import ContainerType
from managers.container_manager import ContainerManager
from utils.logger import logger


class ResearchManager:
    """
    Specialized manager for handling research notes.

    Provides methods for organizing, searching, and managing research notes
    with support for sources, tags, and categories.

    Attributes:
        container_manager: The underlying container manager
        container_type: Always RESEARCH
    """

    def __init__(self, container_manager: ContainerManager):
        """
        Initialize the research manager.

        Args:
            container_manager: The container manager instance
        """
        self.container_manager = container_manager
        self.container_type = ContainerType.RESEARCH

    def add_research_note(self, title: str, content: str = "", category: str = "") -> str:
        """
        Create a new research note.

        Args:
            title: Note title
            content: Note content
            category: Category for organization

        Returns:
            str: ID of the created note
        """
        note = ResearchNote(
            title=title,
            content=content,
            category=category
        )

        note_id = self.container_manager.add_item(self.container_type, note)
        logger.info(f"Created research note: {title} (ID: {note_id})")
        return note_id

    def add_research_note_object(self, note: ResearchNote) -> str:
        """
        Add a research note object directly.

        Args:
            note: ResearchNote object to add

        Returns:
            str: ID of the created research note
        """
        note_id = self.container_manager.add_item(self.container_type, note)
        logger.info(f"Created research note: {note.title} (ID: {note_id})")
        return note_id

    def get_research_note(self, note_id: str) -> Optional[ResearchNote]:
        """
        Get a research note by ID.

        Args:
            note_id: ID of the note

        Returns:
            Optional[ResearchNote]: The note if found, None otherwise
        """
        return self.container_manager.get_item(self.container_type, note_id)

    def get_all_research_notes(self) -> List[ResearchNote]:
        """
        Get all research notes.

        Returns:
            List[ResearchNote]: List of all research notes
        """
        return self.container_manager.get_all_items(self.container_type)

    def update_research_note(self, note: ResearchNote) -> bool:
        """
        Update an existing research note.

        Args:
            note: Updated note object

        Returns:
            bool: True if update was successful
        """
        note.update_modified_date()
        return self.container_manager.update_item(
            self.container_type,
            note.id,
            note
        )

    def delete_research_note(self, note_id: str) -> bool:
        """
        Delete a research note.

        Args:
            note_id: ID of the note to delete

        Returns:
            bool: True if deletion was successful
        """
        note = self.get_research_note(note_id)
        success = self.container_manager.delete_item(self.container_type, note_id)

        if success and note:
            logger.info(f"Deleted research note: {note.title} (ID: {note_id})")

        return success

    def get_notes_by_category(self, category: str) -> List[ResearchNote]:
        """
        Get all research notes in a specific category.

        Args:
            category: Category to filter by

        Returns:
            List[ResearchNote]: List of matching notes
        """
        all_notes = self.get_all_research_notes()
        return [note for note in all_notes if note.category == category]

    def get_notes_by_tag(self, tag: str) -> List[ResearchNote]:
        """
        Get all research notes with a specific tag.

        Args:
            tag: Tag to filter by

        Returns:
            List[ResearchNote]: List of matching notes
        """
        all_notes = self.get_all_research_notes()
        return [note for note in all_notes if note.has_tag(tag)]

    def get_all_categories(self) -> List[str]:
        """
        Get a list of all unique categories.

        Returns:
            List[str]: List of category names
        """
        all_notes = self.get_all_research_notes()
        categories = set(note.category for note in all_notes if note.category)
        return sorted(list(categories))

    def get_all_tags(self) -> List[str]:
        """
        Get a list of all unique tags used across all notes.

        Returns:
            List[str]: List of tag names
        """
        all_notes = self.get_all_research_notes()
        tags = set()
        for note in all_notes:
            tags.update(note.tags)
        return sorted(list(tags))

    def search_notes(self, query: str) -> List[ResearchNote]:
        """
        Search research notes by title, content, or sources.

        Args:
            query: Search query string

        Returns:
            List[ResearchNote]: List of matching notes
        """
        query = query.lower()
        all_notes = self.get_all_research_notes()
        results = []

        for note in all_notes:
            # Check title
            if query in note.title.lower():
                results.append(note)
                continue

            # Check content
            if query in note.content.lower():
                results.append(note)
                continue

            # Check sources
            for source in note.sources:
                if query in source.lower():
                    results.append(note)
                    break

        return results

    def get_notes_with_sources(self) -> List[ResearchNote]:
        """
        Get all research notes that have at least one source.

        Returns:
            List[ResearchNote]: List of notes with sources
        """
        all_notes = self.get_all_research_notes()
        return [note for note in all_notes if note.sources]

    def get_notes_without_sources(self) -> List[ResearchNote]:
        """
        Get all research notes that have no sources.

        Returns:
            List[ResearchNote]: List of notes without sources
        """
        all_notes = self.get_all_research_notes()
        return [note for note in all_notes if not note.sources]

    def save(self) -> bool:
        """
        Save all research notes to disk.

        Returns:
            bool: True if save was successful
        """
        return self.container_manager.save_container(self.container_type)
