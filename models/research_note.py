"""
Research Note data model - For research notes and background information
"""
from dataclasses import dataclass, field
from typing import List
from datetime import datetime
import uuid


@dataclass
class ResearchNote:
    """
    Represents a research note with sources and tags.

    Research notes are used to organize background research, historical facts,
    technical information, or any reference material needed for writing.

    Attributes:
        title: Note title
        content: Full content/body of the note
        sources: List of sources (URLs, citations, references)
        tags: List of tags for categorization and search
        id: Unique identifier
        created_date: ISO format creation timestamp
        modified_date: ISO format last modification timestamp
        category: Category for organization (e.g., "history", "technology", "culture")
    """
    title: str
    content: str = ""
    sources: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_date: str = ""
    modified_date: str = ""

    # Optional metadata
    category: str = ""  # e.g., "history", "technology", "culture", "science"

    def __post_init__(self):
        """Initialize timestamps if not provided"""
        if not self.created_date:
            self.created_date = datetime.now().isoformat()
        if not self.modified_date:
            self.modified_date = datetime.now().isoformat()

    def update_modified_date(self):
        """Update the modified_date to current time"""
        self.modified_date = datetime.now().isoformat()

    def add_source(self, source: str):
        """
        Add a source to the note.

        Args:
            source: Source URL or citation
        """
        if source and source not in self.sources:
            self.sources.append(source)
            self.update_modified_date()

    def remove_source(self, source: str):
        """
        Remove a source from the note.

        Args:
            source: Source to remove
        """
        if source in self.sources:
            self.sources.remove(source)
            self.update_modified_date()

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

    def to_dict(self) -> dict:
        """
        Convert research note to dictionary for JSON serialization.

        Returns:
            dict: Research note data as dictionary
        """
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'sources': self.sources,
            'tags': self.tags,
            'created_date': self.created_date,
            'modified_date': self.modified_date,
            'category': self.category
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'ResearchNote':
        """
        Create ResearchNote instance from dictionary.

        Args:
            data: Dictionary containing research note data

        Returns:
            ResearchNote: New ResearchNote instance
        """
        return cls(
            id=data.get('id', str(uuid.uuid4())),
            title=data.get('title', 'Untitled Note'),
            content=data.get('content', ''),
            sources=data.get('sources', []),
            tags=data.get('tags', []),
            created_date=data.get('created_date', datetime.now().isoformat()),
            modified_date=data.get('modified_date', datetime.now().isoformat()),
            category=data.get('category', '')
        )
