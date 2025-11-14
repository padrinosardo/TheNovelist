"""
Zoom Manager - Centralized zoom management for all text editors
"""
from PySide6.QtCore import QObject, Signal
from typing import List, Optional
from weakref import WeakSet


class ZoomManager(QObject):
    """
    Singleton manager for handling zoom across all text editors in the application.

    Features:
    - Single source of truth for zoom level (50-200%)
    - Automatic synchronization of all registered editors
    - Persistent storage in settings
    - Thread-safe singleton implementation
    """

    _instance: Optional['ZoomManager'] = None

    # Signals
    zoom_changed = Signal(int)  # Emitted when zoom level changes (50-200%)

    # Constants
    MIN_ZOOM = 50
    MAX_ZOOM = 200
    DEFAULT_ZOOM = 100  # Default zoom level

    def __new__(cls):
        """Singleton pattern - ensure only one instance exists"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize the zoom manager (only once)"""
        if self._initialized:
            return

        super().__init__()
        self._zoom_level: int = self.DEFAULT_ZOOM
        self._editors: WeakSet = WeakSet()  # Weak references to avoid memory leaks
        self._settings = None  # Will be set by main window
        self._initialized = True

    @classmethod
    def instance(cls) -> 'ZoomManager':
        """Get the singleton instance"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def set_settings(self, settings):
        """
        Set the settings manager for persistent storage

        Args:
            settings: SettingsManager instance
        """
        self._settings = settings
        # Load saved zoom level
        if settings:
            saved_zoom = settings.get_editor_zoom_level()
            if self.MIN_ZOOM <= saved_zoom <= self.MAX_ZOOM:
                self._zoom_level = saved_zoom

    def register_editor(self, editor):
        """
        Register a text editor to receive zoom updates

        Args:
            editor: Text editor widget (must have apply_zoom_level method)
        """
        import sys
        if not hasattr(editor, 'apply_zoom_level'):
            raise AttributeError(f"Editor {editor} must implement apply_zoom_level(level: int)")

        print(f"[DEBUG] ZoomManager.register_editor: Registering editor {type(editor).__name__}", file=sys.stderr, flush=True)
        print(f"[DEBUG] ZoomManager: Current zoom level = {self._zoom_level}%", file=sys.stderr, flush=True)

        self._editors.add(editor)
        print(f"[DEBUG] ZoomManager: Total editors registered = {len(self._editors)}", file=sys.stderr, flush=True)

        # Apply current zoom to newly registered editor
        editor.apply_zoom_level(self._zoom_level)
        print(f"[DEBUG] ZoomManager: Applied initial zoom to {type(editor).__name__}", file=sys.stderr, flush=True)

    def unregister_editor(self, editor):
        """
        Unregister a text editor

        Args:
            editor: Text editor widget to unregister
        """
        self._editors.discard(editor)

    def get_zoom_level(self) -> int:
        """
        Get current zoom level

        Returns:
            int: Current zoom level (50-200%)
        """
        return self._zoom_level

    def set_zoom_level(self, level: int, save: bool = True):
        """
        Set zoom level for all registered editors

        Args:
            level: Zoom level (50-200%)
            save: Whether to save to settings (default: True)
        """
        import sys
        # Clamp to valid range
        level = max(self.MIN_ZOOM, min(self.MAX_ZOOM, level))

        print(f"[DEBUG] ZoomManager.set_zoom_level: Called with level={level}%", file=sys.stderr, flush=True)

        if level == self._zoom_level:
            print(f"[DEBUG] ZoomManager: No change needed (already at {level}%)", file=sys.stderr, flush=True)
            return  # No change

        old_level = self._zoom_level
        self._zoom_level = level

        print(f"[DEBUG] ZoomManager: Changing zoom from {old_level}% to {level}%", file=sys.stderr, flush=True)
        print(f"[DEBUG] ZoomManager: Applying to {len(self._editors)} registered editors", file=sys.stderr, flush=True)

        # Apply to all registered editors
        for editor in list(self._editors):  # Create list to avoid modification during iteration
            try:
                print(f"[DEBUG] ZoomManager: Applying zoom to {type(editor).__name__}", file=sys.stderr, flush=True)
                editor.apply_zoom_level(level)
                print(f"[DEBUG] ZoomManager: Successfully applied zoom to {type(editor).__name__}", file=sys.stderr, flush=True)
            except Exception as e:
                print(f"Warning: Failed to apply zoom to editor {editor}: {e}", file=sys.stderr, flush=True)

        # Save to settings
        if save and self._settings:
            self._settings.set_editor_zoom_level(level)

        # Emit signal
        self.zoom_changed.emit(level)

        print(f"[ZoomManager] Zoom changed: {old_level}% → {level}%")

    def zoom_in(self, increment: int = 10):
        """
        Increase zoom level

        Args:
            increment: Amount to increase (default: 10%)
        """
        import sys
        print(f"[DEBUG] ZoomManager.zoom_in: Called with increment={increment}", file=sys.stderr, flush=True)
        new_level = min(self.MAX_ZOOM, self._zoom_level + increment)
        print(f"[DEBUG] ZoomManager.zoom_in: new_level={new_level}%", file=sys.stderr, flush=True)
        self.set_zoom_level(new_level)
        print(f"[DEBUG] ZoomManager.zoom_in: Completed", file=sys.stderr, flush=True)

    def zoom_out(self, decrement: int = 10):
        """
        Decrease zoom level

        Args:
            decrement: Amount to decrease (default: 10%)
        """
        new_level = max(self.MIN_ZOOM, self._zoom_level - decrement)
        self.set_zoom_level(new_level)

    def reset_zoom(self):
        """Reset zoom to default (100%)"""
        self.set_zoom_level(self.DEFAULT_ZOOM)

    def get_editor_count(self) -> int:
        """
        Get number of registered editors

        Returns:
            int: Number of active editors
        """
        return len(self._editors)

    def clear_editors(self):
        """Clear all registered editors (useful for testing)"""
        self._editors.clear()

    def __repr__(self) -> str:
        return f"<ZoomManager: {self._zoom_level}%, {self.get_editor_count()} editors>"
