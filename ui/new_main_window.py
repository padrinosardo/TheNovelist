"""
The Novelist - Main Application Window (New Version)
"""
from PySide6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QSplitter,
                               QMessageBox, QFileDialog, QInputDialog, QProgressBar, QLabel, QDialog)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QCloseEvent

from ui.components import (MenuBar, ProjectTree, WorkspaceContainer,
                           ManuscriptView, CharactersListView, CharacterDetailView,
                           StatisticsDashboard, ChaptersPreviewWidget, ScenesPreviewWidget,
                           ChapterDetailWidget, WorldbuildingListView, WorldbuildingDetailView)
from ui.views import (LocationListView, LocationDetailView, ResearchListView,
                      ResearchDetailView, TimelineView, SourcesListView,
                      NotesListView, ProjectInfoDetailView)
from ui.dialogs import (TimelineEventDialog, SourceDetailDialog, NoteDetailDialog)
from ui.styles import Stili
from managers.project_manager import ProjectManager
from managers.ai.ai_manager import AIManager
from workers.thread_analysis import AnalysisThread
from analysis.grammar import GrammarAnalyzer
from analysis.repetition import RepetitionAnalyzer
from analysis.style import StyleAnalyzer
from analysis.context_analyzer import ContextAnalyzer
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

        # AI management
        self.ai_manager = AIManager()

        # Analysis
        self.analysis_thread = None
        self.grammar_analyzer = GrammarAnalyzer()
        self.repetitions_analyzer = RepetitionAnalyzer()
        self.style_analyzer = StyleAnalyzer()
        self.context_analyzer = ContextAnalyzer()

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
        self.manuscript_view = ManuscriptView(
            manuscript_manager=self.project_manager.manuscript_structure_manager,
            project_manager=self.project_manager,
            ai_manager=self.ai_manager
        )
        self.characters_list_view = CharactersListView()
        self.character_detail_view = CharacterDetailView(
            character_manager=self.project_manager.character_manager,
            project_manager=self.project_manager,
            ai_manager=self.ai_manager
        )
        self.statistics_dashboard = StatisticsDashboard()
        self.project_info_view = ProjectInfoDetailView()

        # Dynamic container views
        self.location_list_view = LocationListView()
        self.location_detail_view = LocationDetailView(
            location_manager=self.project_manager.location_manager,
            project_manager=self.project_manager,
            ai_manager=self.ai_manager
        )
        self.research_list_view = ResearchListView()
        self.research_detail_view = ResearchDetailView()
        self.timeline_view = TimelineView()
        self.worldbuilding_list_view = WorldbuildingListView()
        self.worldbuilding_detail_view = WorldbuildingDetailView()
        self.sources_list_view = SourcesListView()
        self.notes_list_view = NotesListView()

        # Preview widgets
        self.chapters_preview = ChaptersPreviewWidget()
        self.scenes_preview = ScenesPreviewWidget()
        self.chapter_detail = ChapterDetailWidget()

        self.workspace.add_view(WorkspaceContainer.VIEW_MANUSCRIPT, self.manuscript_view)
        self.workspace.add_view(WorkspaceContainer.VIEW_CHARACTERS_LIST, self.characters_list_view)
        self.workspace.add_view(WorkspaceContainer.VIEW_CHARACTER_DETAIL, self.character_detail_view)
        self.workspace.add_view(WorkspaceContainer.VIEW_STATISTICS, self.statistics_dashboard)
        self.workspace.add_view(WorkspaceContainer.VIEW_PROJECT_INFO, self.project_info_view)

        # Add dynamic container views
        self.workspace.add_view(WorkspaceContainer.VIEW_LOCATIONS, self.location_list_view)
        self.workspace.add_view(WorkspaceContainer.VIEW_RESEARCH, self.research_list_view)
        self.workspace.add_view(WorkspaceContainer.VIEW_TIMELINE, self.timeline_view)
        self.workspace.add_view(WorkspaceContainer.VIEW_WORLDBUILDING, self.worldbuilding_list_view)
        self.workspace.add_view(WorkspaceContainer.VIEW_WORLDBUILDING_DETAIL, self.worldbuilding_detail_view)
        self.workspace.add_view(WorkspaceContainer.VIEW_SOURCES, self.sources_list_view)
        self.workspace.add_view(WorkspaceContainer.VIEW_NOTES, self.notes_list_view)

        # Add preview views
        self.workspace.add_view(WorkspaceContainer.VIEW_CHAPTERS_PREVIEW, self.chapters_preview)
        self.workspace.add_view(WorkspaceContainer.VIEW_SCENES_PREVIEW, self.scenes_preview)
        self.workspace.add_view(WorkspaceContainer.VIEW_CHAPTER_DETAIL, self.chapter_detail)

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

        # Language indicator
        self.language_label = QLabel()
        self.language_label.setStyleSheet("color: #666; font-size: 11px; margin-right: 10px; padding: 2px 6px; background-color: #f0f0f0; border-radius: 3px;")
        self.language_label.setVisible(False)
        self.statusBar().addPermanentWidget(self.language_label)

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
        self.menu_bar.export_project_requested.connect(self.export_project)
        self.menu_bar.close_project_requested.connect(self.close_project)
        self.menu_bar.create_backup_requested.connect(self._create_backup)
        self.menu_bar.restore_backup_requested.connect(self._restore_backup)
        self.menu_bar.exit_requested.connect(self.close)

        # Edit menu
        self.menu_bar.undo_requested.connect(self._undo)
        self.menu_bar.redo_requested.connect(self._redo)
        self.menu_bar.find_requested.connect(self._on_find)
        self.menu_bar.replace_requested.connect(self._on_replace)

        # Manuscript menu
        self.menu_bar.add_chapter_requested.connect(self._add_chapter)
        self.menu_bar.add_scene_requested.connect(self._add_scene_from_menu)
        self.menu_bar.rename_requested.connect(self._rename_from_menu)
        self.menu_bar.delete_requested.connect(self._delete_from_menu)
        self.menu_bar.previous_scene_requested.connect(self._go_to_previous_scene)
        self.menu_bar.next_scene_requested.connect(self._go_to_next_scene)
        self.menu_bar.go_to_scene_requested.connect(self._go_to_scene_dialog)

        # View menu
        self.menu_bar.toggle_sidebar_requested.connect(self._toggle_sidebar)
        self.menu_bar.toggle_analysis_requested.connect(self._toggle_analysis)

        # Tools menu
        self.menu_bar.grammar_check_requested.connect(self.analyze_grammar)
        self.menu_bar.repetitions_check_requested.connect(self.analyze_repetitions)
        self.menu_bar.style_check_requested.connect(self.analyze_style)
        self.menu_bar.ai_settings_requested.connect(self._open_ai_settings)

        # Help menu
        self.menu_bar.view_error_log_requested.connect(self._view_error_log)
        self.menu_bar.report_issue_requested.connect(self._report_issue)
        self.menu_bar.about_requested.connect(self._show_about)

        # Project tree signals
        self.project_tree.manuscript_selected.connect(self._on_manuscript_selected)
        self.project_tree.chapter_selected.connect(self._on_chapter_selected_for_preview)
        self.project_tree.scene_selected.connect(self._on_scene_selected)
        self.project_tree.characters_list_selected.connect(self._show_characters_list)
        self.project_tree.character_selected.connect(self._show_character_detail)
        self.project_tree.statistics_selected.connect(self._show_statistics)
        self.project_tree.project_info_selected.connect(self._show_project_info)

        # Dynamic container selection signals
        self.project_tree.locations_selected.connect(self._show_locations)
        self.project_tree.research_selected.connect(self._show_research)
        self.project_tree.timeline_selected.connect(self._show_timeline)
        self.project_tree.worldbuilding_selected.connect(self._show_worldbuilding)
        self.project_tree.sources_selected.connect(self._show_sources)
        self.project_tree.notes_selected.connect(self._show_notes)

        # Manuscript structure operations
        self.project_tree.add_chapter_requested.connect(self._add_chapter)
        self.project_tree.add_scene_requested.connect(self._add_scene)
        self.project_tree.rename_chapter_requested.connect(self._rename_chapter)
        self.project_tree.rename_scene_requested.connect(self._rename_scene)
        self.project_tree.delete_chapter_requested.connect(self._delete_chapter)
        self.project_tree.delete_scene_requested.connect(self._delete_scene)
        self.project_tree.chapters_reordered.connect(self._on_chapters_reordered)
        self.project_tree.scenes_reordered.connect(self._on_scenes_reordered)

        # Character operations
        self.project_tree.add_character_requested.connect(self._add_character)
        self.project_tree.delete_character_requested.connect(self._delete_character)

        # Dynamic container operations
        self.project_tree.add_location_requested.connect(self._add_location)
        self.project_tree.add_research_note_requested.connect(self._add_research_note)
        self.project_tree.add_timeline_event_requested.connect(self._add_timeline_event)
        self.project_tree.add_source_requested.connect(self._add_source)
        self.project_tree.add_note_requested.connect(self._add_note)

        # Characters list view signals
        self.characters_list_view.character_clicked.connect(self._show_character_detail)
        self.characters_list_view.add_character_requested.connect(self._add_character)

        # Character detail view signals
        self.character_detail_view.back_requested.connect(self._show_characters_list)
        self.character_detail_view.character_updated.connect(self._on_character_updated)
        self.character_detail_view.character_deleted.connect(self._on_character_deleted)

        # Project info view signals
        self.project_info_view.save_requested.connect(self._save_project_info)
        self.project_info_view.cancel_requested.connect(self.workspace.show_manuscript)

        # Statistics dashboard signals
        self.statistics_dashboard.refresh_requested.connect(self._refresh_statistics)
        self.statistics_dashboard.daily_goal_changed.connect(self._set_daily_goal)
        self.statistics_dashboard.weekly_goal_changed.connect(self._set_weekly_goal)

        # Manuscript view signals
        self.manuscript_view.text_changed.connect(self._on_text_changed)
        self.manuscript_view.scene_content_changed.connect(self._on_scene_content_changed)
        self.manuscript_view.previous_scene_requested.connect(self._go_to_previous_scene)
        self.manuscript_view.next_scene_requested.connect(self._go_to_next_scene)

        # Preview widget signals
        self.chapters_preview.chapter_clicked.connect(self._on_chapter_clicked_from_preview)
        self.scenes_preview.scene_clicked.connect(self._on_scene_clicked_from_preview)

        # Chapter detail widget signals
        self.chapter_detail.scene_clicked.connect(self._on_scene_clicked_from_preview)
        self.chapter_detail.back_requested.connect(self._on_chapter_detail_back_requested)
        self.chapter_detail.chapter_updated.connect(self._on_chapter_updated)

        # Location view signals
        self.location_list_view.add_location_requested.connect(self._add_location)
        self.location_list_view.edit_location_requested.connect(self._edit_location)
        self.location_list_view.delete_location_requested.connect(self._delete_location)
        self.location_detail_view.save_requested.connect(self._save_location)
        self.location_detail_view.cancel_requested.connect(self._show_locations)

        # Research view signals
        self.research_list_view.add_research_requested.connect(self._add_research_note)
        self.research_list_view.edit_research_requested.connect(self._edit_research_note)
        self.research_list_view.delete_research_requested.connect(self._delete_research_note)
        self.research_detail_view.save_requested.connect(self._save_research_note)
        self.research_detail_view.cancel_requested.connect(self._show_research)

        # Worldbuilding view signals
        self.worldbuilding_list_view.entry_selected.connect(self._show_worldbuilding_detail)
        self.worldbuilding_list_view.entry_added.connect(self._add_worldbuilding_entry)
        self.worldbuilding_detail_view.entry_saved.connect(self._on_worldbuilding_saved)
        self.worldbuilding_detail_view.entry_deleted.connect(self._on_worldbuilding_deleted)
        self.worldbuilding_detail_view.back_requested.connect(self._show_worldbuilding)

        # Timeline view signals
        self.timeline_view.add_event_requested.connect(self._add_timeline_event)
        self.timeline_view.edit_event_requested.connect(self._edit_timeline_event)
        self.timeline_view.delete_event_requested.connect(self._delete_timeline_event)

        # Sources view signals
        self.sources_list_view.add_source_requested.connect(self._add_source)
        self.sources_list_view.edit_source_requested.connect(self._edit_source)
        self.sources_list_view.delete_source_requested.connect(self._delete_source)

        # Notes view signals
        self.notes_list_view.add_note_requested.connect(self._add_note)
        self.notes_list_view.edit_note_requested.connect(self._edit_note)
        self.notes_list_view.delete_note_requested.connect(self._delete_note)
        self.notes_list_view.toggle_pin_requested.connect(self._toggle_note_pin)

    def _update_window_title(self):
        """Update only the window title (for when content is modified)"""
        if self.project_manager.has_project():
            title = self.project_manager.get_project_title()
            modified = " *" if self.is_modified else ""
            self.setWindowTitle(f"The Novelist - {title}{modified}")
        else:
            self.setWindowTitle("The Novelist")

    def _update_ui_state(self):
        """Update UI based on project state"""
        has_project = self.project_manager.has_project()

        # Update menu bar
        self.menu_bar.set_project_open(has_project)

        # Update window title
        self._update_window_title()

        # Update project tree
        if has_project:
            manuscript_structure = self.project_manager.manuscript_structure_manager.get_structure()
            self.project_tree.load_project(
                self.project_manager.current_project,
                self.project_manager.character_manager.get_all_characters(),
                manuscript_structure
            )
            # Select first scene or current scene
            current_scene = manuscript_structure.current_scene_id
            if current_scene:
                self.project_tree.select_scene(current_scene)
                self._on_scene_selected(current_scene)
            else:
                # Select first scene by default
                all_scenes = manuscript_structure.get_all_scenes()
                if all_scenes:
                    first_scene = all_scenes[0]
                    self.project_tree.select_scene(first_scene.id)
                    self._on_scene_selected(first_scene.id)
        else:
            self.project_tree.clear_project()

        # Update language indicator
        self._update_language_indicator()

    def _update_language_indicator(self):
        """Update the language indicator in status bar"""
        if self.project_manager.has_project():
            language = self.project_manager.current_project.language
            # Map language codes to display names with flags
            language_names = {
                'it': '🇮🇹 IT',
                'en': '🇬🇧 EN',
                'es': '🇪🇸 ES',
                'fr': '🇫🇷 FR',
                'de': '🇩🇪 DE'
            }
            display_name = language_names.get(language, language.upper())
            self.language_label.setText(display_name)
            self.language_label.setVisible(True)

            # Update analyzers with project language
            self._update_analyzers_language(language)
        else:
            self.language_label.setVisible(False)

    def _update_analyzers_language(self, language: str):
        """Update all analyzers to use the specified language"""
        try:
            self.grammar_analyzer.set_language(language)
            self.style_analyzer.set_language(language)
            self.context_analyzer.set_language(language)
            # Update text editor UI language for context menus
            self.manuscript_view.text_editor.set_ui_language(language)
            # Update spell checker language
            self.manuscript_view.set_spell_check_language(language)
        except Exception as e:
            print(f"Warning: Failed to update analyzer language: {e}")

    # ==================== Project Management ====================

    def new_project(self):
        """Create a new project"""
        # Check for unsaved changes
        if not self._check_unsaved_changes():
            return

        # Show new project dialog
        from ui.dialogs.new_project_dialog import NewProjectDialog
        from utils.validators import Validators

        dialog = NewProjectDialog(self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        # Get project data from dialog
        (title, author, language, project_type, genre, target_word_count, tags, use_template,
         ai_provider_name, ai_provider_config) = dialog.get_project_data()

        # Get save location
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Save New Project",
            f"{Validators.sanitize_filename(title)}.tnp",
            "The Novelist Project (*.tnp)"
        )

        if not filepath:
            return

        # Validate filepath
        is_valid, error_msg = Validators.validate_filepath(
            filepath,
            check_writable=True
        )
        if not is_valid:
            QMessageBox.critical(self, "Invalid Save Location", error_msg)
            return

        # Create project with all metadata
        success = self.project_manager.create_new_project(
            title=title,
            author=author,
            filepath=filepath,
            language=language,
            project_type=project_type,
            genre=genre,
            target_word_count=target_word_count,
            tags=tags,
            use_template=use_template,
            ai_provider_name=ai_provider_name,
            ai_provider_config=ai_provider_config
        )

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

            # Start writing session
            self.project_manager.statistics_manager.start_session(0, 0)

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

            # Update spell checker language for opened project
            if project:
                self.manuscript_view.set_spell_check_language(project.language)

            # Add to recent projects
            self.settings.add_recent_project(filepath)
            self._update_recent_projects_menu()

            # Start writing session
            text = self.manuscript_view.get_text()
            word_count = len(text.split())
            char_count = len(text)
            self.project_manager.statistics_manager.start_session(word_count, char_count)

            self.statusBar().showMessage(f"Opened: {project.title}", 3000)
        else:
            # Project failed to open - check if backups are available
            from utils.backup_manager import BackupManager

            project_filename = os.path.basename(filepath)
            project_name = project_filename.rsplit('.', 1)[0]
            backup_manager = BackupManager()
            backups = backup_manager.list_backups(project_name)

            if backups:
                # Offer to restore from backup
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Icon.Warning)
                msg.setWindowTitle("Project Corrupted")
                msg.setText(f"The project file appears to be corrupted:\n{filepath}\n\n"
                           f"Found {len(backups)} backup(s). Would you like to restore from backup?")
                msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                msg.setDefaultButton(QMessageBox.StandardButton.Yes)

                if msg.exec() == QMessageBox.StandardButton.Yes:
                    # Show backup selection dialog
                    self._show_backup_restore_dialog(filepath, backups)
            else:
                QMessageBox.critical(
                    self,
                    "Error Opening Project",
                    f"Failed to open project:\n{filepath}\n\n"
                    "The file may be corrupted and no backups are available."
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

        # Save current scene content first
        self._save_current_scene()

        # Get full manuscript text for statistics
        manuscript_text = self.project_manager.manuscript_structure_manager.get_full_manuscript_text()

        # End current writing session before saving
        if self.project_manager.statistics_manager.is_session_active():
            word_count = len(manuscript_text.split())
            char_count = len(manuscript_text)
            self.project_manager.statistics_manager.end_session(word_count, char_count)

        # Update manuscript statistics
        self.project_manager.statistics_manager.update_manuscript_stats(manuscript_text)

        # Save project
        success = self.project_manager.save_project()

        if success:
            self.is_modified = False
            self._update_ui_state()

            # Start a new session after saving
            word_count = len(manuscript_text.split())
            char_count = len(manuscript_text)
            self.project_manager.statistics_manager.start_session(word_count, char_count)

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

        # Save current scene content first
        self._save_current_scene()

        success = self.project_manager.save_project_as(filepath)

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

    def export_project(self):
        """Export project to PDF, DOCX, or Markdown"""
        if not self.project_manager.has_project():
            QMessageBox.warning(
                self,
                "No Project",
                "Please create or open a project before exporting."
            )
            return

        # Save current scene content first
        self._save_current_scene()

        # Import and show export dialog
        from ui.dialogs.export_dialog import ExportDialog

        dialog = ExportDialog(self.project_manager, self)
        result = dialog.exec()

        if result:
            self.statusBar().showMessage("Project exported successfully", 3000)
        else:
            self.statusBar().showMessage("Export cancelled", 2000)

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

    def _show_backup_restore_dialog(self, corrupted_filepath: str, backups: list):
        """
        Show dialog to select and restore from backup

        Args:
            corrupted_filepath: Path to corrupted project file
            backups: List of backup info dictionaries
        """
        from utils.backup_manager import BackupManager

        # Create selection dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Restore from Backup")
        dialog.setModal(True)
        dialog.resize(600, 400)

        layout = QVBoxLayout(dialog)

        # Info label
        info_label = QLabel(
            f"Select a backup to restore:\n\n"
            f"Corrupted file: {os.path.basename(corrupted_filepath)}"
        )
        layout.addWidget(info_label)

        # Backup list widget
        from PySide6.QtWidgets import QListWidget, QListWidgetItem
        backup_list = QListWidget()

        for backup in backups:
            item_text = (
                f"{backup['date_str']} - {backup['operation']} "
                f"({backup['size_mb']} MB)"
            )
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, backup['path'])
            backup_list.addItem(item)

        layout.addWidget(backup_list)

        # Buttons
        from PySide6.QtWidgets import QDialogButtonBox
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        # Show dialog
        if dialog.exec() == QDialog.DialogCode.Accepted:
            selected_items = backup_list.selectedItems()
            if selected_items:
                backup_path = selected_items[0].data(Qt.ItemDataRole.UserRole)

                # Restore backup
                backup_manager = BackupManager()
                success = backup_manager.restore_backup(backup_path, corrupted_filepath)

                if success:
                    QMessageBox.information(
                        self,
                        "Restore Successful",
                        "Backup restored successfully! Opening project..."
                    )
                    # Try to open the restored project
                    project, manuscript_text, characters = self.project_manager.open_project(corrupted_filepath)
                    if project:
                        # Load the restored project (same code as open_project success case)
                        self.manuscript_view.set_text(manuscript_text)
                        images_dir = self.project_manager.get_temp_images_directory()
                        if images_dir:
                            self.project_manager.character_manager.set_images_directory(images_dir)
                        self.character_detail_view.set_character_manager(
                            self.project_manager.character_manager
                        )
                        self.characters_list_view.set_images_directory(images_dir)
                        self.is_modified = False
                        self._update_ui_state()
                        self.settings.add_recent_project(corrupted_filepath)
                        self._update_recent_projects_menu()
                        text = self.manuscript_view.get_text()
                        word_count = len(text.split())
                        char_count = len(text)
                        self.project_manager.statistics_manager.start_session(word_count, char_count)
                        self.statusBar().showMessage(f"Restored and opened: {project.title}", 3000)
                    else:
                        QMessageBox.warning(
                            self,
                            "Error",
                            "Backup was restored but project still failed to open."
                        )
                else:
                    QMessageBox.critical(
                        self,
                        "Restore Failed",
                        "Failed to restore backup. Please try another backup or contact support."
                    )

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

            # Update spell checker language for opened project
            if project:
                self.manuscript_view.set_spell_check_language(project.language)

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

    def _show_statistics(self):
        """Show statistics dashboard"""
        self._refresh_statistics()
        self.workspace.show_statistics()

    def _show_project_info(self):
        """Show project info detail view"""
        if not self.project_manager.has_project():
            return

        project = self.project_manager.current_project
        self.project_info_view.load_project(project)
        self.workspace.show_project_info()

    def _save_project_info(self, updated_project):
        """
        Save updated project info

        Args:
            updated_project: Updated Project instance
        """
        if not self.project_manager.has_project():
            return

        # Update current project with new data
        self.project_manager.current_project = updated_project

        # Update modified date
        self.project_manager.current_project.update_modified_date()

        # Mark as modified
        self.is_modified = True

        # Save project
        success = self.project_manager.save_project()

        if success:
            # Refresh project tree to show updated info
            characters = self.project_manager.character_manager.get_all_characters()
            manuscript_structure = self.project_manager.manuscript_structure_manager.get_structure()
            self.project_tree.load_project(updated_project, characters, manuscript_structure)

            # Update UI state
            self._update_ui_state()

            # Show confirmation
            QMessageBox.information(
                self,
                "Project Info Updated",
                "Project information has been updated successfully!"
            )

            # Return to manuscript view
            self.workspace.show_manuscript()
        else:
            QMessageBox.critical(
                self,
                "Save Failed",
                "Failed to save project information. Please try again."
            )

    def _refresh_statistics(self):
        """Refresh statistics data"""
        if not self.project_manager.has_project():
            return

        # Update manuscript stats
        text = self.manuscript_view.get_text()
        self.project_manager.statistics_manager.update_manuscript_stats(text)

        # Get stats and update dashboard
        stats = self.project_manager.statistics_manager.get_stats()
        self.statistics_dashboard.update_statistics(stats)

    def _set_daily_goal(self, words: int):
        """Set daily writing goal"""
        self.project_manager.statistics_manager.set_daily_goal(words)
        self._refresh_statistics()
        self.show_status_message(f"Daily goal set to {words:,} words")

    def _set_weekly_goal(self, words: int):
        """Set weekly writing goal"""
        self.project_manager.statistics_manager.set_weekly_goal(words)
        self._refresh_statistics()
        self.show_status_message(f"Weekly goal set to {words:,} words")

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
        self._update_window_title()

    def _on_character_deleted(self, character_id: str):
        """Handle character deletion from detail view"""
        self._delete_character(character_id)

    # ==================== Manuscript Structure ====================

    def _on_scene_selected(self, scene_id: str):
        """Handle scene selection from tree"""
        if not self.project_manager.has_project():
            return

        # Save current scene if editing one
        self._save_current_scene()

        # Get scene and chapter info
        manager = self.project_manager.manuscript_structure_manager
        scene = manager.get_scene(scene_id)
        if not scene:
            return

        chapter = manager.structure.get_chapter_for_scene(scene_id)
        if not chapter:
            return

        # Check if there's previous/next scene
        previous_scene = manager.get_previous_scene(scene_id)
        next_scene = manager.get_next_scene(scene_id)

        # Switch to manuscript view
        self.workspace.show_manuscript()

        # Load scene into editor
        self.manuscript_view.load_scene(
            scene_id=scene.id,
            chapter_title=chapter.title,
            scene_title=scene.title,
            content=scene.content,
            has_previous=previous_scene is not None,
            has_next=next_scene is not None,
            synopsis=scene.synopsis,
            notes=scene.notes
        )

        # Update current scene in structure
        manager.set_current_scene(scene_id)

    def _on_chapter_selected(self, chapter_id: str):
        """Handle chapter selection from tree - load first scene"""
        if not self.project_manager.has_project():
            return

        manager = self.project_manager.manuscript_structure_manager
        first_scene = manager.get_first_scene_in_chapter(chapter_id)

        if first_scene:
            self._on_scene_selected(first_scene.id)
            self.project_tree.select_scene(first_scene.id)

    def _on_manuscript_selected(self):
        """Handle manuscript selection from tree - show chapters preview"""
        if not self.project_manager.has_project():
            return

        manager = self.project_manager.manuscript_structure_manager
        chapters = manager.get_structure().chapters

        # Load chapters into preview
        self.chapters_preview.load_chapters(chapters)

        # Show chapters preview
        self.workspace.show_view(WorkspaceContainer.VIEW_CHAPTERS_PREVIEW)

    def _on_chapter_selected_for_preview(self, chapter_id: str):
        """Handle chapter selection from tree - show chapter detail"""
        if not self.project_manager.has_project():
            return

        manager = self.project_manager.manuscript_structure_manager
        chapter = manager.get_chapter(chapter_id)

        if chapter:
            # Load chapter into detail view
            self.chapter_detail.load_chapter(chapter)

            # Show chapter detail
            self.workspace.show_view(WorkspaceContainer.VIEW_CHAPTER_DETAIL)

    def _on_chapter_clicked_from_preview(self, chapter_id: str):
        """Handle chapter click from chapters preview - show chapter detail"""
        if not self.project_manager.has_project():
            return

        manager = self.project_manager.manuscript_structure_manager
        chapter = manager.get_chapter(chapter_id)

        if chapter:
            # Load chapter into detail view
            self.chapter_detail.load_chapter(chapter)

            # Show chapter detail
            self.workspace.show_view(WorkspaceContainer.VIEW_CHAPTER_DETAIL)

            # Update tree selection
            self.project_tree.select_chapter(chapter_id)

    def _on_scene_clicked_from_preview(self, scene_id: str):
        """Handle scene click from scenes preview - open scene in editor"""
        if not self.project_manager.has_project():
            return

        # Load scene in editor
        self._on_scene_selected(scene_id)

        # Update tree selection
        self.project_tree.select_scene(scene_id)

    def _on_chapters_reordered(self, chapter_ids: list):
        """Handle chapters reordered from project tree"""
        if not self.project_manager.has_project():
            return

        # Reorder chapters in the structure
        manager = self.project_manager.manuscript_structure_manager
        success = manager.reorder_chapters(chapter_ids)

        if success:
            # 1. Refresh project tree
            self.project_tree.update_manuscript_structure(manager.get_structure())

            # 2. Refresh chapters preview if visible
            if self.workspace.get_current_view_name() == WorkspaceContainer.VIEW_CHAPTERS_PREVIEW:
                chapters = manager.get_structure().chapters
                self.chapters_preview.load_chapters(chapters)

            # 3. Mark project as modified
            self.is_modified = True

    def _on_scenes_reordered(self, chapter_id: str, scene_ids: list):
        """Handle scenes reordered from project tree"""
        if not self.project_manager.has_project():
            return

        manager = self.project_manager.manuscript_structure_manager
        success = manager.reorder_scenes(chapter_id, scene_ids)

        if success:
            # 1. Refresh project tree
            self.project_tree.update_manuscript_structure(manager.get_structure())

            # 2. Refresh scenes preview if visible
            if self.workspace.get_current_view_name() == WorkspaceContainer.VIEW_SCENES_PREVIEW:
                chapter = manager.get_chapter(chapter_id)
                if chapter:
                    self.scenes_preview.load_scenes(chapter.scenes, chapter.title)

            # 3. Refresh chapter detail if visible and showing this chapter
            if self.workspace.get_current_view_name() == WorkspaceContainer.VIEW_CHAPTER_DETAIL:
                chapter = manager.get_chapter(chapter_id)
                if chapter:
                    self.chapter_detail.load_chapter(chapter)

            # 4. Mark project as modified
            self.is_modified = True

    def _on_chapter_detail_back_requested(self):
        """Handle back button click from chapter detail - show chapters preview"""
        if not self.project_manager.has_project():
            return

        # Save current chapter data before going back
        self.chapter_detail.save_current_data()

        # Show chapters preview
        manager = self.project_manager.manuscript_structure_manager
        chapters = manager.get_structure().chapters
        self.chapters_preview.load_chapters(chapters)
        self.workspace.show_view(WorkspaceContainer.VIEW_CHAPTERS_PREVIEW)

    def _on_chapter_updated(self, chapter_id: str):
        """Handle chapter update (synopsis/notes changed)"""
        if not self.project_manager.has_project():
            return

        # Mark as modified
        if not self.is_modified:
            self.is_modified = True
            self._update_window_title()

    def _on_scene_content_changed(self, scene_id: str, content: str):
        """Handle scene content change"""
        if not self.project_manager.has_project():
            return

        # Update scene content in manager
        manager = self.project_manager.manuscript_structure_manager
        manager.update_scene_content(scene_id, content)

        # Mark as modified
        if not self.is_modified:
            self.is_modified = True
            self._update_ui_state()

    def _save_current_scene(self):
        """Save current scene content before switching"""
        scene_data = self.manuscript_view.save_current_scene_content()
        if scene_data and self.project_manager.has_project():
            scene_id, content = scene_data
            manager = self.project_manager.manuscript_structure_manager
            manager.update_scene_content(scene_id, content)

    def _go_to_previous_scene(self):
        """Navigate to previous scene"""
        if not self.project_manager.has_project():
            return

        current_scene_id = self.manuscript_view.get_current_scene_id()
        if not current_scene_id:
            return

        manager = self.project_manager.manuscript_structure_manager
        previous_scene = manager.get_previous_scene(current_scene_id)

        if previous_scene:
            self.project_tree.select_scene(previous_scene.id)
            self._on_scene_selected(previous_scene.id)

    def _go_to_next_scene(self):
        """Navigate to next scene"""
        if not self.project_manager.has_project():
            return

        current_scene_id = self.manuscript_view.get_current_scene_id()
        if not current_scene_id:
            return

        manager = self.project_manager.manuscript_structure_manager
        next_scene = manager.get_next_scene(current_scene_id)

        if next_scene:
            self.project_tree.select_scene(next_scene.id)
            self._on_scene_selected(next_scene.id)

    def _add_chapter(self):
        """Add a new chapter"""
        if not self.project_manager.has_project():
            return

        from ui.components import ChapterDialog

        dialog = ChapterDialog(self, mode="add")
        if dialog.exec() == QDialog.DialogCode.Accepted:
            title = dialog.get_title()

            # Add chapter through manager
            manager = self.project_manager.manuscript_structure_manager
            new_chapter = manager.add_chapter(title)

            # Update tree
            self.project_tree.update_manuscript_structure(manager.get_structure())

            # Select the first scene of the new chapter
            if new_chapter.scenes:
                self.project_tree.select_scene(new_chapter.scenes[0].id)
                self._on_scene_selected(new_chapter.scenes[0].id)

            self.is_modified = True
            self.statusBar().showMessage(f"Added chapter: {title}", 3000)

    def _add_scene(self, chapter_id: str):
        """Add a new scene to a chapter"""
        if not self.project_manager.has_project():
            return

        from ui.components import SceneDialog

        dialog = SceneDialog(self, mode="add")
        if dialog.exec() == QDialog.DialogCode.Accepted:
            title = dialog.get_title()

            # Add scene through manager
            manager = self.project_manager.manuscript_structure_manager
            new_scene = manager.add_scene(chapter_id, title)

            if new_scene:
                # Update tree
                self.project_tree.update_manuscript_structure(manager.get_structure())

                # Select the new scene
                self.project_tree.select_scene(new_scene.id)
                self._on_scene_selected(new_scene.id)

                self.is_modified = True
                self.statusBar().showMessage(f"Added scene: {title}", 3000)

    def _rename_chapter(self, chapter_id: str):
        """Rename a chapter"""
        if not self.project_manager.has_project():
            return

        from ui.components import ChapterDialog

        manager = self.project_manager.manuscript_structure_manager
        chapter = manager.get_chapter(chapter_id)
        if not chapter:
            return

        dialog = ChapterDialog(self, current_title=chapter.title, mode="rename")
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_title = dialog.get_title()

            # Rename through manager
            manager.rename_chapter(chapter_id, new_title)

            # Update tree
            self.project_tree.update_manuscript_structure(manager.get_structure())

            self.is_modified = True
            self.statusBar().showMessage(f"Renamed chapter to: {new_title}", 3000)

    def _rename_scene(self, scene_id: str):
        """Rename a scene"""
        if not self.project_manager.has_project():
            return

        from ui.components import SceneDialog

        manager = self.project_manager.manuscript_structure_manager
        scene = manager.get_scene(scene_id)
        if not scene:
            return

        dialog = SceneDialog(self, current_title=scene.title, mode="rename")
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_title = dialog.get_title()

            # Rename through manager
            manager.rename_scene(scene_id, new_title)

            # Update tree
            self.project_tree.update_manuscript_structure(manager.get_structure())

            # Update breadcrumb if this is the current scene
            if self.manuscript_view.get_current_scene_id() == scene_id:
                chapter = manager.structure.get_chapter_for_scene(scene_id)
                if chapter:
                    self.manuscript_view.load_scene(
                        scene_id=scene.id,
                        chapter_title=chapter.title,
                        scene_title=new_title,
                        content=scene.content,
                        has_previous=manager.get_previous_scene(scene_id) is not None,
                        has_next=manager.get_next_scene(scene_id) is not None,
                        synopsis=scene.synopsis,
                        notes=scene.notes
                    )

            self.is_modified = True
            self.statusBar().showMessage(f"Renamed scene to: {new_title}", 3000)

    def _delete_chapter(self, chapter_id: str):
        """Delete a chapter"""
        if not self.project_manager.has_project():
            return

        from ui.components import show_delete_chapter_confirmation

        manager = self.project_manager.manuscript_structure_manager
        chapter = manager.get_chapter(chapter_id)
        if not chapter:
            return

        # Confirm deletion
        if not show_delete_chapter_confirmation(self, chapter.title, len(chapter.scenes)):
            return

        # Delete through manager
        success = manager.delete_chapter(chapter_id)

        if success:
            # Update tree
            self.project_tree.update_manuscript_structure(manager.get_structure())

            # If we deleted the current scene's chapter, clear editor
            current_scene_id = self.manuscript_view.get_current_scene_id()
            if current_scene_id and chapter.get_scene(current_scene_id):
                self.manuscript_view.clear_text()

                # Select first available scene
                all_scenes = manager.get_structure().get_all_scenes()
                if all_scenes:
                    self.project_tree.select_scene(all_scenes[0].id)
                    self._on_scene_selected(all_scenes[0].id)

            self.is_modified = True
            self.statusBar().showMessage(f"Deleted chapter: {chapter.title}", 3000)

    def _delete_scene(self, scene_id: str):
        """Delete a scene"""
        if not self.project_manager.has_project():
            return

        from ui.components import show_delete_scene_confirmation

        manager = self.project_manager.manuscript_structure_manager
        scene = manager.get_scene(scene_id)
        if not scene:
            return

        # Confirm deletion
        if not show_delete_scene_confirmation(self, scene.title, scene.word_count):
            return

        # Get the chapter before deletion (for finding next scene)
        chapter = manager.structure.get_chapter_for_scene(scene_id)
        if not chapter:
            return

        # Delete through manager
        success = manager.delete_scene(scene_id)

        if success:
            # Update tree
            self.project_tree.update_manuscript_structure(manager.get_structure())

            # If we deleted the current scene, load another scene
            current_scene_id = self.manuscript_view.get_current_scene_id()
            if current_scene_id == scene_id:
                # Try to load first scene in same chapter, or first available scene
                first_in_chapter = manager.get_first_scene_in_chapter(chapter.id)
                if first_in_chapter:
                    self.project_tree.select_scene(first_in_chapter.id)
                    self._on_scene_selected(first_in_chapter.id)
                else:
                    # Chapter is empty (shouldn't happen), load first available scene
                    all_scenes = manager.get_structure().get_all_scenes()
                    if all_scenes:
                        self.project_tree.select_scene(all_scenes[0].id)
                        self._on_scene_selected(all_scenes[0].id)

            self.is_modified = True
            self.statusBar().showMessage(f"Deleted scene: {scene.title}", 3000)

    def _add_scene_from_menu(self):
        """Add scene from menu - adds to current chapter or prompts to select"""
        if not self.project_manager.has_project():
            return

        manager = self.project_manager.manuscript_structure_manager

        # Try to get current scene to determine chapter
        current_scene_id = self.manuscript_view.get_current_scene_id()
        chapter_id = None

        if current_scene_id:
            # Get chapter for current scene
            chapter = manager.structure.get_chapter_for_scene(current_scene_id)
            if chapter:
                chapter_id = chapter.id

        # If no chapter determined, use first chapter or create one
        if not chapter_id:
            chapters = manager.get_structure().chapters
            if chapters:
                chapter_id = chapters[0].id
            else:
                # No chapters exist, create one first
                QMessageBox.information(
                    self,
                    "No Chapters",
                    "Please create a chapter first before adding scenes."
                )
                self._add_chapter()
                return

        # Now add scene to the chapter
        self._add_scene(chapter_id)

    def _rename_from_menu(self):
        """Rename from menu - renames currently selected item in tree"""
        if not self.project_manager.has_project():
            return

        # Get current selection from tree
        selected_items = self.project_tree.selectedItems()
        if not selected_items:
            QMessageBox.information(
                self,
                "No Selection",
                "Please select a chapter or scene to rename."
            )
            return

        item = selected_items[0]
        item_type = item.data(0, Qt.ItemDataRole.UserRole)

        if isinstance(item_type, str) and item_type.startswith("chapter:"):
            chapter_id = item_type.split(":", 1)[1]
            self._rename_chapter(chapter_id)
        elif isinstance(item_type, str) and item_type.startswith("scene:"):
            scene_id = item_type.split(":", 1)[1]
            self._rename_scene(scene_id)
        else:
            QMessageBox.information(
                self,
                "Invalid Selection",
                "Please select a chapter or scene to rename."
            )

    def _delete_from_menu(self):
        """Delete from menu - deletes currently selected item in tree"""
        if not self.project_manager.has_project():
            return

        # Get current selection from tree
        selected_items = self.project_tree.selectedItems()
        if not selected_items:
            QMessageBox.information(
                self,
                "No Selection",
                "Please select a chapter or scene to delete."
            )
            return

        item = selected_items[0]
        item_type = item.data(0, Qt.ItemDataRole.UserRole)

        if isinstance(item_type, str) and item_type.startswith("chapter:"):
            chapter_id = item_type.split(":", 1)[1]
            self._delete_chapter(chapter_id)
        elif isinstance(item_type, str) and item_type.startswith("scene:"):
            scene_id = item_type.split(":", 1)[1]
            self._delete_scene(scene_id)
        else:
            QMessageBox.information(
                self,
                "Invalid Selection",
                "Please select a chapter or scene to delete."
            )

    def _go_to_scene_dialog(self):
        """Show quick scene switcher dialog"""
        if not self.project_manager.has_project():
            return

        from ui.components import QuickSceneDialog

        # Get current manuscript structure and scene
        manager = self.project_manager.manuscript_structure_manager
        current_scene_id = self.manuscript_view.get_current_scene_id()

        # Create and show dialog
        dialog = QuickSceneDialog(
            manager.get_structure(),
            current_scene_id,
            self
        )

        # Connect to scene selection
        dialog.scene_selected.connect(self._on_scene_selected)
        dialog.scene_selected.connect(lambda scene_id: self.project_tree.select_scene(scene_id))

        dialog.exec()

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

        # Get project type for context-aware analysis
        project_type = None
        if self.project_manager.current_project:
            project_type = self.project_manager.current_project.project_type

        # Show progress
        self.progress.setVisible(True)
        self.progress.setRange(0, 0)
        self.statusBar().showMessage(f"{analysis_name} in progress...")

        # Start thread
        self.analysis_thread = AnalysisThread(text, analysis_type, project_type)
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

    def _on_find(self):
        """Handle Find request (Ctrl+F)"""
        if self.workspace.get_current_view_name() == WorkspaceContainer.VIEW_MANUSCRIPT:
            self.manuscript_view.show_find_dialog()
        else:
            self.show_status_message("Find is only available in manuscript view")

    def _on_replace(self):
        """Handle Replace request (Ctrl+H)"""
        if self.workspace.get_current_view_name() == WorkspaceContainer.VIEW_MANUSCRIPT:
            self.manuscript_view.show_replace_dialog()
        else:
            self.show_status_message("Replace is only available in manuscript view")

    def _toggle_sidebar(self):
        """Toggle sidebar visibility"""
        visible = self.project_tree.isVisible()
        self.project_tree.setVisible(not visible)

    def _toggle_analysis(self):
        """Toggle analysis panels"""
        self.manuscript_view.toggle_analysis_panels()

    def _create_backup(self):
        """Create a manual backup of the current project"""
        if not self.project_manager.has_project():
            QMessageBox.warning(
                self,
                "No Project",
                "Please open a project first."
            )
            return

        from utils.backup_manager import BackupManager

        backup_path = BackupManager().create_backup(
            self.project_manager.current_filepath,
            "manual"
        )

        if backup_path:
            QMessageBox.information(
                self,
                "Backup Created",
                f"Backup created successfully:\n\n{os.path.basename(backup_path)}"
            )
        else:
            QMessageBox.critical(
                self,
                "Backup Failed",
                "Failed to create backup. Check the error log for details."
            )

    def _restore_backup(self):
        """Restore a project from backup"""
        from utils.backup_manager import BackupManager
        from PySide6.QtWidgets import QListWidget, QListWidgetItem, QDialog, QVBoxLayout, QLabel, QDialogButtonBox

        # First, ask user to select a project (or use current one)
        if self.project_manager.has_project():
            reply = QMessageBox.question(
                self,
                "Restore Backup",
                "Do you want to restore the current project from backup?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                project_filepath = self.project_manager.current_filepath
            else:
                # Ask for project file
                project_filepath, _ = QFileDialog.getOpenFileName(
                    self,
                    "Select Project to Restore",
                    "",
                    "The Novelist Project (*.tnp)"
                )
                if not project_filepath:
                    return
        else:
            # No project open, ask for project file
            project_filepath, _ = QFileDialog.getOpenFileName(
                self,
                "Select Project to Restore",
                "",
                "The Novelist Project (*.tnp)"
            )
            if not project_filepath:
                return

        # Get project name and list backups
        project_filename = os.path.basename(project_filepath)
        project_name = project_filename.rsplit('.', 1)[0]
        backup_manager = BackupManager()
        backups = backup_manager.list_backups(project_name)

        if not backups:
            QMessageBox.information(
                self,
                "No Backups",
                f"No backups found for project: {project_name}"
            )
            return

        # Show backup selection dialog
        self._show_backup_restore_dialog(project_filepath, backups)

    def _view_error_log(self):
        """Open the error log file in the system's default text editor"""
        from utils.logger import AppLogger
        import subprocess
        import platform

        log_file = AppLogger.get_log_file_path()

        if not os.path.exists(log_file):
            QMessageBox.information(
                self,
                "No Log File",
                "No error log file found yet. The log file will be created when errors occur."
            )
            return

        try:
            # Open log file with system default application
            if platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', log_file])
            elif platform.system() == 'Windows':
                os.startfile(log_file)
            else:  # Linux
                subprocess.run(['xdg-open', log_file])

        except Exception as e:
            # If opening fails, show the path instead
            QMessageBox.information(
                self,
                "Error Log Location",
                f"Error log file location:\n\n{log_file}\n\n"
                f"(Could not open automatically: {str(e)})"
            )

    def _report_issue(self):
        """Show dialog for reporting issues"""
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setWindowTitle("Report Issue")
        msg.setText("To report an issue or bug:")
        msg.setInformativeText(
            "1. Check the error log (Help → View Error Log)\n"
            "2. Prepare a description of the issue\n"
            "3. Note the steps to reproduce the problem\n"
            "4. Contact support with this information\n\n"
            "Thank you for helping improve The Novelist!"
        )
        msg.exec()

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

    def _open_ai_settings(self):
        """Open AI Settings dialog"""
        from ui.dialogs.ai_settings_dialog import AISettingsDialog
        from managers.ai import AIManager

        ai_manager = AIManager()
        dialog = AISettingsDialog(ai_manager, self)
        dialog.exec()

    # ==================== Dynamic Containers ====================

    def _show_locations(self):
        """Show locations list view"""
        if not self.project_manager.has_project():
            return

        locations = self.project_manager.location_manager.get_all_locations()
        self.location_list_view.load_locations(locations)
        self.workspace.show_view(WorkspaceContainer.VIEW_LOCATIONS)

    def _add_location(self):
        """Add a new location"""
        if not self.project_manager.has_project():
            QMessageBox.warning(self, "No Project", "Please create or open a project first.")
            return

        # Load context data
        all_locations = self.project_manager.location_manager.get_all_locations()
        all_characters = self.project_manager.character_manager.get_all_characters()
        self.location_detail_view.load_context(all_locations, all_characters)
        self.location_detail_view.clear_form()

        self.workspace.add_view("location_detail", self.location_detail_view)
        self.workspace.show_view("location_detail")

    def _edit_location(self, location_id: str):
        """Edit an existing location"""
        location = self.project_manager.location_manager.get_location(location_id)
        if not location:
            return

        # Load context data
        all_locations = self.project_manager.location_manager.get_all_locations()
        all_characters = self.project_manager.character_manager.get_all_characters()
        self.location_detail_view.load_context(all_locations, all_characters)
        self.location_detail_view.load_location(location)

        self.workspace.add_view("location_detail", self.location_detail_view)
        self.workspace.show_view("location_detail")

    def _save_location(self, location):
        """Save a location"""
        # Check if location exists in manager
        existing = self.project_manager.location_manager.get_location(location.id)

        if existing:
            # Update existing
            self.project_manager.location_manager.update_location(location)
        else:
            # Add new
            self.project_manager.location_manager.add_location_object(location)

        self.is_modified = True
        self._update_window_title()
        self._show_locations()
        self.statusBar().showMessage(f"Location saved: {location.name}", 3000)

    def _delete_location(self, location_id: str):
        """Delete a location"""
        success = self.project_manager.location_manager.delete_location(location_id)
        if success:
            self._show_locations()
            self.is_modified = True
            self._update_window_title()
            self.statusBar().showMessage("Location deleted", 3000)

    def _show_research(self):
        """Show research notes list view"""
        if not self.project_manager.has_project():
            return

        notes = self.project_manager.research_manager.get_all_research_notes()
        self.research_list_view.load_research_notes(notes)
        self.workspace.show_view(WorkspaceContainer.VIEW_RESEARCH)

    def _add_research_note(self):
        """Add a new research note"""
        if not self.project_manager.has_project():
            QMessageBox.warning(self, "No Project", "Please create or open a project first.")
            return

        # Load categories
        notes = self.project_manager.research_manager.get_all_research_notes()
        categories = list(set(n.category for n in notes if n.category))
        self.research_detail_view.load_categories(categories)
        self.research_detail_view.clear_form()

        self.workspace.add_view("research_detail", self.research_detail_view)
        self.workspace.show_view("research_detail")

    def _edit_research_note(self, research_id: str):
        """Edit an existing research note"""
        note = self.project_manager.research_manager.get_research_note(research_id)
        if not note:
            return

        # Load categories
        notes = self.project_manager.research_manager.get_all_research_notes()
        categories = list(set(n.category for n in notes if n.category))
        self.research_detail_view.load_categories(categories)
        self.research_detail_view.load_research_note(note)

        self.workspace.add_view("research_detail", self.research_detail_view)
        self.workspace.show_view("research_detail")

    def _save_research_note(self, note):
        """Save a research note"""
        # Check if note exists in manager
        existing = self.project_manager.research_manager.get_research_note(note.id)

        if existing:
            # Update existing
            self.project_manager.research_manager.update_research_note(note)
        else:
            # Add new
            self.project_manager.research_manager.add_research_note_object(note)

        self.is_modified = True
        self._update_window_title()
        self._show_research()
        self.statusBar().showMessage(f"Research note saved: {note.title}", 3000)

    def _delete_research_note(self, research_id: str):
        """Delete a research note"""
        success = self.project_manager.research_manager.delete_research_note(research_id)
        if success:
            self._show_research()
            self.is_modified = True
            self._update_window_title()
            self.statusBar().showMessage("Research note deleted", 3000)

    def _show_timeline(self):
        """Show timeline view"""
        if not self.project_manager.has_project():
            return

        events = self.project_manager.timeline_manager.get_all_timeline_events()
        characters = self.project_manager.character_manager.get_all_characters()
        locations = self.project_manager.location_manager.get_all_locations()
        self.timeline_view.load_events(events, characters, locations)
        self.workspace.show_view(WorkspaceContainer.VIEW_TIMELINE)

    def _add_timeline_event(self):
        """Add a new timeline event"""
        if not self.project_manager.has_project():
            QMessageBox.warning(self, "No Project", "Please create or open a project first.")
            return

        # Create dialog
        dialog = TimelineEventDialog(self)

        # Load context
        characters = self.project_manager.character_manager.get_all_characters()
        locations = self.project_manager.location_manager.get_all_locations()
        dialog.load_context(characters, locations)
        dialog.clear_form()

        if dialog.exec() == QDialog.DialogCode.Accepted:
            event = dialog.get_event()
            self.project_manager.timeline_manager.add_timeline_event_object(event)

            self.is_modified = True
            self._update_window_title()
            self._show_timeline()
            self.statusBar().showMessage(f"Timeline event added: {event.title}", 3000)

    def _edit_timeline_event(self, event_id: str):
        """Edit an existing timeline event"""
        event = self.project_manager.timeline_manager.get_timeline_event(event_id)
        if not event:
            return

        # Create dialog
        dialog = TimelineEventDialog(self)

        # Load context
        characters = self.project_manager.character_manager.get_all_characters()
        locations = self.project_manager.location_manager.get_all_locations()
        dialog.load_context(characters, locations)
        dialog.load_event(event)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            updated_event = dialog.get_event()
            self.project_manager.timeline_manager.update_timeline_event(updated_event)

            self.is_modified = True
            self._update_window_title()
            self._show_timeline()
            self.statusBar().showMessage(f"Timeline event updated: {updated_event.title}", 3000)

    def _delete_timeline_event(self, event_id: str):
        """Delete a timeline event"""
        success = self.project_manager.timeline_manager.delete_timeline_event(event_id)
        if success:
            self._show_timeline()
            self.is_modified = True
            self._update_window_title()
            self.statusBar().showMessage("Timeline event deleted", 3000)

    def _show_worldbuilding(self):
        """Show worldbuilding list view"""
        if not self.project_manager.has_project():
            return

        self.worldbuilding_list_view.load_worldbuilding(
            self.project_manager.container_manager,
            self.project_manager.worldbuilding_manager
        )
        self.workspace.show_view(WorkspaceContainer.VIEW_WORLDBUILDING)

    def _show_worldbuilding_detail(self, entry_id: str):
        """Show worldbuilding detail view for editing"""
        if not self.project_manager.has_project():
            return

        self.worldbuilding_detail_view.set_managers(
            self.project_manager.container_manager,
            self.project_manager.worldbuilding_manager
        )
        self.worldbuilding_detail_view.load_entry(entry_id)
        self.workspace.show_view(WorkspaceContainer.VIEW_WORLDBUILDING_DETAIL)

    def _add_worldbuilding_entry(self):
        """Add a new worldbuilding entry"""
        if not self.project_manager.has_project():
            QMessageBox.warning(self, "No Project", "Please create or open a project first.")
            return

        self.worldbuilding_detail_view.set_managers(
            self.project_manager.container_manager,
            self.project_manager.worldbuilding_manager
        )
        self.worldbuilding_detail_view.new_entry()
        self.workspace.show_view(WorkspaceContainer.VIEW_WORLDBUILDING_DETAIL)

    def _on_worldbuilding_saved(self):
        """Handle worldbuilding entry saved"""
        self._show_worldbuilding()
        self.is_modified = True
        self._update_window_title()
        self.statusBar().showMessage("Worldbuilding entry saved", 3000)

    def _on_worldbuilding_deleted(self, entry_id: str):
        """Handle worldbuilding entry deleted"""
        self._show_worldbuilding()
        self.is_modified = True
        self._update_window_title()
        self.statusBar().showMessage("Worldbuilding entry deleted", 3000)

    def _show_sources(self):
        """Show sources list view"""
        if not self.project_manager.has_project():
            return

        sources = self.project_manager.source_manager.get_all_sources()
        self.sources_list_view.load_sources(sources)
        self.workspace.show_view(WorkspaceContainer.VIEW_SOURCES)

    def _add_source(self):
        """Add a new source"""
        if not self.project_manager.has_project():
            QMessageBox.warning(self, "No Project", "Please create or open a project first.")
            return

        # Create dialog
        dialog = SourceDetailDialog(self)
        dialog.clear_form()

        if dialog.exec() == QDialog.DialogCode.Accepted:
            source = dialog.get_source()
            self.project_manager.source_manager.add_source_object(source)

            self.is_modified = True
            self._update_window_title()
            self._show_sources()
            self.statusBar().showMessage(f"Source added: {source.title}", 3000)

    def _edit_source(self, source_id: str):
        """Edit an existing source"""
        source = self.project_manager.source_manager.get_source(source_id)
        if not source:
            return

        # Create dialog
        dialog = SourceDetailDialog(self)
        dialog.load_source(source)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            updated_source = dialog.get_source()
            self.project_manager.source_manager.update_source(updated_source)

            self.is_modified = True
            self._update_window_title()
            self._show_sources()
            self.statusBar().showMessage(f"Source updated: {updated_source.title}", 3000)

    def _delete_source(self, source_id: str):
        """Delete a source"""
        success = self.project_manager.source_manager.delete_source(source_id)
        if success:
            self._show_sources()
            self.is_modified = True
            self._update_window_title()
            self.statusBar().showMessage("Source deleted", 3000)

    def _show_notes(self):
        """Show notes list view"""
        if not self.project_manager.has_project():
            return

        notes = self.project_manager.note_manager.get_all_notes()
        self.notes_list_view.load_notes(notes)
        self.workspace.show_view(WorkspaceContainer.VIEW_NOTES)

    def _add_note(self):
        """Add a new note"""
        if not self.project_manager.has_project():
            QMessageBox.warning(self, "No Project", "Please create or open a project first.")
            return

        # Create dialog
        dialog = NoteDetailDialog(
            note_manager=self.project_manager.note_manager,
            project_manager=self.project_manager,
            ai_manager=self.ai_manager,
            parent=self
        )

        # Load context
        characters = self.project_manager.character_manager.get_all_characters()
        locations = self.project_manager.location_manager.get_all_locations()

        # Get scenes from manuscript structure
        scenes = []
        structure = self.project_manager.manuscript_structure_manager.get_structure()
        for chapter in structure.chapters:
            for scene in chapter.scenes:
                scenes.append((scene.id, f"{chapter.title} - {scene.title}"))

        dialog.load_context(characters, locations, scenes)
        dialog.clear_form()

        if dialog.exec() == QDialog.DialogCode.Accepted:
            note = dialog.get_note()
            self.project_manager.note_manager.add_note_object(note)

            self.is_modified = True
            self._update_window_title()
            self._show_notes()
            self.statusBar().showMessage(f"Note added: {note.title}", 3000)

    def _edit_note(self, note_id: str):
        """Edit an existing note"""
        note = self.project_manager.note_manager.get_note(note_id)
        if not note:
            return

        # Create dialog
        dialog = NoteDetailDialog(
            note_manager=self.project_manager.note_manager,
            project_manager=self.project_manager,
            ai_manager=self.ai_manager,
            parent=self
        )

        # Load context
        characters = self.project_manager.character_manager.get_all_characters()
        locations = self.project_manager.location_manager.get_all_locations()

        # Get scenes from manuscript structure
        scenes = []
        structure = self.project_manager.manuscript_structure_manager.get_structure()
        for chapter in structure.chapters:
            for scene in chapter.scenes:
                scenes.append((scene.id, f"{chapter.title} - {scene.title}"))

        dialog.load_context(characters, locations, scenes)
        dialog.load_note(note)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            updated_note = dialog.get_note()
            self.project_manager.note_manager.update_note(updated_note)

            self.is_modified = True
            self._update_window_title()
            self._show_notes()
            self.statusBar().showMessage(f"Note updated: {updated_note.title}", 3000)

    def _delete_note(self, note_id: str):
        """Delete a note"""
        success = self.project_manager.note_manager.delete_note(note_id)
        if success:
            self._show_notes()
            self.is_modified = True
            self._update_window_title()
            self.statusBar().showMessage("Note deleted", 3000)

    def _toggle_note_pin(self, note_id: str):
        """Toggle note pin status"""
        success = self.project_manager.note_manager.toggle_pin(note_id)
        if success:
            self._show_notes()
            self.is_modified = True
            self._update_window_title()

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

        # Save project (manuscript is saved automatically via manuscript_structure_manager)
        success = self.project_manager.save_project()

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
