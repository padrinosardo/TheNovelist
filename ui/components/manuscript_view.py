"""
Manuscript View - Text editor with analysis panels
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
                               QGroupBox, QLabel, QPushButton, QTextEdit)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QTextCursor
from ui.components.rich_text_editor import RichTextEditor as TextEditor
from ui.components.unified_text_editor import UnifiedTextEditor
from ui.pannels import ResultsPanel
from ui.styles import Stili
from ui.components.find_replace_dialog import FindReplaceDialog
from ui.components.context_sidebar import ContextSidebar
from ui.components.ai_chat_widget import AIChatWidget
from typing import Optional
from utils.logger import logger


class ManuscriptView(QWidget):
    """
    View for editing the main manuscript text
    Layout: Editor (left) + Analysis Panels (right, optional)
    Supports single-scene editing with navigation
    """

    # Signals
    text_changed = Signal()
    scene_content_changed = Signal(str, str)  # scene_id, content
    previous_scene_requested = Signal()
    next_scene_requested = Signal()

    def __init__(self, manuscript_manager=None, project_manager=None, ai_manager=None, parent=None):
        super().__init__(parent)
        self._current_scene_id: Optional[str] = None
        self._current_chapter_title: str = ""
        self._current_scene_title: str = ""
        self.manuscript_manager = manuscript_manager
        self.project_manager = project_manager
        self.ai_manager = ai_manager
        self._setup_ui()
        self._analysis_visible = True
        self.find_dialog = None  # Lazy initialization

    def _setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Main horizontal splitter
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left: Editor panel
        editor_panel = self._create_editor_panel()
        self.main_splitter.addWidget(editor_panel)

        # Right: Analysis panel
        self.analysis_widget = self._create_analysis_panel()
        self.main_splitter.addWidget(self.analysis_widget)

        # Set proportions (60% editor, 40% analysis)
        self.main_splitter.setStretchFactor(0, 6)
        self.main_splitter.setStretchFactor(1, 4)

        layout.addWidget(self.main_splitter)

    def _create_editor_panel(self):
        """Create the text editor panel with navigation"""
        group = QGroupBox("Manuscript")
        group.setStyleSheet(Stili.gruppo())

        layout = QVBoxLayout()
        group.setLayout(layout)

        # Navigation bar
        nav_bar = self._create_navigation_bar()
        layout.addWidget(nav_bar)

        # Text editor widget
        self.editor = TextEditor()
        self.editor.editor.textChanged.connect(self._on_editor_text_changed)

        # ZOOM: No longer needed - editor uses ZoomManager automatically
        # The internal editor (SpellCheckTextEdit/UnifiedTextEditor) registers
        # itself with ZoomManager during __init__ and responds to global zoom commands

        layout.addWidget(self.editor)

        return group

    def _create_navigation_bar(self):
        """Create the scene navigation bar"""
        nav_widget = QWidget()
        nav_widget.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                border-bottom: 1px solid #dee2e6;
                padding: 5px;
            }
        """)

        nav_layout = QHBoxLayout(nav_widget)
        nav_layout.setContentsMargins(10, 5, 10, 5)

        # Breadcrumb label
        self.breadcrumb_label = QLabel("No scene selected")
        breadcrumb_font = QFont()
        breadcrumb_font.setPointSize(12)
        breadcrumb_font.setBold(True)
        self.breadcrumb_label.setFont(breadcrumb_font)
        self.breadcrumb_label.setStyleSheet("color: #495057; background: transparent; border: none;")
        nav_layout.addWidget(self.breadcrumb_label)

        nav_layout.addStretch()

        # Word count label
        self.word_count_label = QLabel("0 words")
        self.word_count_label.setStyleSheet("color: #6c757d; background: transparent; border: none;")
        nav_layout.addWidget(self.word_count_label)

        # Navigation buttons
        self.prev_button = QPushButton("◀ Previous")
        self.prev_button.setStyleSheet("""
            QPushButton {
                background-color: #e9ecef;
                border: 1px solid #ced4da;
                border-radius: 4px;
                padding: 5px 10px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #dee2e6;
            }
            QPushButton:disabled {
                background-color: #f8f9fa;
                color: #adb5bd;
            }
        """)
        self.prev_button.clicked.connect(self.previous_scene_requested.emit)
        self.prev_button.setEnabled(False)
        nav_layout.addWidget(self.prev_button)

        self.next_button = QPushButton("Next ▶")
        self.next_button.setStyleSheet("""
            QPushButton {
                background-color: #e9ecef;
                border: 1px solid #ced4da;
                border-radius: 4px;
                padding: 5px 10px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #dee2e6;
            }
            QPushButton:disabled {
                background-color: #f8f9fa;
                color: #adb5bd;
            }
        """)
        self.next_button.clicked.connect(self.next_scene_requested.emit)
        self.next_button.setEnabled(False)
        nav_layout.addWidget(self.next_button)

        return nav_widget

    def _on_editor_text_changed(self):
        """Handle editor text changes"""
        self.text_changed.emit()

        # Get HTML content for saving (preserves formatting)
        html_content = self.editor.get_text()

        # Get plain text for word count (without HTML tags)
        plain_text = self.editor.get_plain_text()
        word_count = len(plain_text.split()) if plain_text else 0
        self.word_count_label.setText(f"{word_count} words")

        # Emit scene content changed with HTML content (preserves formatting)
        if self._current_scene_id:
            self.scene_content_changed.emit(self._current_scene_id, html_content)

    def _on_insert_ai_text(self, text: str):
        """
        Insert text from AI chat into editor

        Args:
            text: Text to insert
        """
        # Get current cursor position in editor
        cursor = self.editor.editor.textCursor()

        # If there's selected text, replace it
        if cursor.hasSelection():
            cursor.removeSelectedText()

        # Insert new text at cursor position
        cursor.insertText(text)

        # Set focus back to editor
        self.editor.editor.setFocus()

    def _create_analysis_panel(self):
        """Create the analysis results panel with sidebar"""
        # Create the context sidebar
        self.sidebar = ContextSidebar(
            sidebar_id="manuscript_sidebar",
            default_width=350,
            parent=self
        )

        # Create and add AI Chat Widget
        self.ai_chat = AIChatWidget(
            context_type="Scene",
            ai_manager=self.ai_manager,
            project_manager=self.project_manager,
            entity_manager=self.manuscript_manager,
            parent=self
        )
        self.ai_chat.text_to_insert.connect(self._on_insert_ai_text)
        self.sidebar.add_tab(self.ai_chat, "AI Assistant", "🤖")

        # Grammar panel
        self.grammar_panel = ResultsPanel("Grammar", "📖")
        self.sidebar.add_tab(self.grammar_panel, "Grammar", "📖")

        # Repetitions panel
        self.repetitions_panel = ResultsPanel("Repetitions", "🔄")
        self.sidebar.add_tab(self.repetitions_panel, "Repetitions", "🔄")

        # Style panel
        self.style_panel = ResultsPanel("Style", "✍️")
        self.sidebar.add_tab(self.style_panel, "Style", "✍️")

        # Synopsis panel
        self.synopsis_edit = UnifiedTextEditor()
        self.synopsis_edit.setPlaceholderText("Write a synopsis or summary of this scene...")
        self.synopsis_edit.textChanged.connect(self._on_synopsis_changed)
        self.sidebar.add_tab(self.synopsis_edit, "Synopsis", "📄")

        # Notes panel
        self.notes_edit = UnifiedTextEditor()
        self.notes_edit.setPlaceholderText("Write notes about this scene...")
        self.notes_edit.textChanged.connect(self._on_notes_changed)
        self.sidebar.add_tab(self.notes_edit, "Notes", "📝")

        # Store tab indices for visibility management (order matches menu actions)
        self.analysis_tab_indices = {
            'ai': 0,           # AI Assistant
            'grammar': 1,      # Grammar
            'repetitions': 2,  # Repetitions
            'style': 3,        # Style
            'synopsis': 4,     # Synopsis
            'notes': 5         # Notes
        }

        return self.sidebar

    def get_text(self) -> str:
        """
        Get the manuscript text

        Returns:
            str: Current manuscript text
        """
        return self.editor.get_text()

    def get_selected_text(self) -> str:
        """
        Get selected text in the editor

        Returns:
            str: Selected text, or empty string if no selection
        """
        cursor = self.editor.editor.textCursor()
        return cursor.selectedText()

    def get_current_content(self) -> str:
        """
        Get current content from editor (for AI commands)

        Returns:
            str: Current manuscript plain text
        """
        return self.editor.get_plain_text()

    def set_text(self, text: str):
        """
        Set the manuscript text

        Args:
            text: Text to set
        """
        self.editor.set_text(text)

    def clear_text(self):
        """Clear the manuscript text"""
        self.editor.clear()
        self._current_scene_id = None
        self._current_chapter_title = ""
        self._current_scene_title = ""
        self.breadcrumb_label.setText("No scene selected")
        self.word_count_label.setText("0 words")

    def load_scene(self, scene_id: str, chapter_title: str, scene_title: str,
                   content: str, has_previous: bool = False, has_next: bool = False,
                   synopsis: str = "", notes: str = ""):
        """
        Load a scene into the editor

        Args:
            scene_id: Scene ID
            chapter_title: Chapter title for breadcrumb
            scene_title: Scene title for breadcrumb
            content: Scene content
            has_previous: Whether there's a previous scene
            has_next: Whether there's a next scene
            synopsis: Scene synopsis (optional)
            notes: Scene notes (optional)
        """
        self._current_scene_id = scene_id
        self._current_chapter_title = chapter_title
        self._current_scene_title = scene_title

        # Temporarily disconnect signal to avoid triggering change event
        self.editor.editor.textChanged.disconnect(self._on_editor_text_changed)

        # Set content
        self.editor.set_text(content)

        # Update breadcrumb
        self.breadcrumb_label.setText(f"📖 {chapter_title} > 📝 {scene_title}")

        # Update word count (use plain text to avoid counting HTML tags)
        # toPlainText() will be called after setHtml/setPlainText in set_text
        # For now, calculate from plain text version of content
        from PySide6.QtGui import QTextDocument
        doc = QTextDocument()
        doc.setHtml(content) if ('<' in content) else doc.setPlainText(content)
        plain_text = doc.toPlainText()
        word_count = len(plain_text.split()) if plain_text else 0
        self.word_count_label.setText(f"{word_count} words")

        # Enable/disable navigation buttons
        self.prev_button.setEnabled(has_previous)
        self.next_button.setEnabled(has_next)

        # Load synopsis and notes (block signals to avoid triggering save)
        self.synopsis_edit.blockSignals(True)
        self.synopsis_edit.setPlainText(synopsis)
        self.synopsis_edit.blockSignals(False)

        self.notes_edit.blockSignals(True)
        self.notes_edit.setPlainText(notes)
        self.notes_edit.blockSignals(False)

        # Reconnect signal
        self.editor.editor.textChanged.connect(self._on_editor_text_changed)

        # Set context for AI chat widget
        context_data = {
            'scene_id': scene_id,
            'chapter_title': chapter_title,
            'scene_title': scene_title,
            'content': content
        }
        # For scenes, entity is the scene_data dict itself
        self.ai_chat.set_context(context_data, entity=context_data)

    def get_current_scene_id(self) -> Optional[str]:
        """
        Get the currently loaded scene ID

        Returns:
            Optional[str]: Current scene ID or None
        """
        return self._current_scene_id

    def save_current_scene_content(self) -> Optional[tuple]:
        """
        Get current scene ID and content for saving

        Returns:
            Optional[tuple]: (scene_id, content) or None if no scene loaded
        """
        if self._current_scene_id:
            return (self._current_scene_id, self.editor.get_text())
        return None

    def toggle_analysis_panels(self):
        """Toggle visibility of analysis panels"""
        self._analysis_visible = not self._analysis_visible
        self.analysis_widget.setVisible(self._analysis_visible)

    def is_analysis_visible(self) -> bool:
        """
        Check if analysis panels are visible

        Returns:
            bool: True if visible
        """
        return self._analysis_visible

    def clear_analysis(self):
        """Clear all analysis panels"""
        self.grammar_panel.clear()
        self.repetitions_panel.clear()
        self.style_panel.clear()

    def update_grammar_results(self, formatted_text: str):
        """
        Update grammar panel with results

        Args:
            formatted_text: Formatted analysis text
        """
        self.grammar_panel.set_text(formatted_text)

    def update_repetitions_results(self, formatted_text: str):
        """
        Update repetitions panel with results

        Args:
            formatted_text: Formatted analysis text
        """
        self.repetitions_panel.set_text(formatted_text)

    def update_style_results(self, formatted_text: str):
        """
        Update style panel with results

        Args:
            formatted_text: Formatted analysis text
        """
        self.style_panel.set_text(formatted_text)

    def highlight_errors(self, errors):
        """
        Highlight grammar errors in the editor

        Args:
            errors: List of error dictionaries
        """
        self.editor.highlight_errors(errors)

    def clear_highlights(self):
        """Clear error highlights from editor"""
        self.editor.clear_highlights()

    def undo(self):
        """Undo last action in editor"""
        self.editor.editor.undo()

    def redo(self):
        """Redo last action in editor"""
        self.editor.editor.redo()

    def can_undo(self) -> bool:
        """Check if undo is available"""
        return self.editor.editor.document().isUndoAvailable()

    def can_redo(self) -> bool:
        """Check if redo is available"""
        return self.editor.editor.document().isRedoAvailable()

    def show_find_dialog(self):
        """Show the Find dialog (without Replace)"""
        if not self.find_dialog:
            self.find_dialog = FindReplaceDialog(
                self.editor.editor,
                show_replace=False,
                parent=self
            )
        else:
            self.find_dialog.set_replace_visible(False)

        self.find_dialog.show()
        self.find_dialog.raise_()
        self.find_dialog.activateWindow()

    def show_replace_dialog(self):
        """Show the Find & Replace dialog (full version)"""
        if not self.find_dialog:
            self.find_dialog = FindReplaceDialog(
                self.editor.editor,
                show_replace=True,
                parent=self
            )
        else:
            self.find_dialog.set_replace_visible(True)

        self.find_dialog.show()
        self.find_dialog.raise_()
        self.find_dialog.activateWindow()

    def _on_synopsis_changed(self):
        """Handle synopsis text change"""
        if self._current_scene_id and self.manuscript_manager:
            synopsis = self.synopsis_edit.toPlainText()
            scene = self.manuscript_manager.get_scene(self._current_scene_id)
            if scene:
                scene.synopsis = synopsis
                # Emit text_changed to trigger save
                self.text_changed.emit()

    def _on_notes_changed(self):
        """Handle notes text change"""
        if self._current_scene_id and self.manuscript_manager:
            notes = self.notes_edit.toPlainText()
            scene = self.manuscript_manager.get_scene(self._current_scene_id)
            if scene:
                scene.notes = notes
                # Emit text_changed to trigger save
                self.text_changed.emit()

    def set_analysis_tab_visible(self, tab_index: int, visible: bool):
        """
        Set visibility of a specific analysis tab

        Args:
            tab_index: Index of tab to show/hide (0-5)
            visible: True to show, False to hide
        """
        if hasattr(self, 'sidebar'):
            self.sidebar.set_tab_visible(tab_index, visible)

    def zoom_in(self):
        """Zoom in (increase font size)"""
        if hasattr(self, 'editor'):
            self.editor.zoom_in()

    def zoom_out(self):
        """Zoom out (decrease font size)"""
        if hasattr(self, 'editor'):
            self.editor.zoom_out()

    def zoom_reset(self):
        """Reset zoom to default"""
        if hasattr(self, 'editor'):
            self.editor.zoom_reset()

    # REMOVED: set_zoom_level() - ZoomManager handles zoom automatically via registered editors

    def update_custom_dictionary(self):
        """
        Update the spell checker's custom dictionary with project-specific terms
        (character names, location names, etc.)
        """
        if not self.project_manager:
            return

        custom_words = []

        # Add character names
        if hasattr(self.project_manager, 'characters_manager') and self.project_manager.characters_manager:
            characters = self.project_manager.characters_manager.get_all_characters()
            for character in characters:
                # Add full name and first/last names separately
                if character.name:
                    custom_words.append(character.name)
                    # Split name into parts
                    name_parts = character.name.split()
                    custom_words.extend(name_parts)

        # Add location names
        if hasattr(self.project_manager, 'location_manager') and self.project_manager.location_manager:
            locations = self.project_manager.location_manager.get_all_locations()
            for location in locations:
                if location.name:
                    custom_words.append(location.name)
                    # Split location name into parts
                    name_parts = location.name.split()
                    custom_words.extend(name_parts)

        # Add worldbuilding entry titles
        if hasattr(self.project_manager, 'worldbuilding_manager') and self.project_manager.worldbuilding_manager:
            entries = self.project_manager.worldbuilding_manager.get_all_entries()
            for entry in entries:
                if entry.title:
                    custom_words.append(entry.title)
                    # Also add tags
                    if entry.tags:
                        custom_words.extend(entry.tags)

        # Update the spell checker dictionary
        if custom_words:
            self.editor.editor.add_words_to_dictionary(custom_words)

    def set_spell_check_language(self, language: str):
        """
        Set the spell checking language

        Args:
            language: Language code (e.g., 'it', 'en', 'es')
        """
        self.editor.editor.set_language(language)
