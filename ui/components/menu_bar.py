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
    export_project_requested = Signal()
    close_project_requested = Signal()
    create_backup_requested = Signal()
    restore_backup_requested = Signal()
    exit_requested = Signal()

    # Edit menu signals
    undo_requested = Signal()
    redo_requested = Signal()
    cut_requested = Signal()
    copy_requested = Signal()
    paste_requested = Signal()
    find_requested = Signal()
    replace_requested = Signal()

    # Manuscript menu signals
    add_chapter_requested = Signal()
    add_scene_requested = Signal()
    rename_requested = Signal()
    delete_requested = Signal()
    previous_scene_requested = Signal()
    next_scene_requested = Signal()
    go_to_scene_requested = Signal()

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
    view_error_log_requested = Signal()
    report_issue_requested = Signal()
    about_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.recent_menu = None
        self._create_menus()

    def _create_menus(self):
        """Create all menus"""
        self._create_file_menu()
        self._create_edit_menu()
        self._create_manuscript_menu()
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

        # Export Project
        export_action = QAction("&Export...", self)
        export_action.setShortcut(QKeySequence("Ctrl+E"))
        export_action.setStatusTip("Export project to PDF, DOCX, or Markdown")
        export_action.triggered.connect(self.export_project_requested.emit)
        file_menu.addAction(export_action)
        self.export_action = export_action

        file_menu.addSeparator()

        # Close Project
        close_action = QAction("&Close Project", self)
        close_action.setShortcut(QKeySequence("Ctrl+W"))
        close_action.setStatusTip("Close the current project")
        close_action.triggered.connect(self.close_project_requested.emit)
        file_menu.addAction(close_action)
        self.close_action = close_action

        file_menu.addSeparator()

        # Create Backup
        backup_action = QAction("Create &Backup", self)
        backup_action.setStatusTip("Create a backup of the current project")
        backup_action.triggered.connect(self.create_backup_requested.emit)
        file_menu.addAction(backup_action)
        self.backup_action = backup_action

        # Restore from Backup
        restore_action = QAction("Restore from Backup...", self)
        restore_action.setStatusTip("Restore project from a backup file")
        restore_action.triggered.connect(self.restore_backup_requested.emit)
        file_menu.addAction(restore_action)
        self.restore_action = restore_action

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
        find_action = QAction("&Find...", self)
        find_action.setShortcut(QKeySequence.StandardKey.Find)  # Cmd+F on Mac, Ctrl+F on others
        find_action.triggered.connect(self.find_requested.emit)
        edit_menu.addAction(find_action)
        self.find_action = find_action

        # Replace
        replace_action = QAction("&Replace...", self)
        # On Mac, use Cmd+Option+F instead of Cmd+H (which hides the app)
        import sys
        if sys.platform == 'darwin':  # macOS
            replace_action.setShortcut(QKeySequence("Ctrl+Alt+F"))
        else:
            replace_action.setShortcut(QKeySequence.StandardKey.Replace)
        replace_action.triggered.connect(self.replace_requested.emit)
        edit_menu.addAction(replace_action)
        self.replace_action = replace_action

    def _create_manuscript_menu(self):
        """Create Manuscript menu"""
        import sys
        manuscript_menu = self.addMenu("&Manuscript")

        # Add Chapter
        add_chapter_action = QAction("Add &Chapter", self)
        add_chapter_action.setShortcut(QKeySequence("Ctrl+Shift+N"))
        add_chapter_action.setStatusTip("Add a new chapter to the manuscript")
        add_chapter_action.triggered.connect(self.add_chapter_requested.emit)
        manuscript_menu.addAction(add_chapter_action)
        self.add_chapter_action = add_chapter_action

        # Add Scene
        add_scene_action = QAction("Add &Scene", self)
        # Use Ctrl+Alt+N to avoid conflict with Cmd+N (New Project)
        add_scene_action.setShortcut(QKeySequence("Ctrl+Alt+N"))
        add_scene_action.setStatusTip("Add a new scene to the current chapter")
        add_scene_action.triggered.connect(self.add_scene_requested.emit)
        manuscript_menu.addAction(add_scene_action)
        self.add_scene_action = add_scene_action

        manuscript_menu.addSeparator()

        # Rename
        rename_action = QAction("&Rename", self)
        rename_action.setShortcut(QKeySequence("F2"))
        rename_action.setStatusTip("Rename the selected chapter or scene")
        rename_action.triggered.connect(self.rename_requested.emit)
        manuscript_menu.addAction(rename_action)
        self.rename_action = rename_action

        # Delete
        delete_action = QAction("&Delete", self)
        if sys.platform == 'darwin':  # macOS
            delete_action.setShortcut(QKeySequence("Ctrl+Backspace"))
        else:
            delete_action.setShortcut(QKeySequence.StandardKey.Delete)
        delete_action.setStatusTip("Delete the selected chapter or scene")
        delete_action.triggered.connect(self.delete_requested.emit)
        manuscript_menu.addAction(delete_action)
        self.delete_action = delete_action

        manuscript_menu.addSeparator()

        # Previous Scene
        prev_scene_action = QAction("&Previous Scene", self)
        prev_scene_action.setShortcut(QKeySequence("Ctrl+["))
        prev_scene_action.setStatusTip("Navigate to previous scene")
        prev_scene_action.triggered.connect(self.previous_scene_requested.emit)
        manuscript_menu.addAction(prev_scene_action)
        self.prev_scene_action = prev_scene_action

        # Next Scene
        next_scene_action = QAction("&Next Scene", self)
        next_scene_action.setShortcut(QKeySequence("Ctrl+]"))
        next_scene_action.setStatusTip("Navigate to next scene")
        next_scene_action.triggered.connect(self.next_scene_requested.emit)
        manuscript_menu.addAction(next_scene_action)
        self.next_scene_action = next_scene_action

        manuscript_menu.addSeparator()

        # Go to Scene
        goto_scene_action = QAction("&Go to Scene...", self)
        goto_scene_action.setShortcut(QKeySequence("Ctrl+G"))
        goto_scene_action.setStatusTip("Quick navigation to any scene")
        goto_scene_action.triggered.connect(self.go_to_scene_requested.emit)
        manuscript_menu.addAction(goto_scene_action)
        self.goto_scene_action = goto_scene_action

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

        # View Error Log
        log_action = QAction("View Error &Log", self)
        log_action.setStatusTip("View application error log")
        log_action.triggered.connect(self.view_error_log_requested.emit)
        help_menu.addAction(log_action)

        # Report Issue
        report_action = QAction("&Report Issue", self)
        report_action.setStatusTip("Report a bug or issue")
        report_action.triggered.connect(self.report_issue_requested.emit)
        help_menu.addAction(report_action)

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
        self.export_action.setEnabled(is_open)
        self.close_action.setEnabled(is_open)
        self.backup_action.setEnabled(is_open)
        # Restore action is always enabled (can restore without open project)
        self.add_chapter_action.setEnabled(is_open)
        self.add_scene_action.setEnabled(is_open)
        self.rename_action.setEnabled(is_open)
        self.delete_action.setEnabled(is_open)
        self.prev_scene_action.setEnabled(is_open)
        self.next_scene_action.setEnabled(is_open)
        self.goto_scene_action.setEnabled(is_open)
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
