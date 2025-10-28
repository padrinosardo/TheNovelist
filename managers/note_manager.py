"""
Note Manager - Specialized manager for generic notes
"""
from typing import List, Optional
from models.note import Note
from models.container_type import ContainerType
from managers.container_manager import ContainerManager
from utils.logger import logger


class NoteManager:
    """
    Specialized manager for handling generic notes.

    Provides methods for organizing notes with support for tags,
    colors, pinning, and entity linking.

    Attributes:
        container_manager: The underlying container manager
        container_type: Always NOTES
    """

    def __init__(self, container_manager: ContainerManager):
        """
        Initialize the note manager.

        Args:
            container_manager: The container manager instance
        """
        self.container_manager = container_manager
        self.container_type = ContainerType.NOTES

    def add_note(self, title: str, content: str = "", color: str = "", pinned: bool = False) -> str:
        """
        Create a new note.

        Args:
            title: Note title
            content: Note content
            color: Hex color code
            pinned: Whether to pin the note

        Returns:
            str: ID of the created note
        """
        note = Note(
            title=title,
            content=content,
            color=color,
            pinned=pinned
        )

        note_id = self.container_manager.add_item(self.container_type, note)
        logger.info(f"Created note: {title} (ID: {note_id})")
        return note_id

    def add_note_object(self, note: Note) -> str:
        """
        Add a note object directly.

        Args:
            note: Note object to add

        Returns:
            str: ID of the created note
        """
        note_id = self.container_manager.add_item(self.container_type, note)
        logger.info(f"Created note: {note.title} (ID: {note_id})")
        return note_id

    def get_note(self, note_id: str) -> Optional[Note]:
        """
        Get a note by ID.

        Args:
            note_id: ID of the note

        Returns:
            Optional[Note]: The note if found, None otherwise
        """
        return self.container_manager.get_item(self.container_type, note_id)

    def get_all_notes(self) -> List[Note]:
        """
        Get all notes.

        Returns:
            List[Note]: List of all notes
        """
        return self.container_manager.get_all_items(self.container_type)

    def update_note(self, note: Note) -> bool:
        """
        Update an existing note.

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

    def delete_note(self, note_id: str) -> bool:
        """
        Delete a note.

        Args:
            note_id: ID of the note to delete

        Returns:
            bool: True if deletion was successful
        """
        note = self.get_note(note_id)
        success = self.container_manager.delete_item(self.container_type, note_id)

        if success and note:
            logger.info(f"Deleted note: {note.title} (ID: {note_id})")

        return success

    def get_pinned_notes(self) -> List[Note]:
        """
        Get all pinned notes.

        Returns:
            List[Note]: List of pinned notes
        """
        all_notes = self.get_all_notes()
        return [note for note in all_notes if note.pinned]

    def get_notes_by_tag(self, tag: str) -> List[Note]:
        """
        Get all notes with a specific tag.

        Args:
            tag: Tag to filter by

        Returns:
            List[Note]: List of matching notes
        """
        all_notes = self.get_all_notes()
        return [note for note in all_notes if note.has_tag(tag)]

    def get_notes_by_color(self, color: str) -> List[Note]:
        """
        Get all notes with a specific color.

        Args:
            color: Hex color code

        Returns:
            List[Note]: List of matching notes
        """
        all_notes = self.get_all_notes()
        return [note for note in all_notes if note.color == color]

    def get_notes_linked_to_scene(self, scene_id: str) -> List[Note]:
        """
        Get all notes linked to a specific scene.

        Args:
            scene_id: ID of the scene

        Returns:
            List[Note]: List of linked notes
        """
        all_notes = self.get_all_notes()
        return [note for note in all_notes if note.linked_to_scene == scene_id]

    def get_notes_linked_to_character(self, character_id: str) -> List[Note]:
        """
        Get all notes linked to a specific character.

        Args:
            character_id: ID of the character

        Returns:
            List[Note]: List of linked notes
        """
        all_notes = self.get_all_notes()
        return [note for note in all_notes if note.linked_to_character == character_id]

    def get_notes_linked_to_location(self, location_id: str) -> List[Note]:
        """
        Get all notes linked to a specific location.

        Args:
            location_id: ID of the location

        Returns:
            List[Note]: List of linked notes
        """
        all_notes = self.get_all_notes()
        return [note for note in all_notes if note.linked_to_location == location_id]

    def get_notes_with_links(self) -> List[Note]:
        """
        Get all notes that have links to other entities.

        Returns:
            List[Note]: List of notes with links
        """
        all_notes = self.get_all_notes()
        return [note for note in all_notes if note.has_links()]

    def get_all_tags(self) -> List[str]:
        """
        Get a list of all unique tags used across all notes.

        Returns:
            List[str]: List of tag names
        """
        all_notes = self.get_all_notes()
        tags = set()
        for note in all_notes:
            tags.update(note.tags)
        return sorted(list(tags))

    def get_all_colors(self) -> List[str]:
        """
        Get a list of all unique colors used across all notes.

        Returns:
            List[str]: List of color codes
        """
        all_notes = self.get_all_notes()
        colors = set(note.color for note in all_notes if note.color)
        return sorted(list(colors))

    def search_notes(self, query: str) -> List[Note]:
        """
        Search notes by title or content.

        Args:
            query: Search query string

        Returns:
            List[Note]: List of matching notes
        """
        query = query.lower()
        all_notes = self.get_all_notes()

        return [
            note for note in all_notes
            if (query in note.title.lower() or query in note.content.lower())
        ]

    def toggle_pin(self, note_id: str) -> bool:
        """
        Toggle the pinned state of a note.

        Args:
            note_id: ID of the note

        Returns:
            bool: True if toggle was successful
        """
        note = self.get_note(note_id)
        if not note:
            return False

        note.toggle_pin()
        return self.update_note(note)

    def get_notes_sorted_by_date(self, reverse: bool = False) -> List[Note]:
        """
        Get all notes sorted by creation date.

        Args:
            reverse: If True, sort newest first

        Returns:
            List[Note]: Sorted list of notes
        """
        all_notes = self.get_all_notes()
        return sorted(all_notes, key=lambda n: n.created_date, reverse=reverse)

    def get_notes_sorted_by_modified(self, reverse: bool = False) -> List[Note]:
        """
        Get all notes sorted by last modified date.

        Args:
            reverse: If True, sort newest first

        Returns:
            List[Note]: Sorted list of notes
        """
        all_notes = self.get_all_notes()
        return sorted(all_notes, key=lambda n: n.modified_date, reverse=reverse)

    def get_recently_modified_notes(self, limit: int = 10) -> List[Note]:
        """
        Get the most recently modified notes.

        Args:
            limit: Maximum number of notes to return

        Returns:
            List[Note]: List of recently modified notes
        """
        notes = self.get_notes_sorted_by_modified(reverse=True)
        return notes[:limit]

    def save(self) -> bool:
        """
        Save all notes to disk.

        Returns:
            bool: True if save was successful
        """
        return self.container_manager.save_container(self.container_type)
