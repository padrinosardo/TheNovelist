"""
Workspace Container - Dynamic view switcher
"""
from PySide6.QtWidgets import QStackedWidget
from PySide6.QtCore import Signal


class WorkspaceContainer(QStackedWidget):
    """
    Container that switches between different views:
    - ManuscriptView: Text editor + analysis
    - CharactersListView: Grid of character cards
    - CharacterDetailView: Single character form
    """

    # Signals
    view_changed = Signal(str)  # view_name

    # View constants
    VIEW_MANUSCRIPT = "manuscript"
    VIEW_CHARACTERS_LIST = "characters_list"
    VIEW_CHARACTER_DETAIL = "character_detail"
    VIEW_STATISTICS = "statistics"

    # Dynamic container views
    VIEW_LOCATIONS = "locations"
    VIEW_RESEARCH = "research"
    VIEW_TIMELINE = "timeline"
    VIEW_SOURCES = "sources"
    VIEW_NOTES = "notes"

    def __init__(self, parent=None):
        super().__init__(parent)
        self._views = {}
        self._current_view_name = None

    def add_view(self, name: str, widget):
        """
        Add a view to the container

        Args:
            name: View identifier
            widget: Widget to add
        """
        self.addWidget(widget)
        self._views[name] = widget

    def show_view(self, name: str):
        """
        Show a specific view

        Args:
            name: View identifier
        """
        if name in self._views:
            widget = self._views[name]
            self.setCurrentWidget(widget)
            self._current_view_name = name
            self.view_changed.emit(name)

    def get_current_view(self):
        """
        Get the currently displayed view widget

        Returns:
            QWidget: Current view widget
        """
        return self.currentWidget()

    def get_current_view_name(self) -> str:
        """
        Get the name of the currently displayed view

        Returns:
            str: Current view name
        """
        return self._current_view_name

    def get_view(self, name: str):
        """
        Get a specific view widget by name

        Args:
            name: View identifier

        Returns:
            QWidget or None: View widget if found
        """
        return self._views.get(name)

    def show_manuscript(self):
        """Show the manuscript editor view"""
        self.show_view(self.VIEW_MANUSCRIPT)

    def show_characters_list(self):
        """Show the characters list view"""
        self.show_view(self.VIEW_CHARACTERS_LIST)

    def show_character_detail(self):
        """Show the character detail view"""
        self.show_view(self.VIEW_CHARACTER_DETAIL)

    def show_statistics(self):
        """Show the statistics dashboard view"""
        self.show_view(self.VIEW_STATISTICS)
