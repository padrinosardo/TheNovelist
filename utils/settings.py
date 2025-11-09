"""
Settings Manager - Persistent application settings
"""
import json
import os
from pathlib import Path
from typing import List, Any


class SettingsManager:
    """
    Manages application settings stored in JSON format
    Settings location: ~/.thenovelist/settings.json
    """

    def __init__(self):
        """Initialize settings manager"""
        self.settings_dir = Path.home() / ".thenovelist"
        self.settings_file = self.settings_dir / "settings.json"
        self.settings = self._load_settings()

    def _load_settings(self) -> dict:
        """
        Load settings from file

        Returns:
            dict: Settings dictionary
        """
        # Ensure settings directory exists
        self.settings_dir.mkdir(parents=True, exist_ok=True)

        # Load settings if file exists
        if self.settings_file.exists():
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading settings: {e}")
                return self._default_settings()
        else:
            # Create default settings
            settings = self._default_settings()
            self._save_settings(settings)
            return settings

    def _default_settings(self) -> dict:
        """
        Get default settings

        Returns:
            dict: Default settings
        """
        return {
            "recent_projects": [],
            "auto_save_enabled": True,
            "auto_save_interval": 5,  # minutes
            "theme": "light",
            "window_geometry": None,
            "last_directory": str(Path.home() / "Documents"),
            "preferred_ui_language": "it",  # UI language (separate from project language)
            "editor_zoom_level": 100,  # Editor zoom level (50-200%)
            "editor_font_size": 18,  # Font size for text editors (8-72pt)
            "toolbar_groups": {
                "script": True,  # Superscript/Subscript
                "smallcaps": True,  # Small Caps
                "alignment": True,  # Alignment buttons
                "special_chars": True,  # Quote, dashes, ellipsis
                "tables": True  # Table buttons
            },
            "analysis_tabs_visibility": {
                0: True,  # AI Assistant
                1: True,  # Grammar
                2: True,  # Repetitions
                3: True,  # Style
                4: True,  # Synopsis
                5: True   # Notes
            }
        }

    def _save_settings(self, settings: dict = None):
        """
        Save settings to file

        Args:
            settings: Settings dict to save (uses self.settings if None)
        """
        if settings is None:
            settings = self.settings

        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2)
        except Exception as e:
            print(f"Error saving settings: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a setting value

        Args:
            key: Setting key
            default: Default value if key not found

        Returns:
            Any: Setting value
        """
        return self.settings.get(key, default)

    def set(self, key: str, value: Any):
        """
        Set a setting value and save

        Args:
            key: Setting key
            value: Setting value
        """
        self.settings[key] = value
        self._save_settings()

    # ==================== Recent Projects ====================

    def add_recent_project(self, filepath: str, project_metadata: dict = None):
        """
        Add a project to recent projects list with metadata

        Args:
            filepath: Full path to project file
            project_metadata: Optional project metadata dict (title, type, dates, etc.)
        """
        recent = self.settings.get("recent_projects", [])

        # Ensure recent is a list (backward compatibility)
        if not isinstance(recent, list):
            recent = []

        # Convert old format (list of strings) to new format (list of dicts)
        if recent and isinstance(recent[0], str):
            recent = [{"filepath": path} for path in recent if isinstance(path, str)]

        # Remove if already in list (match by filepath)
        recent = [item for item in recent if item.get("filepath") != filepath]

        # Create metadata entry
        if project_metadata:
            entry = {
                "filepath": filepath,
                "title": project_metadata.get("title", ""),
                "author": project_metadata.get("author", ""),
                "project_type": project_metadata.get("project_type", "novel"),
                "created_date": project_metadata.get("created_date", ""),
                "modified_date": project_metadata.get("modified_date", ""),
                "last_opened_date": project_metadata.get("last_opened_date", ""),
                "genre": project_metadata.get("genre", ""),
                "target_word_count": project_metadata.get("target_word_count", 0)
            }
        else:
            # Minimal entry if no metadata provided
            entry = {"filepath": filepath}

        # Add to front
        recent.insert(0, entry)

        # Keep only last 10
        recent = recent[:10]

        self.set("recent_projects", recent)

    def get_recent_projects(self) -> List[str]:
        """
        Get list of recent project paths (only existing files)

        DEPRECATED: Use get_recent_projects_metadata() for full metadata

        Returns:
            List[str]: List of existing project file paths
        """
        metadata_list = self.get_recent_projects_metadata()
        return [item["filepath"] for item in metadata_list]

    def get_recent_projects_metadata(self) -> List[dict]:
        """
        Get list of recent projects with metadata (only existing files)

        Returns:
            List[dict]: List of project metadata dicts with keys:
                - filepath: Full path to project file
                - title: Project title
                - author: Author name
                - project_type: Type of project (novel, article, etc.)
                - created_date: ISO format creation date
                - modified_date: ISO format last modification date
                - last_opened_date: ISO format last opened date
                - genre: Genre/category
                - target_word_count: Target word count
        """
        recent = self.settings.get("recent_projects", [])

        # Ensure recent is a list (backward compatibility)
        if not isinstance(recent, list):
            recent = []

        # Convert old format (list of strings) to new format (list of dicts)
        if recent and isinstance(recent[0], str):
            recent = [{"filepath": path} for path in recent if isinstance(path, str)]

        # Filter out non-existent files
        existing = [item for item in recent if os.path.exists(item.get("filepath", ""))]

        # Update list if any were removed
        if len(existing) != len(recent):
            self.set("recent_projects", existing)

        return existing

    def update_project_last_opened(self, filepath: str, last_opened_date: str = None):
        """
        Update the last_opened_date for a project in the recent list

        Args:
            filepath: Full path to project file
            last_opened_date: ISO format date (default: current time)
        """
        from datetime import datetime

        if last_opened_date is None:
            last_opened_date = datetime.now().isoformat()

        recent = self.get_recent_projects_metadata()

        # Find and update the project
        for item in recent:
            if item.get("filepath") == filepath:
                item["last_opened_date"] = last_opened_date
                break

        self.set("recent_projects", recent)

    def clear_recent_projects(self):
        """Clear all recent projects"""
        self.set("recent_projects", [])

    # ==================== Auto-save ====================

    def get_auto_save_enabled(self) -> bool:
        """Get auto-save enabled setting"""
        return self.settings.get("auto_save_enabled", True)

    def set_auto_save_enabled(self, enabled: bool):
        """Set auto-save enabled"""
        self.set("auto_save_enabled", enabled)

    def get_auto_save_interval(self) -> int:
        """Get auto-save interval in minutes"""
        return self.settings.get("auto_save_interval", 5)

    def set_auto_save_interval(self, minutes: int):
        """Set auto-save interval in minutes"""
        self.set("auto_save_interval", minutes)

    # ==================== Theme ====================

    def get_theme(self) -> str:
        """Get current theme"""
        return self.settings.get("theme", "light")

    def set_theme(self, theme: str):
        """Set theme (light/dark)"""
        self.set("theme", theme)

    # ==================== Window ====================

    def get_window_geometry(self):
        """Get saved window geometry"""
        return self.settings.get("window_geometry")

    def set_window_geometry(self, geometry: dict):
        """Save window geometry"""
        self.set("window_geometry", geometry)

    def get_last_directory(self) -> str:
        """Get last used directory"""
        return self.settings.get("last_directory", str(Path.home() / "Documents"))

    def set_last_directory(self, directory: str):
        """Set last used directory"""
        self.set("last_directory", directory)

    # ==================== Language ====================

    def get_preferred_ui_language(self) -> str:
        """
        Get preferred UI language

        Note: This is separate from project language.
        - UI language: Controls interface text (future i18n)
        - Project language: Controls NLP analysis for manuscript

        Returns:
            str: Language code ('it', 'en', 'es', 'fr', 'de')
        """
        return self.settings.get("preferred_ui_language", "it")

    def set_preferred_ui_language(self, language: str):
        """
        Set preferred UI language

        Args:
            language: Language code ('it', 'en', 'es', 'fr', 'de')

        Note: This setting is for future UI localization.
        Currently, the UI is in Italian/English only.
        """
        # Validate language code
        valid_languages = ['it', 'en', 'es', 'fr', 'de']
        if language not in valid_languages:
            print(f"Warning: Invalid language code '{language}'. Using 'it'.")
            language = 'it'

        self.set("preferred_ui_language", language)

    # ==================== Toolbar Groups ====================

    def get_toolbar_groups(self) -> dict:
        """
        Get toolbar groups visibility settings

        Returns:
            dict: Dictionary with group names as keys and bool visibility as values
                - script: Superscript/Subscript buttons
                - smallcaps: Small Caps button
                - alignment: Alignment buttons
                - special_chars: Quote, dashes, ellipsis buttons
                - tables: Table manipulation buttons
        """
        default_groups = {
            "script": True,
            "smallcaps": True,
            "alignment": True,
            "special_chars": True,
            "tables": True
        }
        return self.settings.get("toolbar_groups", default_groups)

    def set_toolbar_group(self, group_name: str, visible: bool):
        """
        Set visibility for a specific toolbar group

        Args:
            group_name: Group name ('script', 'smallcaps', 'alignment', 'special_chars', 'tables')
            visible: True to show, False to hide
        """
        groups = self.get_toolbar_groups()
        if group_name in groups:
            groups[group_name] = visible
            self.set("toolbar_groups", groups)

    def is_toolbar_group_visible(self, group_name: str) -> bool:
        """
        Check if a toolbar group is visible

        Args:
            group_name: Group name

        Returns:
            bool: True if visible, False otherwise
        """
        groups = self.get_toolbar_groups()
        return groups.get(group_name, True)

    # ==================== Analysis Tabs Visibility ====================

    def get_analysis_tabs_visibility(self) -> dict:
        """
        Get analysis tabs visibility settings

        Returns:
            dict: Dictionary with tab indices as keys and bool visibility as values
                 {0: True, 1: False, 2: True, ...}
        """
        default_tabs = {
            0: True,  # AI Assistant
            1: True,  # Grammar
            2: True,  # Repetitions
            3: True,  # Style
            4: True,  # Synopsis
            5: True   # Notes
        }
        tabs = self.settings.get("analysis_tabs_visibility", default_tabs)

        # Ensure indices are integers (JSON may have converted them to strings)
        return {int(k): v for k, v in tabs.items()}

    def set_analysis_tab_visibility(self, tab_index: int, visible: bool):
        """
        Set visibility for a specific analysis tab

        Args:
            tab_index: Tab index (0-5)
            visible: True to show, False to hide
        """
        tabs = self.get_analysis_tabs_visibility()
        if tab_index in tabs:
            tabs[tab_index] = visible
            self.set("analysis_tabs_visibility", tabs)

    def is_analysis_tab_visible(self, tab_index: int) -> bool:
        """
        Check if an analysis tab is visible

        Args:
            tab_index: Tab index (0-5)

        Returns:
            bool: True if visible, False otherwise
        """
        tabs = self.get_analysis_tabs_visibility()
        return tabs.get(tab_index, True)

    # ==================== Editor Zoom ====================

    def get_editor_zoom_level(self) -> int:
        """
        Get editor zoom level

        Returns:
            int: Zoom level percentage (50-200, default 100)
        """
        return self.settings.get("editor_zoom_level", 100)

    def set_editor_zoom_level(self, level: int):
        """
        Set editor zoom level

        Args:
            level: Zoom level percentage (50-200)
        """
        # Clamp value between 50 and 200
        clamped_level = max(50, min(200, level))
        self.set("editor_zoom_level", clamped_level)

    # ==================== Editor Font Size ====================

    def get_editor_font_size(self) -> int:
        """
        Get editor font size

        Returns:
            int: Font size in points (8-72, default 18)
        """
        return self.settings.get("editor_font_size", 18)

    def set_editor_font_size(self, size: int):
        """
        Set editor font size

        Args:
            size: Font size in points (8-72)
        """
        # Clamp value between 8 and 72
        clamped_size = max(8, min(72, size))
        self.set("editor_font_size", clamped_size)
