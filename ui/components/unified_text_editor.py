"""
Unified Text Editor - Base class for all text editors with robust zoom management
"""
from PySide6.QtWidgets import QTextEdit
from PySide6.QtGui import QFont
from PySide6.QtCore import Signal
from utils.zoom_manager import ZoomManager


class UnifiedTextEditor(QTextEdit):
    """
    Base class for all text editors in TheNovelist with unified zoom management.

    Features:
    - Automatic registration with ZoomManager
    - Zoom preserved across setHtml/setPlainText operations
    - Consistent zoom behavior across all editors
    - No manual zoom tracking needed

    Usage:
        editor = UnifiedTextEditor()
        # Zoom is handled automatically via ZoomManager
    """

    # Signal emitted when text changes (for compatibility)
    text_changed = Signal()

    def __init__(self, parent=None, auto_register: bool = True):
        """
        Initialize unified text editor

        Args:
            parent: Parent widget
            auto_register: Whether to auto-register with ZoomManager (default: True)
        """
        super().__init__(parent)

        # Internal state
        self._current_zoom_level = 100  # Zoom percentage (50-200%)
        self._zoom_manager = ZoomManager.instance()
        self._is_applying_zoom = False  # Prevent recursive zoom application

        # Auto-register with ZoomManager
        if auto_register:
            self._zoom_manager.register_editor(self)
            # Apply current global zoom
            self.apply_zoom_level(self._zoom_manager.get_zoom_level())

        # Connect text changed signal
        self.textChanged.connect(self._on_text_changed)

    def _on_text_changed(self):
        """Internal handler for text changes"""
        self.text_changed.emit()

    def apply_zoom_level(self, level: int):
        """
        Apply zoom level (called by ZoomManager)

        Args:
            level: Zoom level (50-200%)
        """
        import sys
        print(f"[DEBUG] UnifiedTextEditor.apply_zoom_level: Called with level={level}%", file=sys.stderr, flush=True)
        print(f"[DEBUG] UnifiedTextEditor: Current level = {self._current_zoom_level}%", file=sys.stderr, flush=True)

        if self._is_applying_zoom:
            print(f"[DEBUG] UnifiedTextEditor: Already applying zoom, skipping", file=sys.stderr, flush=True)
            return  # Prevent recursion

        self._is_applying_zoom = True
        try:
            # Calculate zoom difference from current level
            diff = level - self._current_zoom_level
            print(f"[DEBUG] UnifiedTextEditor: Zoom diff = {diff}", file=sys.stderr, flush=True)

            if diff > 0:
                # Zoom in
                print(f"[DEBUG] UnifiedTextEditor: Zooming IN by {abs(diff)} steps", file=sys.stderr, flush=True)
                for _ in range(abs(diff)):
                    self.zoomIn(1)
            elif diff < 0:
                # Zoom out
                print(f"[DEBUG] UnifiedTextEditor: Zooming OUT by {abs(diff)} steps", file=sys.stderr, flush=True)
                for _ in range(abs(diff)):
                    self.zoomOut(1)
            else:
                print(f"[DEBUG] UnifiedTextEditor: No zoom change needed", file=sys.stderr, flush=True)

            # Update current level
            self._current_zoom_level = level
            print(f"[DEBUG] UnifiedTextEditor: Zoom applied successfully, new level = {level}%", file=sys.stderr, flush=True)

        finally:
            self._is_applying_zoom = False

    def setHtml(self, html: str):
        """
        Override setHtml to preserve zoom

        Args:
            html: HTML content
        """
        import sys
        print(f"[DEBUG] UnifiedTextEditor.setHtml: Called, current zoom={self._current_zoom_level}%", file=sys.stderr, flush=True)

        # Save current zoom
        zoom = self._current_zoom_level
        print(f"[DEBUG] UnifiedTextEditor.setHtml: Saved zoom={zoom}%", file=sys.stderr, flush=True)

        # Set content (this resets zoom internally to 100%)
        super().setHtml(html)
        print(f"[DEBUG] UnifiedTextEditor.setHtml: Content set, now restoring zoom...", file=sys.stderr, flush=True)

        # Restore zoom by directly calling zoomIn/Out (avoid recursion with apply_zoom_level)
        if zoom != 100:
            diff = zoom - 100  # Now we're at 100% after setHtml
            print(f"[DEBUG] UnifiedTextEditor.setHtml: Need to adjust by {diff}%", file=sys.stderr, flush=True)
            if diff > 0:
                for _ in range(abs(diff)):
                    self.zoomIn(1)
                print(f"[DEBUG] UnifiedTextEditor.setHtml: Zoomed IN by {abs(diff)} steps", file=sys.stderr, flush=True)
            elif diff < 0:
                for _ in range(abs(diff)):
                    self.zoomOut(1)
                print(f"[DEBUG] UnifiedTextEditor.setHtml: Zoomed OUT by {abs(diff)} steps", file=sys.stderr, flush=True)

            # Update internal tracking
            self._current_zoom_level = zoom
            print(f"[DEBUG] UnifiedTextEditor.setHtml: Zoom restored to {zoom}%", file=sys.stderr, flush=True)

    def setPlainText(self, text: str):
        """
        Override setPlainText to preserve zoom

        Args:
            text: Plain text content
        """
        import sys
        print(f"[DEBUG] UnifiedTextEditor.setPlainText: Called, current zoom={self._current_zoom_level}%", file=sys.stderr, flush=True)

        # Save current zoom
        zoom = self._current_zoom_level
        print(f"[DEBUG] UnifiedTextEditor.setPlainText: Saved zoom={zoom}%", file=sys.stderr, flush=True)

        # Set content (this resets zoom internally to 100%)
        super().setPlainText(text)
        print(f"[DEBUG] UnifiedTextEditor.setPlainText: Content set, now restoring zoom...", file=sys.stderr, flush=True)

        # Restore zoom by directly calling zoomIn/Out (avoid recursion with apply_zoom_level)
        if zoom != 100:
            diff = zoom - 100  # Now we're at 100% after setPlainText
            print(f"[DEBUG] UnifiedTextEditor.setPlainText: Need to adjust by {diff}%", file=sys.stderr, flush=True)
            if diff > 0:
                for _ in range(abs(diff)):
                    self.zoomIn(1)
                print(f"[DEBUG] UnifiedTextEditor.setPlainText: Zoomed IN by {abs(diff)} steps", file=sys.stderr, flush=True)
            elif diff < 0:
                for _ in range(abs(diff)):
                    self.zoomOut(1)
                print(f"[DEBUG] UnifiedTextEditor.setPlainText: Zoomed OUT by {abs(diff)} steps", file=sys.stderr, flush=True)

            # Update internal tracking
            self._current_zoom_level = zoom
            print(f"[DEBUG] UnifiedTextEditor.setPlainText: Zoom restored to {zoom}%", file=sys.stderr, flush=True)

    def setText(self, text: str):
        """
        Set text (plain or HTML)

        Args:
            text: Text content
        """
        if '<' in text and ('>' in text):
            # Looks like HTML
            self.setHtml(text)
        else:
            self.setPlainText(text)

    def get_zoom_level(self) -> int:
        """
        Get current zoom level

        Returns:
            int: Zoom level (50-200%)
        """
        return self._current_zoom_level

    def zoom_in(self, increment: int = 10):
        """
        Increase zoom level

        Args:
            increment: Amount to increase (default: 10%)
        """
        self._zoom_manager.zoom_in(increment)

    def zoom_out(self, decrement: int = 10):
        """
        Decrease zoom level

        Args:
            decrement: Amount to decrease (default: 10%)
        """
        self._zoom_manager.zoom_out(decrement)

    def zoom_reset(self):
        """Reset zoom to default (100%)"""
        self._zoom_manager.reset_zoom()

    def closeEvent(self, event):
        """Unregister from zoom manager on close"""
        self._zoom_manager.unregister_editor(self)
        super().closeEvent(event)

    def __del__(self):
        """Cleanup: unregister from zoom manager"""
        try:
            self._zoom_manager.unregister_editor(self)
        except:
            pass  # Already unregistered or manager destroyed


class UnifiedPlainTextEditor(UnifiedTextEditor):
    """
    Plain text variant of UnifiedTextEditor (disables rich text formatting)
    """

    def __init__(self, parent=None, auto_register: bool = True):
        super().__init__(parent, auto_register)
        # Force plain text mode
        self.setAcceptRichText(False)


class UnifiedRichTextEditor(UnifiedTextEditor):
    """
    Rich text variant of UnifiedTextEditor (enables rich text formatting)

    This is a simple alias for clarity - UnifiedTextEditor already supports rich text
    """

    def __init__(self, parent=None, auto_register: bool = True):
        super().__init__(parent, auto_register)
        # Enable rich text mode (already default)
        self.setAcceptRichText(True)
