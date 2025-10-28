"""
Note data model - Generic notes for any project
"""
from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime
import uuid


@dataclass
class Note:
    """
    Represents a generic note.

    Notes are universal containers available in all project types for capturing
    ideas, reminders, plot points, or any other miscellaneous information.

    Attributes:
        title: Note title
        content: Full content/body of the note
        tags: List of tags for categorization and search
        id: Unique identifier
        created_date: ISO format creation timestamp
        modified_date: ISO format last modification timestamp
        linked_to_scene: ID of linked scene (if applicable)
        linked_to_character: ID of linked character (if applicable)
        linked_to_location: ID of linked location (if applicable)
        color: Optional color for visual categorization (hex format)
        pinned: Whether the note is pinned to the top
    """
    title: str
    content: str = ""
    tags: List[str] = field(default_factory=list)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_date: str = ""
    modified_date: str = ""

    # Optional links to other entities
    linked_to_scene: str = ""  # Scene ID
    linked_to_character: str = ""  # Character ID
    linked_to_location: str = ""  # Location ID

    # Visual and organizational metadata
    color: str = ""  # Hex color code, e.g., "#FFD700"
    pinned: bool = False  # Pin important notes to the top

    def __post_init__(self):
        """Initialize timestamps if not provided"""
        if not self.created_date:
            self.created_date = datetime.now().isoformat()
        if not self.modified_date:
            self.modified_date = datetime.now().isoformat()

    def update_modified_date(self):
        """Update the modified_date to current time"""
        self.modified_date = datetime.now().isoformat()

    def add_tag(self, tag: str):
        """
        Add a tag to the note.

        Args:
            tag: Tag to add
        """
        tag = tag.lower().strip()
        if tag and tag not in self.tags:
            self.tags.append(tag)
            self.update_modified_date()

    def remove_tag(self, tag: str):
        """
        Remove a tag from the note.

        Args:
            tag: Tag to remove
        """
        tag = tag.lower().strip()
        if tag in self.tags:
            self.tags.remove(tag)
            self.update_modified_date()

    def has_tag(self, tag: str) -> bool:
        """
        Check if note has a specific tag.

        Args:
            tag: Tag to check

        Returns:
            bool: True if tag exists
        """
        return tag.lower().strip() in self.tags

    def toggle_pin(self):
        """Toggle the pinned state of the note"""
        self.pinned = not self.pinned
        self.update_modified_date()

    def link_to_scene(self, scene_id: str):
        """
        Link note to a scene.

        Args:
            scene_id: ID of the scene to link
        """
        self.linked_to_scene = scene_id
        self.update_modified_date()

    def link_to_character(self, character_id: str):
        """
        Link note to a character.

        Args:
            character_id: ID of the character to link
        """
        self.linked_to_character = character_id
        self.update_modified_date()

    def link_to_location(self, location_id: str):
        """
        Link note to a location.

        Args:
            location_id: ID of the location to link
        """
        self.linked_to_location = location_id
        self.update_modified_date()

    def clear_links(self):
        """Clear all entity links"""
        self.linked_to_scene = ""
        self.linked_to_character = ""
        self.linked_to_location = ""
        self.update_modified_date()

    def has_links(self) -> bool:
        """Check if note has any links to other entities"""
        return bool(self.linked_to_scene or self.linked_to_character or self.linked_to_location)

    def get_word_count(self) -> int:
        """
        Get word count of the note content.

        Returns:
            int: Number of words
        """
        return len(self.content.split())

    def to_dict(self) -> dict:
        """
        Convert note to dictionary for JSON serialization.

        Returns:
            dict: Note data as dictionary
        """
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'tags': self.tags,
            'created_date': self.created_date,
            'modified_date': self.modified_date,
            'linked_to_scene': self.linked_to_scene,
            'linked_to_character': self.linked_to_character,
            'linked_to_location': self.linked_to_location,
            'color': self.color,
            'pinned': self.pinned
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Note':
        """
        Create Note instance from dictionary.

        Args:
            data: Dictionary containing note data

        Returns:
            Note: New Note instance
        """
        return cls(
            id=data.get('id', str(uuid.uuid4())),
            title=data.get('title', 'Untitled Note'),
            content=data.get('content', ''),
            tags=data.get('tags', []),
            created_date=data.get('created_date', datetime.now().isoformat()),
            modified_date=data.get('modified_date', datetime.now().isoformat()),
            linked_to_scene=data.get('linked_to_scene', ''),
            linked_to_character=data.get('linked_to_character', ''),
            linked_to_location=data.get('linked_to_location', ''),
            color=data.get('color', ''),
            pinned=data.get('pinned', False)
        )
