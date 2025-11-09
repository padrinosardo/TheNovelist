"""
Context Sidebar - Collapsible sidebar with tabs for contextual tools

Unified sidebar component for all document views (Characters, Locations, Scenes, Notes).
Features:
- Collapsible with toggle button
- Resizable width
- Tab-based content (AI, Grammar, Style, etc.)
- Saves state (collapsed/expanded, width)
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTabWidget,
    QSplitter, QFrame
)
from PySide6.QtCore import Qt, Signal, QSettings
from PySide6.QtGui import QIcon
from typing import Optional, List, Tuple


class ContextSidebar(QWidget):
    """
    Collapsible sidebar with customizable tabs

    Signals:
        visibility_changed(bool): Emitted when sidebar is shown/hidden
        width_changed(int): Emitted when sidebar width changes
    """

    visibility_changed = Signal(bool)
    width_changed = Signal(int)

    def __init__(self, sidebar_id: str = "default", default_width: int = 300, parent=None):
        """
        Initialize sidebar

        Args:
            sidebar_id: Unique identifier for saving settings
            default_width: Default width in pixels
            parent: Parent widget
        """
        super().__init__(parent)
        self.sidebar_id = sidebar_id
        self.default_width = default_width
        self._is_visible = True

        # Track tabs for individual visibility management
        self.tabs_data = []  # List of {'widget': QWidget, 'title': str, 'visible': bool}

        self._setup_ui()
        self._load_settings()

    def _setup_ui(self):
        """Setup the UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header with collapse button
        header = QWidget()
        header.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
                border-bottom: 1px solid #ddd;
            }
        """)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(5, 5, 5, 5)

        # Title
        self.title_label = QPushButton("Context Tools")
        self.title_label.setFlat(True)
        self.title_label.setStyleSheet("""
            QPushButton {
                text-align: left;
                font-weight: bold;
                font-size: 12px;
                color: #333;
                border: none;
                padding: 5px;
            }
        """)
        header_layout.addWidget(self.title_label)

        header_layout.addStretch()

        # Collapse button
        self.collapse_btn = QPushButton("◀")
        self.collapse_btn.setFixedSize(24, 24)
        self.collapse_btn.setToolTip("Collapse sidebar (more space for editor)")
        self.collapse_btn.clicked.connect(self.toggle_visibility)
        self.collapse_btn.setObjectName("collapse_btn")
        self.collapse_btn.setStyleSheet("""
            QPushButton#collapse_btn {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 3px;
                font-size: 10px;
                font-weight: bold;
            }
            QPushButton#collapse_btn:hover {
                background-color: #1976D2;
            }
        """)
        header_layout.addWidget(self.collapse_btn)

        layout.addWidget(header)

        # Tab widget for different tools
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background: white;
            }
            QTabBar::tab {
                background: #e0e0e0;
                padding: 8px 12px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background: #2196F3;
                color: white;
            }
            QTabBar::tab:hover:!selected {
                background: #bdbdbd;
            }
        """)
        layout.addWidget(self.tab_widget)

        # Set width constraints (resizable between min and max)
        self.setMinimumWidth(200)
        self.setMaximumWidth(800)
        # Set initial width (not fixed, can be resized by splitter)
        self.resize(self.default_width, self.height())

    def add_tab(self, widget: QWidget, title: str, icon: Optional[str] = None):
        """
        Add a tab to the sidebar

        Args:
            widget: Widget to display in tab
            title: Tab title
            icon: Optional icon name/emoji
        """
        if icon:
            tab_title = f"{icon} {title}"
        else:
            tab_title = title

        # Track tab data
        tab_index = len(self.tabs_data)
        self.tabs_data.append({
            'widget': widget,
            'title': tab_title,
            'visible': True,
            'index': tab_index
        })

        self.tab_widget.addTab(widget, tab_title)

    def toggle_visibility(self):
        """Toggle sidebar visibility"""
        self._is_visible = not self._is_visible

        if self._is_visible:
            # Show full sidebar - restore to resizable state
            self.tab_widget.show()
            self.title_label.show()
            # Remove fixed width constraint and restore min/max
            self.setMinimumWidth(200)
            self.setMaximumWidth(800)
            # Restore previous width
            self.resize(self.default_width, self.height())
            self.collapse_btn.setText("◀")
            self.collapse_btn.setFixedSize(24, 24)
            self.collapse_btn.setToolTip("Collapse sidebar")
            self.collapse_btn.setStyleSheet("""
                QPushButton#collapse_btn {
                    background-color: #2196F3;
                    color: white;
                    border: none;
                    border-radius: 3px;
                    font-size: 10px;
                    font-weight: bold;
                }
                QPushButton#collapse_btn:hover {
                    background-color: #1976D2;
                }
            """)
        else:
            # Hide content but keep expand button visible
            # Save current width before collapsing
            if self.width() > 40:
                self.default_width = self.width()
            self.tab_widget.hide()
            self.title_label.hide()
            # Fixed narrow width when collapsed
            self.setMinimumWidth(35)
            self.setMaximumWidth(35)
            # Make button vertical and larger
            self.collapse_btn.setText("🤖\n▶")
            self.collapse_btn.setFixedSize(30, 100)
            self.collapse_btn.setToolTip("Expand AI Assistant")
            self.collapse_btn.setStyleSheet("""
                QPushButton#collapse_btn {
                    background-color: #2196F3;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    font-size: 14px;
                    font-weight: bold;
                    padding: 8px 2px;
                }
                QPushButton#collapse_btn:hover {
                    background-color: #1976D2;
                }
            """)

        self.visibility_changed.emit(self._is_visible)
        self._save_settings()

    def set_visible(self, visible: bool):
        """Set sidebar visibility programmatically"""
        if visible != self._is_visible:
            self.toggle_visibility()

    def is_sidebar_visible(self) -> bool:
        """Check if sidebar is visible"""
        return self._is_visible

    def set_tab_visible(self, tab_index: int, visible: bool):
        """
        Show or hide a specific tab

        Args:
            tab_index: Index of tab to show/hide (0-based)
            visible: True to show, False to hide
        """
        if tab_index < 0 or tab_index >= len(self.tabs_data):
            return

        tab_data = self.tabs_data[tab_index]

        # If already in desired state, do nothing
        if tab_data['visible'] == visible:
            return

        tab_data['visible'] = visible

        if visible:
            # Re-add tab at correct position
            self._rebuild_tabs()
        else:
            # Remove tab from QTabWidget
            # Find current position in QTabWidget
            widget = tab_data['widget']
            for i in range(self.tab_widget.count()):
                if self.tab_widget.widget(i) == widget:
                    self.tab_widget.removeTab(i)
                    break

    def _rebuild_tabs(self):
        """Rebuild all tabs in correct order (only visible ones)"""
        # Clear all tabs
        self.tab_widget.clear()

        # Re-add only visible tabs in original order
        for tab_data in self.tabs_data:
            if tab_data['visible']:
                self.tab_widget.addTab(tab_data['widget'], tab_data['title'])

    def get_tab_count(self) -> int:
        """Get total number of tabs (including hidden)"""
        return len(self.tabs_data)

    def get_tab_title(self, tab_index: int) -> str:
        """
        Get tab title by index

        Args:
            tab_index: Tab index (0-based)

        Returns:
            Tab title or empty string if invalid index
        """
        if 0 <= tab_index < len(self.tabs_data):
            return self.tabs_data[tab_index]['title']
        return ""

    def is_tab_visible(self, tab_index: int) -> bool:
        """
        Check if a tab is visible

        Args:
            tab_index: Tab index (0-based)

        Returns:
            True if visible, False otherwise
        """
        if 0 <= tab_index < len(self.tabs_data):
            return self.tabs_data[tab_index]['visible']
        return False

    def _save_settings(self):
        """Save sidebar state to settings"""
        settings = QSettings("TheNovelist", "Sidebar")
        settings.setValue(f"{self.sidebar_id}/visible", self._is_visible)
        # Only save width when expanded (not when collapsed to button size)
        if self._is_visible:
            settings.setValue(f"{self.sidebar_id}/width", self.width())

    def _load_settings(self):
        """Load sidebar state from settings"""
        settings = QSettings("TheNovelist", "Sidebar")

        # Load visibility
        visible = settings.value(f"{self.sidebar_id}/visible", True, type=bool)
        if not visible:
            self._is_visible = True  # Start true
            self.toggle_visibility()  # Then toggle to false (collapses to button)

        # Load width (only used when expanded)
        saved_width = settings.value(f"{self.sidebar_id}/width", self.default_width, type=int)
        if saved_width > 40:  # Valid width for expanded state
            self.default_width = saved_width
            if self._is_visible:
                # Restore saved width (resizable)
                self.resize(saved_width, self.height())

    def resizeEvent(self, event):
        """Handle resize events"""
        super().resizeEvent(event)
        self.width_changed.emit(self.width())
        self._save_settings()


class CollapsibleSidebarContainer(QWidget):
    """
    Container that manages main content + collapsible sidebar

    Automatically adjusts main content when sidebar is collapsed
    """

    def __init__(self, main_widget: QWidget, sidebar: ContextSidebar, parent=None):
        """
        Initialize container

        Args:
            main_widget: Main content widget (editor)
            sidebar: ContextSidebar instance
            parent: Parent widget
        """
        super().__init__(parent)
        self.main_widget = main_widget
        self.sidebar = sidebar

        self._setup_ui()

    def _setup_ui(self):
        """Setup the UI with splitter"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Use splitter for resizable panels
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.setHandleWidth(6)  # Slightly wider for easier dragging
        self.splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #ccc;
                border-left: 1px solid #bbb;
                border-right: 1px solid #bbb;
            }
            QSplitter::handle:hover {
                background-color: #2196F3;
                border-left: 1px solid #1976D2;
                border-right: 1px solid #1976D2;
            }
        """)

        # Add main widget and sidebar
        self.splitter.addWidget(self.main_widget)
        self.splitter.addWidget(self.sidebar)

        # Set initial sizes (main widget gets most space)
        self.splitter.setStretchFactor(0, 3)  # Main widget
        self.splitter.setStretchFactor(1, 1)  # Sidebar

        layout.addWidget(self.splitter)

        # Connect sidebar visibility to adjust splitter
        self.sidebar.visibility_changed.connect(self._on_sidebar_visibility_changed)

    def _on_sidebar_visibility_changed(self, visible: bool):
        """Handle sidebar visibility changes"""
        # Sidebar manages its own visibility now (collapses to button only)
        # No need to hide/show here as the sidebar width changes handle the layout
        pass
