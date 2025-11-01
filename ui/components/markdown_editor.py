"""
Markdown Editor Widget - Advanced editor with syntax highlighting for AI Writing Guide
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton,
    QToolBar, QLabel, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QRegularExpression
from PySide6.QtGui import (
    QSyntaxHighlighter, QTextCharFormat, QFont, QColor,
    QTextCursor, QAction, QIcon
)
from typing import Optional


class MarkdownHighlighter(QSyntaxHighlighter):
    """
    Syntax highlighter for Markdown

    Highlights:
    - Headers (# ## ###)
    - Bold (**text**)
    - Italic (*text*)
    - Code blocks (```code```)
    - Custom commands (#COMMAND)
    - Links [text](url)
    - Lists (- * +)
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_formats()
        self._setup_rules()

    def _setup_formats(self):
        """Setup text formats for different Markdown elements"""

        # Headers (# ## ###)
        self.header_format = QTextCharFormat()
        self.header_format.setForeground(QColor("#2196F3"))  # Blue
        self.header_format.setFontWeight(QFont.Weight.Bold)
        self.header_format.setFontPointSize(14)

        # Bold (**text**)
        self.bold_format = QTextCharFormat()
        self.bold_format.setFontWeight(QFont.Weight.Bold)
        self.bold_format.setForeground(QColor("#1976D2"))  # Dark blue

        # Italic (*text*)
        self.italic_format = QTextCharFormat()
        self.italic_format.setFontItalic(True)
        self.italic_format.setForeground(QColor("#7B1FA2"))  # Purple

        # Code blocks (```code```)
        self.code_format = QTextCharFormat()
        self.code_format.setForeground(QColor("#D32F2F"))  # Red
        self.code_format.setFontFamily("Courier New")
        self.code_format.setBackground(QColor("#F5F5F5"))  # Light gray bg

        # Custom commands (#COMMAND)
        self.command_format = QTextCharFormat()
        self.command_format.setForeground(QColor("#F57C00"))  # Orange
        self.command_format.setFontWeight(QFont.Weight.Bold)

        # Links [text](url)
        self.link_format = QTextCharFormat()
        self.link_format.setForeground(QColor("#0288D1"))  # Cyan
        self.link_format.setFontUnderline(True)

        # Lists (- * +)
        self.list_format = QTextCharFormat()
        self.list_format.setForeground(QColor("#388E3C"))  # Green

        # Blockquotes (>)
        self.quote_format = QTextCharFormat()
        self.quote_format.setForeground(QColor("#757575"))  # Gray
        self.quote_format.setFontItalic(True)

    def _setup_rules(self):
        """Setup highlighting rules with regex patterns"""
        self.highlighting_rules = []

        # Headers (# Header, ## Header, etc.)
        self.highlighting_rules.append((
            QRegularExpression(r"^#{1,6}\s.*$"),
            self.header_format
        ))

        # Bold (**text** or __text__)
        self.highlighting_rules.append((
            QRegularExpression(r"\*\*[^\*]+\*\*"),
            self.bold_format
        ))
        self.highlighting_rules.append((
            QRegularExpression(r"__[^_]+__"),
            self.bold_format
        ))

        # Italic (*text* or _text_)
        self.highlighting_rules.append((
            QRegularExpression(r"\*[^\*]+\*"),
            self.italic_format
        ))
        self.highlighting_rules.append((
            QRegularExpression(r"\b_[^_]+_\b"),
            self.italic_format
        ))

        # Code blocks (`code` or ```code```)
        self.highlighting_rules.append((
            QRegularExpression(r"`[^`]+`"),
            self.code_format
        ))
        self.highlighting_rules.append((
            QRegularExpression(r"```[^`]+```"),
            self.code_format
        ))

        # Custom commands (#COMMAND)
        self.highlighting_rules.append((
            QRegularExpression(r"#[A-Z_]+\b"),
            self.command_format
        ))

        # Links [text](url)
        self.highlighting_rules.append((
            QRegularExpression(r"\[([^\]]+)\]\(([^\)]+)\)"),
            self.link_format
        ))

        # Lists (- item, * item, + item)
        self.highlighting_rules.append((
            QRegularExpression(r"^[\-\*\+]\s"),
            self.list_format
        ))

        # Blockquotes (> quote)
        self.highlighting_rules.append((
            QRegularExpression(r"^>\s.*$"),
            self.quote_format
        ))

    def highlightBlock(self, text: str):
        """Apply highlighting to a block of text"""
        # Apply all rules
        for pattern, format_obj in self.highlighting_rules:
            match_iterator = pattern.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(
                    match.capturedStart(),
                    match.capturedLength(),
                    format_obj
                )


class MarkdownEditor(QWidget):
    """
    Advanced Markdown editor with syntax highlighting and formatting toolbar

    Features:
    - Markdown syntax highlighting
    - Formatting toolbar (Bold, Italic, Headers, Lists)
    - Character and word counter
    - Auto-save capability

    Signals:
        content_changed: Emitted when text changes
        word_count_changed(int, int): Emitted with (words, characters) count
    """

    content_changed = Signal()
    word_count_changed = Signal(int, int)  # words, characters

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._setup_highlighter()
        self._connect_signals()

    def _setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        # Toolbar
        self.toolbar = self._create_toolbar()
        layout.addWidget(self.toolbar)

        # Text editor
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText(
            "Write your AI Writing Guide here...\n\n"
            "Use Markdown formatting:\n"
            "# Header 1\n"
            "## Header 2\n"
            "**bold** *italic*\n"
            "- List item\n"
            "#COMMAND for custom commands"
        )
        self.text_edit.setStyleSheet("""
            QTextEdit {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 10px;
                font-size: 13px;
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                line-height: 1.6;
            }
            QTextEdit:focus {
                border: 2px solid #2196F3;
            }
        """)
        layout.addWidget(self.text_edit)

        # Stats bar (word count, character count)
        self.stats_bar = self._create_stats_bar()
        layout.addWidget(self.stats_bar)

    def _create_toolbar(self) -> QToolBar:
        """Create formatting toolbar"""
        toolbar = QToolBar()
        toolbar.setStyleSheet("""
            QToolBar {
                background-color: #f5f5f5;
                border: 1px solid #ddd;
                border-radius: 4px;
                spacing: 3px;
                padding: 5px;
            }
            QPushButton {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 3px;
                padding: 5px 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e3f2fd;
                border-color: #2196F3;
            }
            QPushButton:pressed {
                background-color: #bbdefb;
            }
        """)

        # Bold button
        bold_btn = QPushButton("B")
        bold_btn.setToolTip("Bold (**text**)")
        bold_btn.clicked.connect(lambda: self._insert_formatting("**", "**"))
        toolbar.addWidget(bold_btn)

        # Italic button
        italic_btn = QPushButton("I")
        italic_btn.setFont(QFont("Arial", 10, QFont.Weight.Normal, True))
        italic_btn.setToolTip("Italic (*text*)")
        italic_btn.clicked.connect(lambda: self._insert_formatting("*", "*"))
        toolbar.addWidget(italic_btn)

        # Header 1
        h1_btn = QPushButton("H1")
        h1_btn.setToolTip("Header 1 (# Header)")
        h1_btn.clicked.connect(lambda: self._insert_header(1))
        toolbar.addWidget(h1_btn)

        # Header 2
        h2_btn = QPushButton("H2")
        h2_btn.setToolTip("Header 2 (## Header)")
        h2_btn.clicked.connect(lambda: self._insert_header(2))
        toolbar.addWidget(h2_btn)

        # Header 3
        h3_btn = QPushButton("H3")
        h3_btn.setToolTip("Header 3 (### Header)")
        h3_btn.clicked.connect(lambda: self._insert_header(3))
        toolbar.addWidget(h3_btn)

        # List
        list_btn = QPushButton("• List")
        list_btn.setToolTip("Unordered list (- item)")
        list_btn.clicked.connect(self._insert_list)
        toolbar.addWidget(list_btn)

        # Code
        code_btn = QPushButton("</>")
        code_btn.setToolTip("Code (`code`)")
        code_btn.clicked.connect(lambda: self._insert_formatting("`", "`"))
        toolbar.addWidget(code_btn)

        # Link
        link_btn = QPushButton("🔗")
        link_btn.setToolTip("Link ([text](url))")
        link_btn.clicked.connect(self._insert_link)
        toolbar.addWidget(link_btn)

        # Command
        command_btn = QPushButton("#CMD")
        command_btn.setToolTip("Custom command (#COMMAND)")
        command_btn.clicked.connect(self._insert_command)
        toolbar.addWidget(command_btn)

        return toolbar

    def _create_stats_bar(self) -> QWidget:
        """Create statistics bar with word/character count"""
        stats_widget = QWidget()
        stats_layout = QHBoxLayout(stats_widget)
        stats_layout.setContentsMargins(5, 5, 5, 5)

        self.words_label = QLabel("Words: 0")
        self.words_label.setStyleSheet("color: #666; font-size: 12px;")
        stats_layout.addWidget(self.words_label)

        stats_layout.addWidget(QLabel("•"))

        # Character counter with limit indicator
        self.chars_label = QLabel("0 / 50,000 characters")
        self.chars_label.setStyleSheet("color: #666; font-size: 12px;")
        stats_layout.addWidget(self.chars_label)

        stats_layout.addStretch()

        stats_widget.setStyleSheet("""
            QWidget {
                background-color: #f9f9f9;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
        """)

        return stats_widget

    def _setup_highlighter(self):
        """Setup Markdown syntax highlighter"""
        self.highlighter = MarkdownHighlighter(self.text_edit.document())

    def _connect_signals(self):
        """Connect widget signals"""
        self.text_edit.textChanged.connect(self._on_text_changed)

    def _on_text_changed(self):
        """Handle text change - update stats, validate, and emit signal"""
        text = self.text_edit.toPlainText()

        # Count words and characters
        words = len(text.split()) if text.strip() else 0
        characters = len(text)

        # Character limit validation
        max_length = 50000
        warning_threshold = 10000

        # Update labels
        self.words_label.setText(f"Words: {words}")
        self.chars_label.setText(f"{characters} / {max_length} characters")

        # Color-coded validation feedback
        if characters > max_length:
            # Exceeded limit - RED
            self.chars_label.setStyleSheet(
                "color: #f44336; font-size: 12px; font-weight: bold;"
            )
        elif characters > warning_threshold:
            # Warning (large context) - ORANGE
            self.chars_label.setStyleSheet(
                "color: #ff9800; font-size: 12px;"
            )
        else:
            # Normal - GRAY
            self.chars_label.setStyleSheet(
                "color: #666; font-size: 12px;"
            )

        # Emit signals
        self.content_changed.emit()
        self.word_count_changed.emit(words, characters)

    def _insert_formatting(self, prefix: str, suffix: str):
        """Insert formatting around selected text or at cursor"""
        cursor = self.text_edit.textCursor()

        if cursor.hasSelection():
            # Wrap selected text
            selected_text = cursor.selectedText()
            cursor.insertText(f"{prefix}{selected_text}{suffix}")
        else:
            # Insert at cursor
            cursor.insertText(f"{prefix}text{suffix}")
            # Select "text" for easy replacement
            cursor.movePosition(QTextCursor.MoveOperation.Left, QTextCursor.MoveMode.MoveAnchor, len(suffix) + 4)
            cursor.movePosition(QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.KeepAnchor, 4)
            self.text_edit.setTextCursor(cursor)

    def _insert_header(self, level: int):
        """Insert header at current line"""
        cursor = self.text_edit.textCursor()

        # Move to start of line
        cursor.movePosition(QTextCursor.MoveOperation.StartOfLine)

        # Insert header markers
        prefix = "#" * level + " "
        cursor.insertText(prefix)

    def _insert_list(self):
        """Insert list item"""
        cursor = self.text_edit.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.StartOfLine)
        cursor.insertText("- ")

    def _insert_link(self):
        """Insert Markdown link"""
        cursor = self.text_edit.textCursor()

        if cursor.hasSelection():
            selected_text = cursor.selectedText()
            cursor.insertText(f"[{selected_text}](url)")
        else:
            cursor.insertText("[text](url)")
            # Select "text" for easy replacement
            cursor.movePosition(QTextCursor.MoveOperation.Left, QTextCursor.MoveMode.MoveAnchor, 10)
            cursor.movePosition(QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.KeepAnchor, 4)
            self.text_edit.setTextCursor(cursor)

    def _insert_command(self):
        """Insert custom command placeholder"""
        cursor = self.text_edit.textCursor()
        cursor.insertText("#COMMAND [description]")
        # Select "COMMAND" for easy replacement
        cursor.movePosition(QTextCursor.MoveOperation.Left, QTextCursor.MoveMode.MoveAnchor, 23)
        cursor.movePosition(QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.KeepAnchor, 7)
        self.text_edit.setTextCursor(cursor)

    def get_content(self) -> str:
        """
        Get current editor content

        Returns:
            str: Markdown content
        """
        return self.text_edit.toPlainText()

    def set_content(self, content: str):
        """
        Set editor content

        Args:
            content: Markdown content to set
        """
        self.text_edit.setPlainText(content)

    def clear(self):
        """Clear editor content"""
        self.text_edit.clear()

    def get_word_count(self) -> int:
        """
        Get current word count

        Returns:
            int: Number of words
        """
        text = self.text_edit.toPlainText()
        return len(text.split()) if text.strip() else 0

    def get_character_count(self) -> int:
        """
        Get current character count

        Returns:
            int: Number of characters
        """
        return len(self.text_edit.toPlainText())
