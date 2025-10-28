"""
Timeline Event data model - For chronological events in narratives
"""
from dataclasses import dataclass, field
from typing import List
from datetime import datetime
import uuid


@dataclass
class TimelineEvent:
    """
    Represents an event in the narrative timeline.

    Timeline events help organize the chronological structure of the story,
    tracking when events happen, who is involved, and where they take place.

    Attributes:
        title: Event title/name
        date: Date/time in the story (e.g., "Year 2145", "May 3rd", "Chapter 1")
        description: Detailed description of the event
        characters: List of character IDs involved in the event
        locations: List of location IDs where the event takes place
        id: Unique identifier
        created_date: ISO format creation timestamp (real world)
        modified_date: ISO format last modification timestamp (real world)
        sort_order: Manual sort order for organizing events chronologically
    """
    title: str
    date: str = ""  # In-story date (flexible format)
    description: str = ""
    characters: List[str] = field(default_factory=list)  # Character IDs
    locations: List[str] = field(default_factory=list)  # Location IDs
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_date: str = ""  # Real world timestamp
    modified_date: str = ""  # Real world timestamp

    # For manual chronological ordering
    sort_order: int = 0

    def __post_init__(self):
        """Initialize timestamps if not provided"""
        if not self.created_date:
            self.created_date = datetime.now().isoformat()
        if not self.modified_date:
            self.modified_date = datetime.now().isoformat()

    def update_modified_date(self):
        """Update the modified_date to current time"""
        self.modified_date = datetime.now().isoformat()

    def add_character(self, character_id: str):
        """
        Add a character to the event.

        Args:
            character_id: ID of the character to add
        """
        if character_id not in self.characters:
            self.characters.append(character_id)
            self.update_modified_date()

    def remove_character(self, character_id: str):
        """
        Remove a character from the event.

        Args:
            character_id: ID of the character to remove
        """
        if character_id in self.characters:
            self.characters.remove(character_id)
            self.update_modified_date()

    def add_location(self, location_id: str):
        """
        Add a location to the event.

        Args:
            location_id: ID of the location to add
        """
        if location_id not in self.locations:
            self.locations.append(location_id)
            self.update_modified_date()

    def remove_location(self, location_id: str):
        """
        Remove a location from the event.

        Args:
            location_id: ID of the location to remove
        """
        if location_id in self.locations:
            self.locations.remove(location_id)
            self.update_modified_date()

    def to_dict(self) -> dict:
        """
        Convert timeline event to dictionary for JSON serialization.

        Returns:
            dict: Timeline event data as dictionary
        """
        return {
            'id': self.id,
            'title': self.title,
            'date': self.date,
            'description': self.description,
            'characters': self.characters,
            'locations': self.locations,
            'created_date': self.created_date,
            'modified_date': self.modified_date,
            'sort_order': self.sort_order
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'TimelineEvent':
        """
        Create TimelineEvent instance from dictionary.

        Args:
            data: Dictionary containing timeline event data

        Returns:
            TimelineEvent: New TimelineEvent instance
        """
        return cls(
            id=data.get('id', str(uuid.uuid4())),
            title=data.get('title', 'Untitled Event'),
            date=data.get('date', ''),
            description=data.get('description', ''),
            characters=data.get('characters', []),
            locations=data.get('locations', []),
            created_date=data.get('created_date', datetime.now().isoformat()),
            modified_date=data.get('modified_date', datetime.now().isoformat()),
            sort_order=data.get('sort_order', 0)
        )
