"""
Project data model
"""
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Project:
    """
    Represents a writing project

    Attributes:
        title: Project title
        author: Author name
        created_date: ISO format creation date
        modified_date: ISO format last modification date
        manuscript_text: The main text content
    """
    title: str
    author: str
    created_date: str
    modified_date: str
    manuscript_text: str = ""

    @classmethod
    def create_new(cls, title: str, author: str) -> 'Project':
        """
        Create a new project with current timestamps

        Args:
            title: Project title
            author: Author name

        Returns:
            Project: New Project instance
        """
        now = datetime.now().isoformat()
        return cls(
            title=title,
            author=author,
            created_date=now,
            modified_date=now,
            manuscript_text=""
        )

    def update_modified_date(self):
        """Update the modified_date to current time"""
        self.modified_date = datetime.now().isoformat()

    def to_dict(self) -> dict:
        """
        Convert project to dictionary for JSON serialization

        Returns:
            dict: Project data as dictionary
        """
        return {
            'title': self.title,
            'author': self.author,
            'created_date': self.created_date,
            'modified_date': self.modified_date
        }

    @classmethod
    def from_dict(cls, data: dict, manuscript_text: str = "") -> 'Project':
        """
        Create Project instance from dictionary

        Args:
            data: Dictionary containing project metadata
            manuscript_text: The manuscript text content

        Returns:
            Project: New Project instance
        """
        return cls(
            title=data.get('title', 'Untitled'),
            author=data.get('author', 'Unknown'),
            created_date=data.get('created_date', datetime.now().isoformat()),
            modified_date=data.get('modified_date', datetime.now().isoformat()),
            manuscript_text=manuscript_text
        )
