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

    # Story context fields - AI Integration (Milestone 1)
    synopsis: str = ""                      # Plot summary (max 1000 chars)
    setting_time_period: str = ""           # Time period/era
    setting_location: str = ""              # Geographic location
    narrative_tone: str = ""                # Narrative tone
    narrative_pov: str = ""                 # Point of view (first_person, third_limited, etc.)
    themes: List[str] = field(default_factory=list)  # Main themes
    target_audience: str = ""               # Target audience
    story_notes: str = ""                   # Additional story notes

    # AI Writing Guide (Milestone 2)
    ai_writing_guide_enabled: bool = False  # Whether AI Writing Guide is enabled
    ai_writing_guide_content: str = ""      # Markdown content of the Writing Guide

    # AI Custom Commands (Milestone 3)
    ai_commands: List[dict] = field(default_factory=list)  # Custom AI commands for this project

    # AI Provider Configuration (Milestone 5) - PER-PROJECT AI
    ai_provider_name: str = "claude"  # Active AI provider: 'claude', 'openai', 'ollama'
    ai_provider_config: dict = field(default_factory=lambda: {
        'api_key': '',
        'model': 'claude-3-haiku-20240307',
        'temperature': 0.7,
        'max_tokens': 2000
    })  # Provider-specific configuration

    @classmethod
    def create_new(cls, title: str, author: str, language: str = "it",
                   project_type: ProjectType = ProjectType.NOVEL,
                   genre: str = "", target_word_count: int = 0,
                   tags: List[str] = None,
                   include_default_commands: bool = True,
                   ai_provider_name: str = "claude",
                   ai_provider_config: dict = None) -> 'Project':
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
            include_default_commands: Whether to include default AI commands (default: True)
            ai_provider_name: AI provider name (default: 'claude')
            ai_provider_config: AI provider configuration (optional)

        Returns:
            Project: New Project instance
        """
        now = datetime.now().isoformat()

        # Get default AI commands if requested
        ai_commands = []
        if include_default_commands:
            try:
                from managers.ai.default_commands import get_all_default_commands
                ai_commands = get_all_default_commands()
            except ImportError:
                # If default_commands module is not available, continue without them
                pass

        # Default AI config if not provided
        if ai_provider_config is None:
            ai_provider_config = {
                'api_key': '',
                'model': 'claude-3-haiku-20240307',
                'temperature': 0.7,
                'max_tokens': 2000
            }

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
            tags=tags if tags is not None else [],
            ai_commands=ai_commands,
            ai_provider_name=ai_provider_name,
            ai_provider_config=ai_provider_config
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
            'containers_version': self.containers_version,
            # Story context fields
            'synopsis': self.synopsis,
            'setting_time_period': self.setting_time_period,
            'setting_location': self.setting_location,
            'narrative_tone': self.narrative_tone,
            'narrative_pov': self.narrative_pov,
            'themes': self.themes,
            'target_audience': self.target_audience,
            'story_notes': self.story_notes,
            # AI Writing Guide
            'ai_writing_guide_enabled': self.ai_writing_guide_enabled,
            'ai_writing_guide_content': self.ai_writing_guide_content,
            # AI Custom Commands
            'ai_commands': self.ai_commands,
            # AI Provider Configuration (Milestone 5)
            'ai_provider_name': self.ai_provider_name,
            'ai_provider_config': self.ai_provider_config
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
            containers_version=data.get('containers_version', '1.0'),  # Default to 1.0 for old projects
            # Story context fields (backward compatible - default to empty)
            synopsis=data.get('synopsis', ''),
            setting_time_period=data.get('setting_time_period', ''),
            setting_location=data.get('setting_location', ''),
            narrative_tone=data.get('narrative_tone', ''),
            narrative_pov=data.get('narrative_pov', ''),
            themes=data.get('themes', []),
            target_audience=data.get('target_audience', ''),
            story_notes=data.get('story_notes', ''),
            # AI Writing Guide (backward compatible)
            ai_writing_guide_enabled=data.get('ai_writing_guide_enabled', False),
            ai_writing_guide_content=data.get('ai_writing_guide_content', ''),
            # AI Custom Commands (backward compatible)
            ai_commands=data.get('ai_commands', []),
            # AI Provider Configuration (Milestone 5 - backward compatible)
            ai_provider_name=data.get('ai_provider_name', 'claude'),
            ai_provider_config=data.get('ai_provider_config', {
                'api_key': '',
                'model': 'claude-3-haiku-20240307',
                'temperature': 0.7,
                'max_tokens': 2000
            })
        )
