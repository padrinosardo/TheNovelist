"""
Custom widgets for the interface panels
"""
from PySide6.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, QLabel,
                               QScrollArea, QTextEdit, QWidget)
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCharFormat, QColor, QTextCursor


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

class TextEditor(QFrame):
    """
    Main text editor widget with counter and error highlighting
    """

    def __init__(self):
        """Initialize the text editor"""
        super().__init__()
        self.error_highlights = []
        self._initialize_ui()

    def _initialize_ui(self):
        """Initialize the editor interface"""
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Counter info
        self.counter_info = QLabel("Words: 0 | Characters: 0")
        self.counter_info.setStyleSheet("color: #666; padding: 5px;")
        layout.addWidget(self.counter_info)

        # Main editor
        self.editor = QTextEdit()
        self.editor.setPlaceholderText(
            "Start writing your text here...\n\n"
            "Grammar errors will be highlighted."
        )

        # Connect signal to update counter
        self.editor.textChanged.connect(self._update_counter)

        layout.addWidget(self.editor)

        # Legend
        legend = QLabel("  🔴 Grammar  🟠 Apostrophes  🔵 Punctuation  ")
        legend.setStyleSheet("""
            background-color: #f8f9fa; 
            color: #6c757d; 
            font-size: 10px; 
            padding: 5px 10px;
            border-top: 1px solid #dee2e6;
        """)
        layout.addWidget(legend)

    def _update_counter(self):
        """Update word and character counter"""
        text = self.editor.toPlainText()
        words = len(text.split()) if text.strip() else 0
        characters = len(text)
        self.counter_info.setText(f"Words: {words} | Characters: {characters}")

    def highlight_errors(self, errors):
        """
        Highlight errors in the editor - SAFE VERSION

        Args:
            errors: List of error dictionaries
        """
        if not errors:
            return

        try:
            # Disconnect textChanged to avoid recursion
            self.editor.textChanged.disconnect(self._update_counter)

            # Clear previous highlights
            self.clear_highlights()

            # Get document
            document = self.editor.document()
            if not document:
                return

            # Apply each highlight
            for error in errors:
                try:
                    self._apply_highlight_safe(error, document)
                except Exception as e:
                    print(f"Warning: Could not highlight error: {e}")
                    continue

        except Exception as e:
            print(f"Error in highlight_errors: {e}")
        finally:
            # Reconnect signal
            self.editor.textChanged.connect(self._update_counter)

    def _apply_highlight_safe(self, error, document):
        """Apply highlight safely with bounds checking"""
        start = error.get('start', 0)
        end = error.get('end', 0)

        # Validate positions
        text_length = len(self.editor.toPlainText())
        if start < 0 or end > text_length or start >= end:
            return

        # Create cursor
        cursor = QTextCursor(document)
        cursor.setPosition(start)
        cursor.setPosition(end, QTextCursor.KeepAnchor)

        # Create format
        fmt = QTextCharFormat()
        color = self._get_category_color(error.get('category', 'custom'))
        fmt.setUnderlineColor(color)
        fmt.setUnderlineStyle(QTextCharFormat.WaveUnderline)

        # Apply format
        cursor.setCharFormat(fmt)

    def _get_category_color(self, category):
        """Get color for error category"""
        colors = {
            'accent': QColor(255, 0, 0),
            'apostrophe': QColor(255, 140, 0),
            'preposition': QColor(255, 0, 0),
            'h_verb': QColor(255, 0, 0),
            'verb': QColor(255, 0, 0),
            'punctuation': QColor(0, 120, 215),
            'double': QColor(255, 0, 0),
            'custom': QColor(128, 128, 128)
        }
        return colors.get(category, QColor(255, 0, 0))

    def clear_highlights(self):
        """Clear all highlights safely"""
        try:
            # Get document
            document = self.editor.document()
            if not document:
                return

            # Select all and reset format
            cursor = QTextCursor(document)
            cursor.select(QTextCursor.Document)

            fmt = QTextCharFormat()
            fmt.setUnderlineStyle(QTextCharFormat.NoUnderline)
            cursor.setCharFormat(fmt)

            self.error_highlights = []
        except Exception as e:
            print(f"Error clearing highlights: {e}")

    def get_text(self):
        """Get text from the editor"""
        return self.editor.toPlainText()

    def set_text(self, text):
        """Set text in the editor"""
        self.editor.setPlainText(text if text else "")
        self._update_counter()

    def clear(self):
        """Clear the editor"""
        try:
            self.clear_highlights()
            self.editor.clear()
            self._update_counter()
        except Exception as e:
            print(f"Error in clear: {e}")