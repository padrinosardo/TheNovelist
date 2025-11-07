"""
Custom widgets for the interface panels
"""
from PySide6.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, QLabel,
                               QScrollArea, QTextEdit, QWidget)
from PySide6.QtCore import Qt


def _get_text_editor():
    """Lazy import to avoid circular dependency"""
    from ui.components.rich_text_editor import RichTextEditor
    return RichTextEditor


# Create TextEditor as a lazy-loaded class for backward compatibility
class TextEditor:
    """Lazy-loaded proxy to RichTextEditor"""
    def __new__(cls, *args, **kwargs):
        return _get_text_editor()(*args, **kwargs)


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
        super().__init__()  # Chiama QFrame.__init__() senza argomenti

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

        self.content = QTextEdit()
        self.content.setReadOnly(True)
        self.content.setPlaceholderText(
            f"Click 'Analyze {self.title_text}' to see results..."
        )

        scroll.setWidget(self.content)
        layout.addWidget(scroll)

    def set_text(self, text):
        """Set the results text"""
        self.content.setPlainText(text if text else "")

    def append_text(self, text):
        """Append text to existing results"""
        if text:
            self.content.append(text)

    def clear(self):
        """Clear the results"""
        self.content.clear()

    def get_text(self):
        """Get the current text"""
        return self.content.toPlainText()


# TextEditor is now imported from ui.components.rich_text_editor
# All functionality (formatting, tables, spell check) is in RichTextEditor
