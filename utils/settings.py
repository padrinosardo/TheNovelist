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
            "preferred_ui_language": "it"  # UI language (separate from project language)
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

    def add_recent_project(self, filepath: str):
        """
        Add a project to recent projects list

        Args:
            filepath: Full path to project file
        """
        recent = self.settings.get("recent_projects", [])

        # Remove if already in list
        if filepath in recent:
            recent.remove(filepath)

        # Add to front
        recent.insert(0, filepath)

        # Keep only last 10
        recent = recent[:10]

        self.set("recent_projects", recent)

    def get_recent_projects(self) -> List[str]:
        """
        Get list of recent project paths (only existing files)

        Returns:
            List[str]: List of existing project file paths
        """
        recent = self.settings.get("recent_projects", [])

        # Filter out non-existent files
        existing = [path for path in recent if os.path.exists(path)]

        # Update list if any were removed
        if len(existing) != len(recent):
            self.set("recent_projects", existing)

        return existing

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
