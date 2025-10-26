"""
Manuscript View - Text editor with analysis panels
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
                               QGroupBox, QLabel)
from PySide6.QtCore import Qt, Signal
from ui.pannels import TextEditor, ResultsPanel
from ui.styles import Stili


class ManuscriptView(QWidget):
    """
    View for editing the main manuscript text
    Layout: Editor (left) + Analysis Panels (right, optional)
    """

    # Signals
    text_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._analysis_visible = True

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
        """Create the text editor panel"""
        group = QGroupBox("Manuscript")
        group.setStyleSheet(Stili.gruppo())

        layout = QVBoxLayout()
        group.setLayout(layout)

        # Text editor widget
        self.editor = TextEditor()
        self.editor.editor.textChanged.connect(self.text_changed.emit)

        layout.addWidget(self.editor)

        return group

    def _create_analysis_panel(self):
        """Create the analysis results panel"""
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)

        # Vertical splitter for analysis panels
        analysis_splitter = QSplitter(Qt.Orientation.Vertical)

        # Grammar panel
        self.grammar_panel = ResultsPanel("Grammar", "📖")
        analysis_splitter.addWidget(self.grammar_panel)

        # Repetitions panel
        self.repetitions_panel = ResultsPanel("Repetitions", "🔄")
        analysis_splitter.addWidget(self.repetitions_panel)

        # Style panel
        self.style_panel = ResultsPanel("Style", "✍️")
        analysis_splitter.addWidget(self.style_panel)

        # Equal proportions
        for i in range(3):
            analysis_splitter.setStretchFactor(i, 1)

        layout.addWidget(analysis_splitter)

        return widget

    def get_text(self) -> str:
        """
        Get the manuscript text

        Returns:
            str: Current manuscript text
        """
        return self.editor.get_text()

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
