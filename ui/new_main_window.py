"""
The Novelist - Main Application Window (New Version)
"""
from PySide6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QSplitter,
                               QMessageBox, QFileDialog, QInputDialog, QProgressBar, QLabel)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QCloseEvent

from ui.components import (MenuBar, ProjectTree, WorkspaceContainer,
                           ManuscriptView, CharactersListView, CharacterDetailView)
from ui.styles import Stili
from managers.project_manager import ProjectManager
from workers.thread_analysis import AnalysisThread
from analysis.grammar import GrammarAnalyzer
from analysis.repetition import RepetitionAnalyzer
from analysis.style import StyleAnalyzer
from utils.settings import SettingsManager
import os


class TheNovelistMainWindow(QMainWindow):
    """
    Main application window for The Novelist
    Features:
    - Professional menu bar
    - Sidebar project tree
    - Dynamic workspace (manuscript/characters)
    - Full project management
    """

    def __init__(self):
        super().__init__()

        # Settings
        self.settings = SettingsManager()

        # Project management
        self.project_manager = ProjectManager()
        self.is_modified = False

        # Analysis
        self.analysis_thread = None
        self.grammar_analyzer = GrammarAnalyzer()
        self.repetitions_analyzer = RepetitionAnalyzer()
        self.style_analyzer = StyleAnalyzer()

        # Auto-save
        self.auto_save_enabled = True
        self.auto_save_interval = 5 * 60 * 1000  # 5 minutes in milliseconds
        self.auto_save_timer = QTimer()
        self.auto_save_timer.timeout.connect(self._auto_save)
        self.last_auto_save = None

        # Initialize UI
        self._initialize_ui()
        self._connect_signals()
        self._update_ui_state()

        # Start auto-save timer
        if self.auto_save_enabled:
            self.auto_save_timer.start(self.auto_save_interval)

        # Load recent projects
        self._update_recent_projects_menu()

    def _initialize_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("The Novelist")
        self.setGeometry(100, 100, 1400, 900)

        # Create menu bar
        self.menu_bar = MenuBar()
        self.setMenuBar(self.menu_bar)

        # Central widget with splitter
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Main horizontal splitter
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left: Project tree
        self.project_tree = ProjectTree()
        self.main_splitter.addWidget(self.project_tree)

        # Right: Workspace container
        self.workspace = WorkspaceContainer()

        # Create and add views
        self.manuscript_view = ManuscriptView()
        self.characters_list_view = CharactersListView()
        self.character_detail_view = CharacterDetailView(
            self.project_manager.character_manager
        )

        self.workspace.add_view(WorkspaceContainer.VIEW_MANUSCRIPT, self.manuscript_view)
        self.workspace.add_view(WorkspaceContainer.VIEW_CHARACTERS_LIST, self.characters_list_view)
        self.workspace.add_view(WorkspaceContainer.VIEW_CHARACTER_DETAIL, self.character_detail_view)

        # Show manuscript by default
        self.workspace.show_manuscript()

        self.main_splitter.addWidget(self.workspace)

        # Set splitter proportions (20% sidebar, 80% workspace)
        self.main_splitter.setStretchFactor(0, 2)
        self.main_splitter.setStretchFactor(1, 8)

        main_layout.addWidget(self.main_splitter)

        # Progress bar
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        self.progress.setMaximumHeight(20)
        self.progress.setStyleSheet(Stili.progress_bar())
        self.statusBar().addPermanentWidget(self.progress)

        # Auto-save indicator
        self.auto_save_label = QLabel()
        self.auto_save_label.setStyleSheet("color: #666; font-size: 11px; margin-right: 10px;")
        self.auto_save_label.setVisible(False)
        self.statusBar().addPermanentWidget(self.auto_save_label)

        # Status bar
        self.statusBar().showMessage("Ready - Create or open a project to start")

    def _connect_signals(self):
        """Connect all signals"""
        # Menu bar signals
        self.menu_bar.new_project_requested.connect(self.new_project)
        self.menu_bar.open_project_requested.connect(self.open_project)
        self.menu_bar.recent_project_requested.connect(self._open_recent_project)
        self.menu_bar.save_project_requested.connect(self.save_project)
        self.menu_bar.save_project_as_requested.connect(self.save_project_as)
        self.menu_bar.close_project_requested.connect(self.close_project)
        self.menu_bar.exit_requested.connect(self.close)

        # Edit menu
        self.menu_bar.undo_requested.connect(self._undo)
        self.menu_bar.redo_requested.connect(self._redo)

        # View menu
        self.menu_bar.toggle_sidebar_requested.connect(self._toggle_sidebar)
        self.menu_bar.toggle_analysis_requested.connect(self._toggle_analysis)

        # Tools menu
        self.menu_bar.grammar_check_requested.connect(self.analyze_grammar)
        self.menu_bar.repetitions_check_requested.connect(self.analyze_repetitions)
        self.menu_bar.style_check_requested.connect(self.analyze_style)

        # Help menu
        self.menu_bar.about_requested.connect(self._show_about)

        # Project tree signals
        self.project_tree.manuscript_selected.connect(self.workspace.show_manuscript)
        self.project_tree.characters_list_selected.connect(self._show_characters_list)
        self.project_tree.character_selected.connect(self._show_character_detail)
        self.project_tree.add_character_requested.connect(self._add_character)
        self.project_tree.delete_character_requested.connect(self._delete_character)

        # Characters list view signals
        self.characters_list_view.character_clicked.connect(self._show_character_detail)
        self.characters_list_view.add_character_requested.connect(self._add_character)

        # Character detail view signals
        self.character_detail_view.back_requested.connect(self._show_characters_list)
        self.character_detail_view.character_updated.connect(self._on_character_updated)
        self.character_detail_view.character_deleted.connect(self._on_character_deleted)

        # Manuscript view signals
        self.manuscript_view.text_changed.connect(self._on_text_changed)

    def _update_ui_state(self):
        """Update UI based on project state"""
        has_project = self.project_manager.has_project()

        # Update menu bar
        self.menu_bar.set_project_open(has_project)

        # Update window title
        if has_project:
            title = self.project_manager.get_project_title()
            modified = " *" if self.is_modified else ""
            self.setWindowTitle(f"The Novelist - {title}{modified}")
        else:
            self.setWindowTitle("The Novelist")

        # Update project tree
        if has_project:
            self.project_tree.load_project(
                self.project_manager.current_project.title,
                self.project_manager.character_manager.get_all_characters()
            )
            self.project_tree.select_manuscript()
        else:
            self.project_tree.clear_project()

    # ==================== Project Management ====================

    def new_project(self):
        """Create a new project"""
        # Check for unsaved changes
        if not self._check_unsaved_changes():
            return

        # Get project details from user
        title, ok = QInputDialog.getText(
            self,
            "New Project",
            "Project Title:"
        )

        if not ok or not title.strip():
            return

        author, ok = QInputDialog.getText(
            self,
            "New Project",
            "Author Name:"
        )

        if not ok or not author.strip():
            author = "Unknown"

        # Get save location
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Save New Project",
            f"{title}.tnp",
            "The Novelist Project (*.tnp)"
        )

        if not filepath:
            return

        # Create project
        success = self.project_manager.create_new_project(title, author, filepath)

        if success:
            # Setup images directory for character manager
            images_dir = self.project_manager.get_temp_images_directory()
            if images_dir:
                self.project_manager.character_manager.set_images_directory(images_dir)

            # Update character detail view with manager
            self.character_detail_view.set_character_manager(
                self.project_manager.character_manager
            )

            # Update characters list
            self.characters_list_view.set_images_directory(images_dir)

            self.is_modified = False
            self.manuscript_view.clear_text()
            self.manuscript_view.clear_analysis()
            self._update_ui_state()

            # Add to recent projects
            self.settings.add_recent_project(filepath)
            self._update_recent_projects_menu()

            self.statusBar().showMessage(f"Created new project: {title}", 3000)
        else:
            QMessageBox.critical(
                self,
                "Error",
                "Failed to create new project."
            )

    def open_project(self):
        """Open an existing project"""
        # Check for unsaved changes
        if not self._check_unsaved_changes():
            return

        # Select project file
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "Open Project",
            "",
            "The Novelist Project (*.tnp)"
        )

        if not filepath:
            return

        # Open project
        project, manuscript_text, characters = self.project_manager.open_project(filepath)

        if project:
            # Load manuscript
            self.manuscript_view.set_text(manuscript_text)

            # Setup images directory for character manager
            images_dir = self.project_manager.get_temp_images_directory()
            if images_dir:
                self.project_manager.character_manager.set_images_directory(images_dir)

            # Update character detail view with manager
            self.character_detail_view.set_character_manager(
                self.project_manager.character_manager
            )

            # Update characters list
            self.characters_list_view.set_images_directory(images_dir)

            self.is_modified = False
            self._update_ui_state()

            # Add to recent projects
            self.settings.add_recent_project(filepath)
            self._update_recent_projects_menu()

            self.statusBar().showMessage(f"Opened: {project.title}", 3000)
        else:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to open project:\n{filepath}"
            )

    def save_project(self):
        """Save the current project"""
        if not self.project_manager.has_project():
            QMessageBox.warning(
                self,
                "No Project",
                "Please create or open a project first."
            )
            return False

        # Get manuscript text
        manuscript_text = self.manuscript_view.get_text()

        # Save project
        success = self.project_manager.save_project(manuscript_text)

        if success:
            self.is_modified = False
            self._update_ui_state()
            self.statusBar().showMessage("Project saved successfully", 3000)
            return True
        else:
            QMessageBox.critical(
                self,
                "Error",
                "Failed to save project."
            )
            return False

    def save_project_as(self):
        """Save project with a new name"""
        if not self.project_manager.has_project():
            return False

        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Save Project As",
            f"{self.project_manager.get_project_title()}.tnp",
            "The Novelist Project (*.tnp)"
        )

        if not filepath:
            return False

        manuscript_text = self.manuscript_view.get_text()
        success = self.project_manager.save_project_as(filepath, manuscript_text)

        if success:
            self.is_modified = False
            self._update_ui_state()

            # Add to recent projects
            self.settings.add_recent_project(filepath)
            self._update_recent_projects_menu()

            self.statusBar().showMessage("Project saved successfully", 3000)
            return True
        else:
            QMessageBox.critical(
                self,
                "Error",
                "Failed to save project."
            )
            return False

    def close_project(self):
        """Close the current project"""
        if not self._check_unsaved_changes():
            return

        self.project_manager.close_project()
        self.manuscript_view.clear_text()
        self.manuscript_view.clear_analysis()
        self.is_modified = False
        self._update_ui_state()
        self.statusBar().showMessage("Project closed", 2000)

    def _check_unsaved_changes(self) -> bool:
        """
        Check for unsaved changes and ask user

        Returns:
            bool: True to continue, False to cancel
        """
        if self.is_modified and self.project_manager.has_project():
            reply = QMessageBox.question(
                self,
                "Unsaved Changes",
                "Do you want to save changes before continuing?",
                QMessageBox.StandardButton.Save |
                QMessageBox.StandardButton.Discard |
                QMessageBox.StandardButton.Cancel
            )

            if reply == QMessageBox.StandardButton.Save:
                return self.save_project()
            elif reply == QMessageBox.StandardButton.Cancel:
                return False

        return True

    def _on_text_changed(self):
        """Handle manuscript text changes"""
        if not self.is_modified:
            self.is_modified = True
            self._update_ui_state()

    def _update_recent_projects_menu(self):
        """Update the recent projects menu"""
        recent_projects = self.settings.get_recent_projects()
        self.menu_bar.update_recent_projects(recent_projects)

    def _open_recent_project(self, filepath: str):
        """
        Open a recent project

        Args:
            filepath: Path to project file
        """
        # Check for unsaved changes
        if not self._check_unsaved_changes():
            return

        # Check if file exists
        if not os.path.exists(filepath):
            QMessageBox.warning(
                self,
                "File Not Found",
                f"The project file no longer exists:\n{filepath}"
            )
            # Remove from recent projects
            recent = self.settings.get_recent_projects()
            if filepath in recent:
                recent.remove(filepath)
                self.settings.set("recent_projects", recent)
                self._update_recent_projects_menu()
            return

        # Open the project
        project, manuscript_text, characters = self.project_manager.open_project(filepath)

        if project:
            # Load manuscript
            self.manuscript_view.set_text(manuscript_text)

            # Setup images directory for character manager
            images_dir = self.project_manager.get_temp_images_directory()
            if images_dir:
                self.project_manager.character_manager.set_images_directory(images_dir)

            # Update character detail view with manager
            self.character_detail_view.set_character_manager(
                self.project_manager.character_manager
            )

            # Update characters list
            self.characters_list_view.set_images_directory(images_dir)

            self.is_modified = False
            self._update_ui_state()

            # Add to recent projects (moves to top)
            self.settings.add_recent_project(filepath)
            self._update_recent_projects_menu()

            self.statusBar().showMessage(f"Opened: {project.title}", 3000)
        else:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to open project:\n{filepath}"
            )

    # ==================== Character Management ====================

    def _show_characters_list(self):
        """Show the characters list view"""
        characters = self.project_manager.character_manager.get_all_characters()
        images_dir = self.project_manager.get_temp_images_directory()

        self.characters_list_view.load_characters(characters, images_dir)
        self.workspace.show_characters_list()

    def _show_character_detail(self, character_id: str):
        """Show character detail view"""
        self.character_detail_view.load_character(character_id)
        self.workspace.show_character_detail()

    def _add_character(self):
        """Add a new character"""
        if not self.project_manager.has_project():
            QMessageBox.warning(
                self,
                "No Project",
                "Please create or open a project first."
            )
            return

        name, ok = QInputDialog.getText(
            self,
            "New Character",
            "Character Name:"
        )

        if ok and name.strip():
            # Add character
            character = self.project_manager.character_manager.add_character(name.strip())

            # Update tree
            self.project_tree.update_characters(
                self.project_manager.character_manager.get_all_characters()
            )

            # Show character detail
            self._show_character_detail(character.id)

            self.is_modified = True
            self._update_ui_state()
            self.statusBar().showMessage(f"Added character: {name}", 3000)

    def _delete_character(self, character_id: str):
        """Delete a character"""
        success = self.project_manager.character_manager.delete_character(character_id)

        if success:
            # Update tree
            self.project_tree.update_characters(
                self.project_manager.character_manager.get_all_characters()
            )

            # Show characters list
            self._show_characters_list()

            self.is_modified = True
            self._update_ui_state()
            self.statusBar().showMessage("Character deleted", 3000)

    def _on_character_updated(self):
        """Handle character update"""
        # Update tree
        self.project_tree.update_characters(
            self.project_manager.character_manager.get_all_characters()
        )

        self.is_modified = True
        self._update_ui_state()

    def _on_character_deleted(self, character_id: str):
        """Handle character deletion from detail view"""
        self._delete_character(character_id)

    # ==================== Analysis ====================

    def analyze_grammar(self):
        """Start grammar analysis"""
        if not self.project_manager.has_project():
            return

        text = self.manuscript_view.get_text().strip()
        if not text:
            QMessageBox.warning(self, "No Text", "Please write some text first.")
            return

        self._start_analysis(
            AnalysisThread.TYPE_GRAMMAR,
            "Grammar analysis"
        )

    def analyze_repetitions(self):
        """Start repetitions analysis"""
        if not self.project_manager.has_project():
            return

        text = self.manuscript_view.get_text().strip()
        if not text:
            QMessageBox.warning(self, "No Text", "Please write some text first.")
            return

        self._start_analysis(
            AnalysisThread.TYPE_REPETITIONS,
            "Repetitions analysis"
        )

    def analyze_style(self):
        """Start style analysis"""
        if not self.project_manager.has_project():
            return

        text = self.manuscript_view.get_text().strip()
        if not text:
            QMessageBox.warning(self, "No Text", "Please write some text first.")
            return

        self._start_analysis(
            AnalysisThread.TYPE_STYLE,
            "Style analysis"
        )

    def _start_analysis(self, analysis_type: str, analysis_name: str):
        """Start an analysis in background"""
        text = self.manuscript_view.get_text()

        # Show progress
        self.progress.setVisible(True)
        self.progress.setRange(0, 0)
        self.statusBar().showMessage(f"{analysis_name} in progress...")

        # Start thread
        self.analysis_thread = AnalysisThread(text, analysis_type)
        self.analysis_thread.finished.connect(
            lambda result: self._handle_analysis_result(
                result, analysis_type, analysis_name
            )
        )
        self.analysis_thread.start()

    def _handle_analysis_result(self, result: dict, analysis_type: str, analysis_name: str):
        """Handle analysis result"""
        self.progress.setVisible(False)

        # Format result
        if analysis_type == AnalysisThread.TYPE_GRAMMAR:
            formatted_text = self.grammar_analyzer.format_results(result)
            self.manuscript_view.update_grammar_results(formatted_text)

            if result.get('success') and result.get('errors'):
                self.manuscript_view.highlight_errors(result['errors'])

        elif analysis_type == AnalysisThread.TYPE_REPETITIONS:
            formatted_text = self.repetitions_analyzer.format_results(result)
            self.manuscript_view.update_repetitions_results(formatted_text)

        elif analysis_type == AnalysisThread.TYPE_STYLE:
            formatted_text = self.style_analyzer.format_results(result)
            self.manuscript_view.update_style_results(formatted_text)

        # Status message
        if result.get('success'):
            self.statusBar().showMessage(f"{analysis_name} completed", 3000)
        else:
            self.statusBar().showMessage(f"Error in {analysis_name}", 3000)

    # ==================== View Management ====================

    def _undo(self):
        """Undo last action in manuscript editor"""
        if self.workspace.get_current_view_name() == WorkspaceContainer.VIEW_MANUSCRIPT:
            self.manuscript_view.undo()

    def _redo(self):
        """Redo last action in manuscript editor"""
        if self.workspace.get_current_view_name() == WorkspaceContainer.VIEW_MANUSCRIPT:
            self.manuscript_view.redo()

    def _toggle_sidebar(self):
        """Toggle sidebar visibility"""
        visible = self.project_tree.isVisible()
        self.project_tree.setVisible(not visible)

    def _toggle_analysis(self):
        """Toggle analysis panels"""
        self.manuscript_view.toggle_analysis_panels()

    def _show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            "About The Novelist",
            "<h2>The Novelist</h2>"
            "<p>Version 2.0</p>"
            "<p>An AI-powered writing assistant for creative writers.</p>"
            "<p><b>Features:</b></p>"
            "<ul>"
            "<li>Project-based manuscript management</li>"
            "<li>Character database with images</li>"
            "<li>Grammar and style analysis</li>"
            "<li>Word repetition detection</li>"
            "</ul>"
            "<p>Built with PySide6, spaCy, and LanguageTool</p>"
        )

    # ==================== Auto-save ====================

    def _auto_save(self):
        """Automatically save project if modified"""
        # Only save if:
        # 1. A project is open
        # 2. There are unsaved changes
        # 3. Auto-save is enabled
        if not self.project_manager.has_project():
            return

        if not self.is_modified:
            return

        if not self.auto_save_enabled:
            return

        # Save project
        manuscript_text = self.manuscript_view.get_text()
        success = self.project_manager.save_project(manuscript_text)

        if success:
            from datetime import datetime
            self.last_auto_save = datetime.now()
            self.is_modified = False
            self._update_ui_state()

            # Update auto-save indicator
            time_str = self.last_auto_save.strftime("%H:%M")
            self.auto_save_label.setText(f"Auto-saved at {time_str}")
            self.auto_save_label.setVisible(True)

            # Hide the indicator after 5 seconds
            QTimer.singleShot(5000, lambda: self.auto_save_label.setVisible(False))

    def closeEvent(self, event: QCloseEvent):
        """Handle window close"""
        if self._check_unsaved_changes():
            self.project_manager.close_project()
            event.accept()
        else:
            event.ignore()
