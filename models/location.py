"""
Location data model - For narrative locations and settings
"""
from dataclasses import dataclass, field
from typing import List
from datetime import datetime
import uuid


@dataclass
class Location:
    """
    Represents a location/place in the narrative.

    Locations can be used in novels, short stories, and screenplays to track
    places where action happens, with descriptions, images, and character associations.

    Attributes:
        name: Location name
        description: Detailed description of the location
        images: List of image filenames associated with the location
        characters_present: List of character IDs associated with this location
        notes: Additional notes about the location
        id: Unique identifier
        created_date: ISO format creation timestamp
        modified_date: ISO format last modification timestamp
        location_type: Type of location (e.g., "city", "room", "planet")
        parent_location_id: ID of parent location for hierarchical organization
    """
    name: str
    description: str = ""
    images: List[str] = field(default_factory=list)
    characters_present: List[str] = field(default_factory=list)
    notes: str = ""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_date: str = ""
    modified_date: str = ""

    # Optional metadata
    location_type: str = ""  # e.g., "city", "room", "planet", "country"
    parent_location_id: str = ""  # For hierarchy: room -> house -> city

    def __post_init__(self):
        """Initialize timestamps if not provided"""
        if not self.created_date:
            self.created_date = datetime.now().isoformat()
        if not self.modified_date:
            self.modified_date = datetime.now().isoformat()

    def update_modified_date(self):
        """Update the modified_date to current time"""
        self.modified_date = datetime.now().isoformat()

    def add_image(self, image_filename: str):
        """
        Add an image to the location.

        Args:
            image_filename: Filename of the image
        """
        if image_filename not in self.images:
            self.images.append(image_filename)
            self.update_modified_date()

    def remove_image(self, image_filename: str):
        """
        Remove an image from the location.

        Args:
            image_filename: Filename of the image to remove
        """
        if image_filename in self.images:
            self.images.remove(image_filename)
            self.update_modified_date()

    def add_character(self, character_id: str):
        """
        Associate a character with this location.

        Args:
            character_id: ID of the character
        """
        if character_id not in self.characters_present:
            self.characters_present.append(character_id)
            self.update_modified_date()

    def remove_character(self, character_id: str):
        """
        Remove character association from this location.

        Args:
            character_id: ID of the character to remove
        """
        if character_id in self.characters_present:
            self.characters_present.remove(character_id)
            self.update_modified_date()

    def to_dict(self) -> dict:
        """
        Convert location to dictionary for JSON serialization.

        Returns:
            dict: Location data as dictionary
        """
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'images': self.images,
            'characters_present': self.characters_present,
            'notes': self.notes,
            'created_date': self.created_date,
            'modified_date': self.modified_date,
            'location_type': self.location_type,
            'parent_location_id': self.parent_location_id
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Location':
        """
        Create Location instance from dictionary.

        Args:
            data: Dictionary containing location data

        Returns:
            Location: New Location instance
        """
        return cls(
            id=data.get('id', str(uuid.uuid4())),
            name=data.get('name', 'Unnamed Location'),
            description=data.get('description', ''),
            images=data.get('images', []),
            characters_present=data.get('characters_present', []),
            notes=data.get('notes', ''),
            created_date=data.get('created_date', datetime.now().isoformat()),
            modified_date=data.get('modified_date', datetime.now().isoformat()),
            location_type=data.get('location_type', ''),
            parent_location_id=data.get('parent_location_id', '')
        )
