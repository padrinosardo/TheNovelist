"""
Custom widgets for the interface panels
"""
from PySide6.QtWidgets import (QFrame, QVBoxLayout, QLabel,
                               QScrollArea, QPlainTextEdit)
from PySide6.QtCore import Qt


class ResultsPanel(QFrame):
    """
    Widget to display analysis results
    """

    def __init__(self, title, icon="📊"):
        """
        Initialize the results panel

        Args:
            title: Panel title
            icon: Emoji/icon to display in the title
        """
        super().__init__()
        self.title_text = title
        self.icon = icon

        self._initialize_ui()

    def _initialize_ui(self):
        """Initialize the panel interface"""
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        self.setLineWidth(2)

        layout = QVBoxLayout()
        self.setLayout(layout)

        # Title
        self.title_label = QLabel(f"{self.icon} {self.title_text}")
        self.title_label.setStyleSheet(
            "font-size: 14px; font-weight: bold; padding: 5px;"
        )
        layout.addWidget(self.title_label)

        # Results area with scroll
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")

        # Use QPlainTextEdit instead of QTextEdit - simpler, fewer cursor issues
        self.content = QPlainTextEdit()
        self.content.setReadOnly(True)
        self.content.setPlaceholderText(
            f"Click 'Analyze {self.title_text}' to see results..."
        )

        scroll.setWidget(self.content)
        layout.addWidget(scroll)

    def set_text(self, text):
        """
        Set the results text

        Args:
            text: Text to display
        """
        self.content.setPlainText(text if text else "")

    def append_text(self, text):
        """
        Append text to existing results

        Args:
            text: Text to append
        """
        if text:
            self.content.appendPlainText(text)

    def clear(self):
        """Clear the results"""
        self.content.clear()

    def get_text(self):
        """
        Get the current text

        Returns:
            str: Panel text
        """
        return self.content.toPlainText()


class TextEditor(QFrame):
    """
    Main text editor widget with counter
    """

    def __init__(self):
        """Initialize the text editor"""
        super().__init__()
        self._initialize_ui()

    def _initialize_ui(self):
        """Initialize the editor interface"""
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Counter info
        self.counter_info = QLabel("Words: 0 | Characters: 0")
        self.counter_info.setStyleSheet("color: #666; padding: 5px;")
        layout.addWidget(self.counter_info)

        # Main editor - use QPlainTextEdit
        self.editor = QPlainTextEdit()
        self.editor.setPlaceholderText(
            "Start writing your text here...\n\n"
            "Use the buttons above to analyze grammar, "
            "find repetitions, and evaluate writing style.\n\n"
            "Results will appear in the panels on the right."
        )

        # Connect signal to update counter
        self.editor.textChanged.connect(self._update_counter)

        layout.addWidget(self.editor)

    def _update_counter(self):
        """Update word and character counter"""
        text = self.editor.toPlainText()
        words = len(text.split()) if text.strip() else 0
        characters = len(text)
        self.counter_info.setText(f"Words: {words} | Characters: {characters}")

    def get_text(self):
        """
        Get text from the editor

        Returns:
            str: Editor text
        """
        return self.editor.toPlainText()

    def set_text(self, text):
        """
        Set text in the editor

        Args:
            text: Text to set
        """
        self.editor.setPlainText(text if text else "")
        self._update_counter()

    def clear(self):
        """Clear the editor"""
        self.editor.clear()
        self._update_counter()