"""
Project data model
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List
from models.project_type import ProjectType


@dataclass
class Project:
    """
    Represents a writing project

    Attributes:
        title: Project title
        author: Author name
        language: Project language code ('it', 'en', 'es', 'fr', 'de')
        project_type: Type of project (novel, article, etc.)
        created_date: ISO format creation date
        modified_date: ISO format last modification date
        manuscript_text: The main text content (legacy, kept for compatibility)
        genre: Genre/category (optional)
        target_word_count: Target word count goal (optional)
        tags: List of tags for organization (optional)
    """
    title: str
    author: str
    language: str = "it"  # Default: Italian
    project_type: ProjectType = ProjectType.NOVEL  # Default: Novel
    created_date: str = ""
    modified_date: str = ""
    manuscript_text: str = ""

    # Optional metadata fields
    genre: str = ""
    target_word_count: int = 0
    tags: List[str] = field(default_factory=list)
    containers_version: str = "1.0"  # Version of container system (Milestone 2)

    @classmethod
    def create_new(cls, title: str, author: str, language: str = "it",
                   project_type: ProjectType = ProjectType.NOVEL,
                   genre: str = "", target_word_count: int = 0,
                   tags: List[str] = None) -> 'Project':
        """
        Create a new project with current timestamps

        Args:
            title: Project title
            author: Author name
            language: Project language code (default: 'it')
            project_type: Type of project (default: NOVEL)
            genre: Genre/category (optional)
            target_word_count: Target word count (optional)
            tags: List of tags (optional)

        Returns:
            Project: New Project instance
        """
        now = datetime.now().isoformat()
        return cls(
            title=title,
            author=author,
            language=language,
            project_type=project_type,
            created_date=now,
            modified_date=now,
            manuscript_text="",
            genre=genre,
            target_word_count=target_word_count,
            tags=tags if tags is not None else []
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
            'language': self.language,
            'project_type': self.project_type.value,  # Save as string
            'created_date': self.created_date,
            'modified_date': self.modified_date,
            'genre': self.genre,
            'target_word_count': self.target_word_count,
            'tags': self.tags,
            'containers_version': self.containers_version
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
        # Parse project_type with backward compatibility
        project_type_str = data.get('project_type', 'novel')
        try:
            project_type = ProjectType(project_type_str)
        except ValueError:
            project_type = ProjectType.NOVEL  # Fallback to NOVEL

        return cls(
            title=data.get('title', 'Untitled'),
            author=data.get('author', 'Unknown'),
            language=data.get('language', 'it'),  # Default to Italian for backward compatibility
            project_type=project_type,
            created_date=data.get('created_date', datetime.now().isoformat()),
            modified_date=data.get('modified_date', datetime.now().isoformat()),
            manuscript_text=manuscript_text,
            genre=data.get('genre', ''),
            target_word_count=data.get('target_word_count', 0),
            tags=data.get('tags', []),
            containers_version=data.get('containers_version', '1.0')  # Default to 1.0 for old projects
        )
