"""
Custom widgets for the interface panels
"""
from PySide6.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, QLabel,
                               QScrollArea, QTextEdit, QWidget, QPushButton)
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCharFormat, QColor, QTextCursor, QFont, QKeySequence


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

        # Formatting toolbar
        self.toolbar = self._create_formatting_toolbar()
        layout.addWidget(self.toolbar)

        # Counter info
        self.counter_info = QLabel("Words: 0 | Characters: 0")
        self.counter_info.setStyleSheet("color: #666; padding: 5px;")
        layout.addWidget(self.counter_info)

        # Main editor with spell checking
        # Lazy import to avoid circular dependency
        try:
            from ui.components.spell_check_text_edit import SpellCheckTextEdit
            self.editor = SpellCheckTextEdit()
            # Enable spell checking by default (language will be set when project loads)
            self.editor.enable_spell_checking('it')
        except ImportError:
            # Fallback to standard QTextEdit if import fails
            self.editor = QTextEdit()

        self.editor.setPlaceholderText(
            "Start writing your text here...\n\n"
            "Grammar and spelling errors will be highlighted."
        )

        # Connect signals
        self.editor.textChanged.connect(self._update_counter)
        self.editor.cursorPositionChanged.connect(self._update_format_buttons)

        layout.addWidget(self.editor)

        # Legend
        legend = QLabel("  🔴 Spelling & Grammar  🟠 Apostrophes  🔵 Punctuation  ")
        legend.setStyleSheet("""
            background-color: #f8f9fa;
            color: #6c757d;
            font-size: 10px;
            padding: 5px 10px;
            border-top: 1px solid #dee2e6;
        """)
        layout.addWidget(legend)

    def _create_formatting_toolbar(self):
        """Create the rich text formatting toolbar"""
        toolbar = QWidget()
        toolbar.setStyleSheet("""
            QWidget {
                background-color: #f0f0f0;
                border-bottom: 1px solid #d0d0d0;
                padding: 5px;
            }
        """)

        layout = QHBoxLayout(toolbar)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # Bold button
        self.bold_btn = QPushButton("B")
        self.bold_btn.setCheckable(True)
        self.bold_btn.setToolTip("Bold (Ctrl+B)")
        self.bold_btn.setShortcut(QKeySequence("Ctrl+B"))
        self.bold_btn.setFixedSize(32, 28)
        self.bold_btn.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.bold_btn.clicked.connect(self._toggle_bold)
        self.bold_btn.setStyleSheet("""
            QPushButton {
                background-color: white;
                border: 1px solid #ccc;
                border-radius: 3px;
            }
            QPushButton:checked {
                background-color: #4CAF50;
                color: white;
            }
            QPushButton:hover {
                background-color: #e8e8e8;
            }
        """)
        layout.addWidget(self.bold_btn)

        # Italic button
        self.italic_btn = QPushButton("I")
        self.italic_btn.setCheckable(True)
        self.italic_btn.setToolTip("Italic (Ctrl+I)")
        self.italic_btn.setShortcut(QKeySequence("Ctrl+I"))
        self.italic_btn.setFixedSize(32, 28)
        italic_font = QFont("Arial", 10)
        italic_font.setItalic(True)
        self.italic_btn.setFont(italic_font)
        self.italic_btn.clicked.connect(self._toggle_italic)
        self.italic_btn.setStyleSheet("""
            QPushButton {
                background-color: white;
                border: 1px solid #ccc;
                border-radius: 3px;
            }
            QPushButton:checked {
                background-color: #2196F3;
                color: white;
            }
            QPushButton:hover {
                background-color: #e8e8e8;
            }
        """)
        layout.addWidget(self.italic_btn)

        # Underline button
        self.underline_btn = QPushButton("U")
        self.underline_btn.setCheckable(True)
        self.underline_btn.setToolTip("Underline (Ctrl+U)")
        self.underline_btn.setShortcut(QKeySequence("Ctrl+U"))
        self.underline_btn.setFixedSize(32, 28)
        underline_font = QFont("Arial", 10)
        underline_font.setUnderline(True)
        self.underline_btn.setFont(underline_font)
        self.underline_btn.clicked.connect(self._toggle_underline)
        self.underline_btn.setStyleSheet("""
            QPushButton {
                background-color: white;
                border: 1px solid #ccc;
                border-radius: 3px;
            }
            QPushButton:checked {
                background-color: #FF9800;
                color: white;
            }
            QPushButton:hover {
                background-color: #e8e8e8;
            }
        """)
        layout.addWidget(self.underline_btn)

        # Spacer
        layout.addStretch()

        # Info label
        info_label = QLabel("Rich text formatting enabled")
        info_label.setStyleSheet("color: #666; font-size: 10px;")
        layout.addWidget(info_label)

        return toolbar

    def _toggle_bold(self):
        """Toggle bold formatting"""
        fmt = self.editor.currentCharFormat()
        if self.bold_btn.isChecked():
            fmt.setFontWeight(QFont.Weight.Bold)
        else:
            fmt.setFontWeight(QFont.Weight.Normal)
        self.editor.setCurrentCharFormat(fmt)
        self.editor.setFocus()

    def _toggle_italic(self):
        """Toggle italic formatting"""
        fmt = self.editor.currentCharFormat()
        fmt.setFontItalic(self.italic_btn.isChecked())
        self.editor.setCurrentCharFormat(fmt)
        self.editor.setFocus()

    def _toggle_underline(self):
        """Toggle underline formatting"""
        fmt = self.editor.currentCharFormat()
        fmt.setFontUnderline(self.underline_btn.isChecked())
        self.editor.setCurrentCharFormat(fmt)
        self.editor.setFocus()

    def _update_format_buttons(self):
        """Update format buttons state based on current cursor position"""
        fmt = self.editor.currentCharFormat()

        # Block signals to avoid triggering the toggle actions
        self.bold_btn.blockSignals(True)
        self.italic_btn.blockSignals(True)
        self.underline_btn.blockSignals(True)

        # Update button states
        self.bold_btn.setChecked(fmt.fontWeight() == QFont.Weight.Bold)
        self.italic_btn.setChecked(fmt.fontItalic())
        self.underline_btn.setChecked(fmt.fontUnderline())

        # Unblock signals
        self.bold_btn.blockSignals(False)
        self.italic_btn.blockSignals(False)
        self.underline_btn.blockSignals(False)

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
        """Get rich text (HTML) from the editor"""
        return self.editor.toHtml()

    def get_plain_text(self):
        """Get plain text from the editor (without formatting)"""
        return self.editor.toPlainText()

    def set_text(self, text):
        """Set text in the editor (supports both plain text and HTML)"""
        if not text:
            self.editor.clear()
        elif text.strip().startswith('<') or '<html>' in text.lower():
            # It's HTML, preserve formatting
            self.editor.setHtml(text)
        else:
            # It's plain text
            self.editor.setPlainText(text)
        self._update_counter()

    def clear(self):
        """Clear the editor"""
        try:
            self.clear_highlights()
            self.editor.clear()
            self._update_counter()
        except Exception as e:
            print(f"Error in clear: {e}")