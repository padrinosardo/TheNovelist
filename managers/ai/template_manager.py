"""
Template Manager - Gestisce i template AI Writing Guide per generi letterari
"""
import os
from typing import List, Dict, Optional
from pathlib import Path
from utils.logger import AppLogger


class TemplateManager:
    """
    Manages AI Writing Guide templates for different literary genres

    Provides methods to:
    - List available templates
    - Load template content
    - Fill template placeholders with project data
    """

    # Template directory relative to project root
    TEMPLATES_DIR = "resources/ai_templates"

    # Mapping genre names to template files
    GENRE_TEMPLATES = {
        "default": "default.md",
        "thriller": "thriller.md",
        "fantasy": "fantasy.md",
        "romance": "romance.md",
        "scifi": "scifi.md",
        "sci-fi": "scifi.md",  # Alias
        "science fiction": "scifi.md",  # Alias
    }

    # POV translations (from code to Italian display)
    POV_TRANSLATIONS = {
        "first_person": "Prima persona",
        "third_limited": "Terza persona limitata",
        "third_omniscient": "Terza persona omnisciente",
        "second_person": "Seconda persona",
        "multiple_pov": "POV multiplo",
    }

    def __init__(self):
        """Initialize Template Manager"""
        self.templates_path = self._get_templates_directory()
        AppLogger.info(f"TemplateManager initialized. Templates dir: {self.templates_path}")

    def _get_templates_directory(self) -> Path:
        """
        Get absolute path to templates directory

        Returns:
            Path: Absolute path to templates directory
        """
        # Get project root (assuming managers/ai/template_manager.py structure)
        current_file = Path(__file__)
        project_root = current_file.parent.parent.parent
        templates_dir = project_root / self.TEMPLATES_DIR

        if not templates_dir.exists():
            AppLogger.error(f"Templates directory not found: {templates_dir}")
            raise FileNotFoundError(f"Templates directory not found: {templates_dir}")

        return templates_dir

    def get_available_templates(self) -> List[Dict[str, str]]:
        """
        Get list of available templates

        Returns:
            List[Dict]: List of template info dictionaries
                [{
                    "id": "thriller",
                    "name": "Thriller",
                    "file": "thriller.md",
                    "description": "Template per thriller psicologici"
                }, ...]
        """
        templates = [
            {
                "id": "default",
                "name": "Default (Generico)",
                "file": "default.md",
                "description": "Template generico adatto a qualsiasi genere"
            },
            {
                "id": "thriller",
                "name": "Thriller",
                "file": "thriller.md",
                "description": "Template specializzato per thriller psicologici"
            },
            {
                "id": "fantasy",
                "name": "Fantasy",
                "file": "fantasy.md",
                "description": "Template per fantasy con worldbuilding e magia"
            },
            {
                "id": "romance",
                "name": "Romance",
                "file": "romance.md",
                "description": "Template per romance e relazioni romantiche"
            },
            {
                "id": "scifi",
                "name": "Science Fiction",
                "file": "scifi.md",
                "description": "Template per fantascienza e speculazione scientifica"
            }
        ]

        # Filter to only templates that exist
        available = []
        for template in templates:
            template_path = self.templates_path / template["file"]
            if template_path.exists():
                available.append(template)
            else:
                AppLogger.warning(f"Template file not found: {template['file']}")

        return available

    def load_template(self, template_id: str) -> Optional[str]:
        """
        Load template content from file

        Args:
            template_id: Template ID (e.g., "thriller", "fantasy", "default")

        Returns:
            str: Template content or None if not found
        """
        # Normalize template ID
        template_id = template_id.lower().strip()

        # Get template filename
        if template_id in self.GENRE_TEMPLATES:
            filename = self.GENRE_TEMPLATES[template_id]
        else:
            # Try to find by matching genre
            AppLogger.warning(f"Unknown template ID: {template_id}, using default")
            filename = self.GENRE_TEMPLATES["default"]

        template_path = self.templates_path / filename

        if not template_path.exists():
            AppLogger.error(f"Template file not found: {template_path}")
            return None

        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()

            AppLogger.info(f"Loaded template: {template_id} ({len(content)} chars)")
            return content

        except Exception as e:
            AppLogger.error(f"Error loading template {template_id}: {e}")
            return None

    def fill_template_placeholders(self, template_content: str, project) -> str:
        """
        Fill template placeholders with project data

        Replaces placeholders like {{PROJECT_TITLE}} with actual project values.

        Args:
            template_content: Raw template content with placeholders
            project: Project model instance

        Returns:
            str: Template with placeholders replaced
        """
        if not template_content:
            return ""

        # Build replacement dictionary
        replacements = {
            "{{PROJECT_TITLE}}": project.title or "Untitled",
            "{{AUTHOR}}": project.author or "Unknown Author",
            "{{GENRE}}": project.genre or "General",
            "{{LANGUAGE}}": self._format_language(project.language),
            "{{SYNOPSIS}}": project.synopsis or "[Da scrivere]",
            "{{SETTING_TIME}}": project.setting_time_period or "[Da definire]",
            "{{SETTING_LOCATION}}": project.setting_location or "[Da definire]",
            "{{TONE}}": project.narrative_tone or "[Da definire]",
            "{{POV}}": self._format_pov(project.narrative_pov),
            "{{THEMES}}": self._format_themes(project.themes),
            "{{TARGET_AUDIENCE}}": project.target_audience or "[Da definire]",
            "{{STORY_NOTES}}": project.story_notes or "[Nessuna nota aggiuntiva]",
        }

        # Perform replacements
        filled_content = template_content
        for placeholder, value in replacements.items():
            filled_content = filled_content.replace(placeholder, value)

        AppLogger.debug(f"Template placeholders filled ({len(replacements)} replacements)")
        return filled_content

    def _format_language(self, language_code: str) -> str:
        """
        Format language code to readable name

        Args:
            language_code: Language code (it, en, es, etc.)

        Returns:
            str: Formatted language name
        """
        language_names = {
            "it": "Italiano",
            "en": "English",
            "es": "Español",
            "fr": "Français",
            "de": "Deutsch"
        }
        return language_names.get(language_code, language_code.upper())

    def _format_pov(self, pov_code: str) -> str:
        """
        Format POV code to readable Italian

        Args:
            pov_code: POV code (first_person, third_limited, etc.)

        Returns:
            str: Formatted POV in Italian
        """
        if not pov_code:
            return "[Da definire]"

        return self.POV_TRANSLATIONS.get(pov_code, pov_code)

    def _format_themes(self, themes: List[str]) -> str:
        """
        Format themes list to comma-separated string

        Args:
            themes: List of theme strings

        Returns:
            str: Comma-separated themes or placeholder
        """
        if not themes:
            return "[Da definire]"

        return ", ".join(themes)

    def suggest_template_for_genre(self, genre: str) -> str:
        """
        Suggest best template based on genre string

        Args:
            genre: Genre string from project

        Returns:
            str: Suggested template ID
        """
        genre_lower = genre.lower()

        # Direct matches
        if any(keyword in genre_lower for keyword in ["thriller", "giallo", "suspense", "noir"]):
            return "thriller"

        if any(keyword in genre_lower for keyword in ["fantasy", "fantasia", "magia"]):
            return "fantasy"

        if any(keyword in genre_lower for keyword in ["romance", "romantico", "amore"]):
            return "romance"

        if any(keyword in genre_lower for keyword in ["sci-fi", "scifi", "fantascienza", "science fiction"]):
            return "scifi"

        # Default fallback
        return "default"

    def get_template_with_project_data(self, template_id: str, project) -> Optional[str]:
        """
        Convenience method: Load template and fill with project data in one call

        Args:
            template_id: Template ID to load
            project: Project instance with data

        Returns:
            str: Filled template content or None if error
        """
        template_content = self.load_template(template_id)
        if not template_content:
            return None

        return self.fill_template_placeholders(template_content, project)
