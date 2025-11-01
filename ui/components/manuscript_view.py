"""
Manuscript View - Text editor with analysis panels
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
                               QGroupBox, QLabel, QPushButton)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QTextCursor
from ui.pannels import TextEditor, ResultsPanel
from ui.styles import Stili
from ui.components.find_replace_dialog import FindReplaceDialog
from ui.components.context_sidebar import ContextSidebar
from ui.components.ai_chat_widget import AIChatWidget
from typing import Optional


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

        # Update word count
        text = self.editor.get_text()
        word_count = len(text.split()) if text else 0
        self.word_count_label.setText(f"{word_count} words")

        # Emit scene content changed if we're editing a scene
        if self._current_scene_id:
            self.scene_content_changed.emit(self._current_scene_id, text)

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
                   content: str, has_previous: bool = False, has_next: bool = False):
        """
        Load a scene into the editor

        Args:
            scene_id: Scene ID
            chapter_title: Chapter title for breadcrumb
            scene_title: Scene title for breadcrumb
            content: Scene content
            has_previous: Whether there's a previous scene
            has_next: Whether there's a next scene
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

        # Update word count
        word_count = len(content.split()) if content else 0
        self.word_count_label.setText(f"{word_count} words")

        # Enable/disable navigation buttons
        self.prev_button.setEnabled(has_previous)
        self.next_button.setEnabled(has_next)

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
