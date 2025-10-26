"""
Menu Bar Component
"""
from PySide6.QtWidgets import QMenuBar, QMenu
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtCore import Signal


class MenuBar(QMenuBar):
    """
    Professional menu bar with File, Edit, View, Tools, Help menus
    """

    # File menu signals
    new_project_requested = Signal()
    open_project_requested = Signal()
    recent_project_requested = Signal(str)  # filepath
    save_project_requested = Signal()
    save_project_as_requested = Signal()
    close_project_requested = Signal()
    exit_requested = Signal()

    # Edit menu signals
    undo_requested = Signal()
    redo_requested = Signal()
    cut_requested = Signal()
    copy_requested = Signal()
    paste_requested = Signal()
    find_requested = Signal()
    replace_requested = Signal()

    # View menu signals
    toggle_sidebar_requested = Signal()
    toggle_analysis_requested = Signal()
    zoom_in_requested = Signal()
    zoom_out_requested = Signal()
    zoom_reset_requested = Signal()

    # Tools menu signals
    grammar_check_requested = Signal()
    repetitions_check_requested = Signal()
    style_check_requested = Signal()

    # Help menu signals
    documentation_requested = Signal()
    about_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.recent_menu = None
        self._create_menus()

    def _create_menus(self):
        """Create all menus"""
        self._create_file_menu()
        self._create_edit_menu()
        self._create_view_menu()
        self._create_tools_menu()
        self._create_help_menu()

    def _create_file_menu(self):
        """Create File menu"""
        file_menu = self.addMenu("&File")

        # New Project
        new_action = QAction("&New Project", self)
        new_action.setShortcut(QKeySequence.StandardKey.New)
        new_action.setStatusTip("Create a new project")
        new_action.triggered.connect(self.new_project_requested.emit)
        file_menu.addAction(new_action)

        # Open Project
        open_action = QAction("&Open Project", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.setStatusTip("Open an existing project")
        open_action.triggered.connect(self.open_project_requested.emit)
        file_menu.addAction(open_action)

        # Recent Projects submenu
        self.recent_menu = QMenu("Open &Recent", self)
        self.recent_menu.setEnabled(False)  # Disabled until we have recent projects
        file_menu.addMenu(self.recent_menu)

        file_menu.addSeparator()

        # Save Project
        save_action = QAction("&Save Project", self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.setStatusTip("Save the current project")
        save_action.triggered.connect(self.save_project_requested.emit)
        file_menu.addAction(save_action)
        self.save_action = save_action

        # Save Project As
        save_as_action = QAction("Save Project &As...", self)
        save_as_action.setShortcut(QKeySequence.StandardKey.SaveAs)
        save_as_action.setStatusTip("Save the project with a new name")
        save_as_action.triggered.connect(self.save_project_as_requested.emit)
        file_menu.addAction(save_as_action)
        self.save_as_action = save_as_action

        file_menu.addSeparator()

        # Close Project
        close_action = QAction("&Close Project", self)
        close_action.setShortcut(QKeySequence("Ctrl+W"))
        close_action.setStatusTip("Close the current project")
        close_action.triggered.connect(self.close_project_requested.emit)
        file_menu.addAction(close_action)
        self.close_action = close_action

        file_menu.addSeparator()

        # Exit
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.setStatusTip("Exit the application")
        exit_action.triggered.connect(self.exit_requested.emit)
        file_menu.addAction(exit_action)

    def _create_edit_menu(self):
        """Create Edit menu"""
        edit_menu = self.addMenu("&Edit")

        # Undo
        undo_action = QAction("&Undo", self)
        undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        undo_action.triggered.connect(self.undo_requested.emit)
        edit_menu.addAction(undo_action)
        self.undo_action = undo_action

        # Redo
        redo_action = QAction("&Redo", self)
        redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        redo_action.triggered.connect(self.redo_requested.emit)
        edit_menu.addAction(redo_action)
        self.redo_action = redo_action

        edit_menu.addSeparator()

        # Cut
        cut_action = QAction("Cu&t", self)
        cut_action.setShortcut(QKeySequence.StandardKey.Cut)
        cut_action.triggered.connect(self.cut_requested.emit)
        edit_menu.addAction(cut_action)

        # Copy
        copy_action = QAction("&Copy", self)
        copy_action.setShortcut(QKeySequence.StandardKey.Copy)
        copy_action.triggered.connect(self.copy_requested.emit)
        edit_menu.addAction(copy_action)

        # Paste
        paste_action = QAction("&Paste", self)
        paste_action.setShortcut(QKeySequence.StandardKey.Paste)
        paste_action.triggered.connect(self.paste_requested.emit)
        edit_menu.addAction(paste_action)

        edit_menu.addSeparator()

        # Find
        find_action = QAction("&Find", self)
        find_action.setShortcut(QKeySequence.StandardKey.Find)
        find_action.triggered.connect(self.find_requested.emit)
        edit_menu.addAction(find_action)

        # Replace
        replace_action = QAction("&Replace", self)
        replace_action.setShortcut(QKeySequence.StandardKey.Replace)
        replace_action.triggered.connect(self.replace_requested.emit)
        edit_menu.addAction(replace_action)

    def _create_view_menu(self):
        """Create View menu"""
        view_menu = self.addMenu("&View")

        # Toggle Sidebar
        sidebar_action = QAction("Toggle &Sidebar", self)
        sidebar_action.setShortcut(QKeySequence("Ctrl+B"))
        sidebar_action.setCheckable(True)
        sidebar_action.setChecked(True)
        sidebar_action.triggered.connect(self.toggle_sidebar_requested.emit)
        view_menu.addAction(sidebar_action)
        self.sidebar_action = sidebar_action

        # Toggle Analysis Panels
        analysis_action = QAction("Toggle &Analysis Panels", self)
        analysis_action.setShortcut(QKeySequence("Ctrl+P"))
        analysis_action.setCheckable(True)
        analysis_action.setChecked(True)
        analysis_action.triggered.connect(self.toggle_analysis_requested.emit)
        view_menu.addAction(analysis_action)
        self.analysis_action = analysis_action

        view_menu.addSeparator()

        # Zoom In
        zoom_in_action = QAction("Zoom &In", self)
        zoom_in_action.setShortcut(QKeySequence.StandardKey.ZoomIn)
        zoom_in_action.triggered.connect(self.zoom_in_requested.emit)
        view_menu.addAction(zoom_in_action)

        # Zoom Out
        zoom_out_action = QAction("Zoom &Out", self)
        zoom_out_action.setShortcut(QKeySequence.StandardKey.ZoomOut)
        zoom_out_action.triggered.connect(self.zoom_out_requested.emit)
        view_menu.addAction(zoom_out_action)

        # Reset Zoom
        zoom_reset_action = QAction("&Reset Zoom", self)
        zoom_reset_action.setShortcut(QKeySequence("Ctrl+0"))
        zoom_reset_action.triggered.connect(self.zoom_reset_requested.emit)
        view_menu.addAction(zoom_reset_action)

    def _create_tools_menu(self):
        """Create Tools menu"""
        tools_menu = self.addMenu("&Tools")

        # Grammar Check
        grammar_action = QAction("&Grammar Check", self)
        grammar_action.setShortcut(QKeySequence("F7"))
        grammar_action.setStatusTip("Check grammar and spelling")
        grammar_action.triggered.connect(self.grammar_check_requested.emit)
        tools_menu.addAction(grammar_action)
        self.grammar_action = grammar_action

        # Repetitions Analysis
        repetitions_action = QAction("&Repetitions Analysis", self)
        repetitions_action.setShortcut(QKeySequence("F8"))
        repetitions_action.setStatusTip("Analyze word repetitions")
        repetitions_action.triggered.connect(self.repetitions_check_requested.emit)
        tools_menu.addAction(repetitions_action)
        self.repetitions_action = repetitions_action

        # Style Analysis
        style_action = QAction("&Style Analysis", self)
        style_action.setShortcut(QKeySequence("F9"))
        style_action.setStatusTip("Analyze writing style")
        style_action.triggered.connect(self.style_check_requested.emit)
        tools_menu.addAction(style_action)
        self.style_action = style_action

    def _create_help_menu(self):
        """Create Help menu"""
        help_menu = self.addMenu("&Help")

        # Documentation
        doc_action = QAction("&Documentation", self)
        doc_action.setShortcut(QKeySequence.StandardKey.HelpContents)
        doc_action.triggered.connect(self.documentation_requested.emit)
        help_menu.addAction(doc_action)

        help_menu.addSeparator()

        # About
        about_action = QAction("&About The Novelist", self)
        about_action.triggered.connect(self.about_requested.emit)
        help_menu.addAction(about_action)

    def set_project_open(self, is_open: bool):
        """
        Enable/disable menu items based on project state

        Args:
            is_open: True if a project is open
        """
        self.save_action.setEnabled(is_open)
        self.save_as_action.setEnabled(is_open)
        self.close_action.setEnabled(is_open)
        self.grammar_action.setEnabled(is_open)
        self.repetitions_action.setEnabled(is_open)
        self.style_action.setEnabled(is_open)

    def update_recent_projects(self, recent_projects: list):
        """
        Update the Recent Projects menu

        Args:
            recent_projects: List of recent project file paths
        """
        # Clear existing actions
        self.recent_menu.clear()

        if not recent_projects:
            # No recent projects
            self.recent_menu.setEnabled(False)
            no_recent = QAction("No recent projects", self)
            no_recent.setEnabled(False)
            self.recent_menu.addAction(no_recent)
        else:
            # Add recent projects
            self.recent_menu.setEnabled(True)

            for filepath in recent_projects:
                # Extract filename for display
                import os
                filename = os.path.basename(filepath)

                action = QAction(filename, self)
                action.setStatusTip(filepath)
                action.triggered.connect(lambda checked, path=filepath: self.recent_project_requested.emit(path))
                self.recent_menu.addAction(action)

            # Add separator and clear action
            self.recent_menu.addSeparator()
            clear_action = QAction("Clear Recent Projects", self)
            clear_action.triggered.connect(lambda: self.update_recent_projects([]))
            self.recent_menu.addAction(clear_action)
