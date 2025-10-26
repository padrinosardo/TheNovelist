"""
Character data model
"""
from dataclasses import dataclass, field
from typing import List
import uuid


@dataclass
class Character:
    """
    Represents a character in the story

    Attributes:
        id: Unique identifier (auto-generated UUID)
        name: Character's full name
        description: Detailed description of the character
        images: List of image filenames associated with this character
    """
    name: str
    description: str = ""
    images: List[str] = field(default_factory=list)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def to_dict(self) -> dict:
        """
        Convert character to dictionary for JSON serialization

        Returns:
            dict: Character data as dictionary
        """
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'images': self.images
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Character':
        """
        Create Character instance from dictionary

        Args:
            data: Dictionary containing character data

        Returns:
            Character: New Character instance
        """
        return cls(
            id=data.get('id', str(uuid.uuid4())),
            name=data.get('name', ''),
            description=data.get('description', ''),
            images=data.get('images', [])
        )
