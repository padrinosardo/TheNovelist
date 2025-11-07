"""
Rich Text Editor - Reusable text editor with formatting toolbar and table support
"""
from PySide6.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, QLabel,
                               QTextEdit, QWidget, QPushButton, QToolButton, QMenu, QApplication)
from PySide6.QtCore import Qt, Signal, QEvent
from PySide6.QtGui import (QTextCharFormat, QColor, QTextCursor, QFont, QKeySequence, QAction,
                           QPixmap, QPainter, QPen, QIcon, QTextTableFormat, QKeyEvent, QPalette)


class RichTextEditor(QFrame):
    """
    Reusable rich text editor widget with formatting toolbar and table support

    Features:
    - Comprehensive formatting toolbar (bold, italic, underline, etc.)
    - Text alignment controls
    - Quote marks and typography symbols
    - Table insertion and editing
    - Spell checking integration
    - Word/character counter
    - Customizable (show/hide components)
    """

    # Signals
    text_changed = Signal()

    def __init__(self,
                 show_toolbar=True,
                 show_counter=True,
                 show_legend=True,
                 enable_spell_check=True,
                 enable_tables=True,
                 spell_check_language='it',
                 parent=None):
        """
        Initialize the rich text editor

        Args:
            show_toolbar: Show formatting toolbar (default: True)
            show_counter: Show word/character counter (default: True)
            show_legend: Show error legend (default: True)
            enable_spell_check: Enable spell checking (default: True)
            enable_tables: Enable table functionality (default: True)
            spell_check_language: Spell check language code (default: 'it')
            parent: Parent widget
        """
        super().__init__(parent)

        self.show_toolbar = show_toolbar
        self.show_counter = show_counter
        self.show_legend = show_legend
        self.enable_spell_check = enable_spell_check
        self.enable_tables = enable_tables
        self.spell_check_language = spell_check_language

        self.error_highlights = []
        self.grammar_extra_selections = []

        # Toolbar groups - widgets for each formatting group
        self.toolbar_groups = {
            'script': [],  # Superscript/Subscript buttons
            'smallcaps': [],  # Small Caps button
            'alignment': [],  # Alignment buttons
            'special_chars': [],  # Quote, dashes, ellipsis
            'tables': []  # Table buttons
        }

        self._initialize_ui()

    def _is_dark_mode(self) -> bool:
        """Detect if system is in dark mode"""
        palette = QApplication.palette()
        bg_color = palette.color(QPalette.ColorRole.Window)
        return bg_color.lightness() < 128

    def _get_button_colors(self) -> dict:
        """Get appropriate button colors based on theme"""
        if self._is_dark_mode():
            return {
                'bg': '#3C3C3C',
                'border': '#555555',
                'text': '#E0E0E0',
                'hover_bg': '#4A4A4A',
            }
        else:
            return {
                'bg': '#FFFFFF',
                'border': '#CCCCCC',
                'text': '#000000',
                'hover_bg': '#E8E8E8',
            }

    def _initialize_ui(self):
        """Initialize the editor interface"""
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Formatting toolbar (optional)
        if self.show_toolbar:
            self.toolbar = self._create_formatting_toolbar()
            layout.addWidget(self.toolbar)

        # Counter info (optional)
        if self.show_counter:
            self.counter_info = QLabel("Words: 0 | Characters: 0")
            self.counter_info.setStyleSheet("color: #666; padding: 5px;")
            layout.addWidget(self.counter_info)

        # Main editor with optional spell checking
        if self.enable_spell_check:
            try:
                from ui.components.spell_check_text_edit import SpellCheckTextEdit
                self.editor = SpellCheckTextEdit()
                self.editor.enable_spell_checking(self.spell_check_language)
            except ImportError:
                self.editor = QTextEdit()
        else:
            self.editor = QTextEdit()

        self.editor.setPlaceholderText(
            "Start writing your text here...\n\n"
            "Use the toolbar to format your text."
        )

        # Connect signals
        self.editor.textChanged.connect(self._on_text_changed)
        if self.show_toolbar:
            self.editor.cursorPositionChanged.connect(self._update_format_buttons)

        # Install event filter for TAB navigation in tables
        self.editor.installEventFilter(self)

        layout.addWidget(self.editor)

        # Legend (optional)
        if self.show_legend:
            legend = QLabel("  🔴 Spelling & Grammar  🟠 Apostrophes  🔵 Punctuation  ")
            legend.setStyleSheet("""
                background-color: #f8f9fa;
                color: #6c757d;
                font-size: 10px;
                padding: 5px 10px;
                border-top: 1px solid #dee2e6;
            """)
            layout.addWidget(legend)

    def _on_text_changed(self):
        """Handle text change"""
        if self.show_counter:
            self._update_counter()
        self.text_changed.emit()

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

        # Main vertical layout to stack two rows
        main_layout = QVBoxLayout(toolbar)
        main_layout.setContentsMargins(5, 2, 5, 2)
        main_layout.setSpacing(3)

        # ROW 1: Basic formatting + alignments + help
        row1_layout = QHBoxLayout()
        row1_layout.setSpacing(5)

        # ROW 2: Special characters + tables
        row2_layout = QHBoxLayout()
        row2_layout.setSpacing(5)

        # Bold button
        self.bold_btn = QPushButton("B")
        self.bold_btn.setCheckable(True)
        self.bold_btn.setToolTip("Bold (Ctrl+B)")
        self.bold_btn.setShortcut(QKeySequence("Ctrl+B"))
        self.bold_btn.setFixedSize(32, 28)
        self.bold_btn.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.bold_btn.clicked.connect(self._toggle_bold)
        self.bold_btn.setStyleSheet(self._get_custom_button_style("#4CAF50"))
        row1_layout.addWidget(self.bold_btn)

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
        self.italic_btn.setStyleSheet(self._get_custom_button_style("#2196F3"))
        row1_layout.addWidget(self.italic_btn)

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
        self.underline_btn.setStyleSheet(self._get_custom_button_style("#FF9800"))
        row1_layout.addWidget(self.underline_btn)

        # Strikethrough button
        self.strike_btn = QPushButton("S")
        self.strike_btn.setCheckable(True)
        self.strike_btn.setToolTip("Strikethrough (Ctrl+Shift+X)")
        self.strike_btn.setShortcut(QKeySequence("Ctrl+Shift+X"))
        self.strike_btn.setFixedSize(32, 28)
        strike_font = QFont("Arial", 10)
        strike_font.setStrikeOut(True)
        self.strike_btn.setFont(strike_font)
        self.strike_btn.clicked.connect(self._toggle_strikethrough)
        self.strike_btn.setStyleSheet(self._get_custom_button_style("#9C27B0"))
        row1_layout.addWidget(self.strike_btn)

        # Separator
        separator1 = QLabel("|")
        separator1.setStyleSheet(self._get_separator_style())
        row1_layout.addWidget(separator1)
        self.toolbar_groups['script'].append(separator1)

        # Superscript button
        self.superscript_btn = QPushButton("x²")
        self.superscript_btn.setCheckable(True)
        self.superscript_btn.setToolTip("Superscript (Ctrl+Shift+=)")
        self.superscript_btn.setShortcut(QKeySequence("Ctrl+Shift+="))
        self.superscript_btn.setFixedSize(32, 28)
        self.superscript_btn.clicked.connect(self._toggle_superscript)
        self.superscript_btn.setStyleSheet(self._get_custom_button_style("#00BCD4"))
        row1_layout.addWidget(self.superscript_btn)
        self.toolbar_groups['script'].append(self.superscript_btn)

        # Subscript button
        self.subscript_btn = QPushButton("x₂")
        self.subscript_btn.setCheckable(True)
        self.subscript_btn.setToolTip("Subscript (Ctrl+=)")
        self.subscript_btn.setShortcut(QKeySequence("Ctrl+="))
        self.subscript_btn.setFixedSize(32, 28)
        self.subscript_btn.clicked.connect(self._toggle_subscript)
        self.subscript_btn.setStyleSheet(self._get_custom_button_style("#009688"))
        row1_layout.addWidget(self.subscript_btn)
        self.toolbar_groups['script'].append(self.subscript_btn)

        # Separator
        separator2 = QLabel("|")
        separator2.setStyleSheet(self._get_separator_style())
        row1_layout.addWidget(separator2)
        self.toolbar_groups['smallcaps'].append(separator2)

        # Small Caps button
        self.smallcaps_btn = QPushButton("ᴀʙ")
        self.smallcaps_btn.setCheckable(True)
        self.smallcaps_btn.setToolTip("Small Caps (Ctrl+Shift+K)")
        self.smallcaps_btn.setShortcut(QKeySequence("Ctrl+Shift+K"))
        self.smallcaps_btn.setFixedSize(32, 28)
        self.smallcaps_btn.clicked.connect(self._toggle_smallcaps)
        self.smallcaps_btn.setStyleSheet(self._get_custom_button_style("#795548"))
        row1_layout.addWidget(self.smallcaps_btn)
        self.toolbar_groups['smallcaps'].append(self.smallcaps_btn)

        # Separator
        separator2b = QLabel("|")
        separator2b.setStyleSheet(self._get_separator_style())
        row1_layout.addWidget(separator2b)
        self.toolbar_groups['alignment'].append(separator2b)

        # Alignment buttons with visual icons
        self.align_left_btn = QPushButton()
        self.align_left_btn.setIcon(self._create_alignment_icon('left'))
        self.align_left_btn.setCheckable(True)
        self.align_left_btn.setToolTip("Align Left (Ctrl+L)")
        self.align_left_btn.setShortcut(QKeySequence("Ctrl+L"))
        self.align_left_btn.setFixedSize(32, 28)
        self.align_left_btn.clicked.connect(lambda: self._set_alignment(Qt.AlignmentFlag.AlignLeft))
        self.align_left_btn.setStyleSheet(self._get_button_style())
        row1_layout.addWidget(self.align_left_btn)
        self.toolbar_groups['alignment'].append(self.align_left_btn)

        self.align_center_btn = QPushButton()
        self.align_center_btn.setIcon(self._create_alignment_icon('center'))
        self.align_center_btn.setCheckable(True)
        self.align_center_btn.setToolTip("Align Center (Ctrl+E)")
        self.align_center_btn.setShortcut(QKeySequence("Ctrl+E"))
        self.align_center_btn.setFixedSize(32, 28)
        self.align_center_btn.clicked.connect(lambda: self._set_alignment(Qt.AlignmentFlag.AlignCenter))
        self.align_center_btn.setStyleSheet(self._get_button_style())
        row1_layout.addWidget(self.align_center_btn)
        self.toolbar_groups['alignment'].append(self.align_center_btn)

        self.align_right_btn = QPushButton()
        self.align_right_btn.setIcon(self._create_alignment_icon('right'))
        self.align_right_btn.setCheckable(True)
        self.align_right_btn.setToolTip("Align Right (Ctrl+R)")
        self.align_right_btn.setShortcut(QKeySequence("Ctrl+R"))
        self.align_right_btn.setFixedSize(32, 28)
        self.align_right_btn.clicked.connect(lambda: self._set_alignment(Qt.AlignmentFlag.AlignRight))
        self.align_right_btn.setStyleSheet(self._get_button_style())
        row1_layout.addWidget(self.align_right_btn)
        self.toolbar_groups['alignment'].append(self.align_right_btn)

        self.align_justify_btn = QPushButton()
        self.align_justify_btn.setIcon(self._create_alignment_icon('justify'))
        self.align_justify_btn.setCheckable(True)
        self.align_justify_btn.setToolTip("Justify (Ctrl+J)")
        self.align_justify_btn.setShortcut(QKeySequence("Ctrl+J"))
        self.align_justify_btn.setFixedSize(32, 28)
        self.align_justify_btn.clicked.connect(lambda: self._set_alignment(Qt.AlignmentFlag.AlignJustify))
        self.align_justify_btn.setStyleSheet(self._get_button_style())
        row1_layout.addWidget(self.align_justify_btn)
        self.toolbar_groups['alignment'].append(self.align_justify_btn)

        # Spacer before help button (ROW 1)
        row1_layout.addStretch()

        # Help button (ROW 1 - at the end)
        self.help_btn = QPushButton("?")
        self.help_btn.setToolTip("Mostra Scorciatoie da Tastiera (F1)")
        self.help_btn.setShortcut(QKeySequence("F1"))
        self.help_btn.setFixedSize(32, 28)
        self.help_btn.clicked.connect(self._show_keyboard_shortcuts)
        # Help button keeps green color in both modes
        self.help_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: 1px solid #4CAF50;
                border-radius: 3px;
                font-weight: bold;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        row1_layout.addWidget(self.help_btn)

        # === ROW 2 STARTS HERE ===
        # Quote marks dropdown button

        # Quote marks dropdown button
        self.quote_btn = QToolButton()
        self.quote_btn.setText("« »")
        self.quote_btn.setToolTip("Insert Quotes")
        self.quote_btn.setFixedSize(40, 28)
        self.quote_btn.setPopupMode(QToolButton.ToolButtonPopupMode.MenuButtonPopup)
        self.quote_btn.clicked.connect(self._insert_current_quotes)
        self.quote_btn.setStyleSheet(self._get_toolbutton_style())

        # Create dropdown menu for quote types
        quote_menu = QMenu(self.quote_btn)

        # Guillemets (French quotes) - Default
        guillemets_action = QAction("« » Guillemets", self)
        guillemets_action.triggered.connect(lambda: self._change_quote_type("«", "»", "« »"))
        quote_menu.addAction(guillemets_action)

        # Curved double quotes
        double_action = QAction("" " Virgolette Doppie", self)
        double_action.triggered.connect(lambda: self._change_quote_type(""", """, "" ""))
        quote_menu.addAction(double_action)

        # Curved single quotes
        single_action = QAction("' ' Virgolette Singole", self)
        single_action.triggered.connect(lambda: self._change_quote_type("'", "'", "' '"))
        quote_menu.addAction(single_action)

        # Straight double quotes
        straight_double_action = QAction('" " Virgolette Dritte Doppie', self)
        straight_double_action.triggered.connect(lambda: self._change_quote_type('"', '"', '" "'))
        quote_menu.addAction(straight_double_action)

        # Straight single quotes
        straight_single_action = QAction("' ' Virgolette Dritte Singole", self)
        straight_single_action.triggered.connect(lambda: self._change_quote_type("'", "'", "' '"))
        quote_menu.addAction(straight_single_action)

        self.quote_btn.setMenu(quote_menu)
        row2_layout.addWidget(self.quote_btn)
        self.toolbar_groups['special_chars'].append(self.quote_btn)

        # Store current quote type
        self.current_quote_open = "«"
        self.current_quote_close = "»"

        # Separator
        separator4 = QLabel("|")
        separator4.setStyleSheet(self._get_separator_style())
        row2_layout.addWidget(separator4)
        self.toolbar_groups['special_chars'].append(separator4)

        # Em dash button
        self.em_dash_btn = QPushButton("—")
        self.em_dash_btn.setToolTip("Insert Em Dash (Ctrl+Shift+-)")
        self.em_dash_btn.setShortcut(QKeySequence("Ctrl+Shift+-"))
        self.em_dash_btn.setFixedSize(32, 28)
        self.em_dash_btn.clicked.connect(lambda: self._insert_text("—"))
        self.em_dash_btn.setStyleSheet(self._get_button_style())
        row2_layout.addWidget(self.em_dash_btn)
        self.toolbar_groups['special_chars'].append(self.em_dash_btn)

        # En dash button
        self.en_dash_btn = QPushButton("–")
        self.en_dash_btn.setToolTip("Insert En Dash (Ctrl+-)")
        self.en_dash_btn.setShortcut(QKeySequence("Ctrl+-"))
        self.en_dash_btn.setFixedSize(32, 28)
        self.en_dash_btn.clicked.connect(lambda: self._insert_text("–"))
        self.en_dash_btn.setStyleSheet(self._get_button_style())
        row2_layout.addWidget(self.en_dash_btn)
        self.toolbar_groups['special_chars'].append(self.en_dash_btn)

        # Ellipsis button
        self.ellipsis_btn = QPushButton("…")
        self.ellipsis_btn.setToolTip("Insert Ellipsis")
        self.ellipsis_btn.setFixedSize(32, 28)
        self.ellipsis_btn.clicked.connect(lambda: self._insert_text("…"))
        self.ellipsis_btn.setStyleSheet(self._get_button_style())
        row2_layout.addWidget(self.ellipsis_btn)
        self.toolbar_groups['special_chars'].append(self.ellipsis_btn)

        # Table buttons (if enabled)
        if self.enable_tables:
            # Separator
            separator_table = QLabel("|")
            separator_table.setStyleSheet(self._get_separator_style())
            row2_layout.addWidget(separator_table)
            self.toolbar_groups['tables'].append(separator_table)

            # Insert table button
            self.insert_table_btn = QPushButton("⊞")
            self.insert_table_btn.setToolTip("Insert Table")
            self.insert_table_btn.setFixedSize(32, 28)
            self.insert_table_btn.clicked.connect(self._show_insert_table_dialog)
            colors = self._get_button_colors()
            self.insert_table_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {colors['bg']};
                    color: {colors['text']};
                    border: 1px solid {colors['border']};
                    border-radius: 3px;
                    font-size: 18px;
                }}
                QPushButton:hover {{
                    background-color: {colors['hover_bg']};
                }}
            """)
            row2_layout.addWidget(self.insert_table_btn)
            self.toolbar_groups['tables'].append(self.insert_table_btn)

            # Add row button
            self.add_row_btn = QPushButton("+R")
            self.add_row_btn.setToolTip("Add Row to Table")
            self.add_row_btn.setFixedSize(32, 28)
            self.add_row_btn.setEnabled(False)  # Enabled only when cursor is in table
            self.add_row_btn.clicked.connect(self._add_table_row)
            self.add_row_btn.setStyleSheet(self._get_button_style())
            row2_layout.addWidget(self.add_row_btn)
            self.toolbar_groups['tables'].append(self.add_row_btn)

            # Remove row button
            self.remove_row_btn = QPushButton("-R")
            self.remove_row_btn.setToolTip("Remove Current Row")
            self.remove_row_btn.setFixedSize(32, 28)
            self.remove_row_btn.setEnabled(False)
            self.remove_row_btn.clicked.connect(self._remove_table_row)
            self.remove_row_btn.setStyleSheet(self._get_button_style())
            row2_layout.addWidget(self.remove_row_btn)
            self.toolbar_groups['tables'].append(self.remove_row_btn)

            # Add column button
            self.add_col_btn = QPushButton("+C")
            self.add_col_btn.setToolTip("Add Column to Table")
            self.add_col_btn.setFixedSize(32, 28)
            self.add_col_btn.setEnabled(False)
            self.add_col_btn.clicked.connect(self._add_table_column)
            self.add_col_btn.setStyleSheet(self._get_button_style())
            row2_layout.addWidget(self.add_col_btn)
            self.toolbar_groups['tables'].append(self.add_col_btn)

            # Remove column button
            self.remove_col_btn = QPushButton("-C")
            self.remove_col_btn.setToolTip("Remove Current Column")
            self.remove_col_btn.setFixedSize(32, 28)
            self.remove_col_btn.setEnabled(False)
            self.remove_col_btn.clicked.connect(self._remove_table_column)
            self.remove_col_btn.setStyleSheet(self._get_button_style())
            row2_layout.addWidget(self.remove_col_btn)
            self.toolbar_groups['tables'].append(self.remove_col_btn)

            # Delete table button
            self.delete_table_btn = QPushButton("✕T")
            self.delete_table_btn.setToolTip("Delete Entire Table")
            self.delete_table_btn.setFixedSize(32, 28)
            self.delete_table_btn.setEnabled(False)
            self.delete_table_btn.clicked.connect(self._delete_table)
            colors = self._get_button_colors()
            self.delete_table_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {colors['bg']};
                    color: {colors['text']};
                    border: 1px solid {colors['border']};
                    border-radius: 3px;
                }}
                QPushButton:enabled:hover {{
                    background-color: #f44336;
                    color: white;
                }}
            """)
            row2_layout.addWidget(self.delete_table_btn)
            self.toolbar_groups['tables'].append(self.delete_table_btn)

        # Spacer at the end of ROW 2
        row2_layout.addStretch()

        # Add both rows to main layout
        main_layout.addLayout(row1_layout)
        main_layout.addLayout(row2_layout)

        return toolbar

    # FORMATTING METHODS

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

    def _toggle_strikethrough(self):
        """Toggle strikethrough formatting"""
        fmt = self.editor.currentCharFormat()
        fmt.setFontStrikeOut(self.strike_btn.isChecked())
        self.editor.setCurrentCharFormat(fmt)
        self.editor.setFocus()

    def _toggle_superscript(self):
        """Toggle superscript formatting"""
        fmt = self.editor.currentCharFormat()
        if self.superscript_btn.isChecked():
            if self.subscript_btn.isChecked():
                self.subscript_btn.setChecked(False)
            fmt.setVerticalAlignment(QTextCharFormat.VerticalAlignment.AlignSuperScript)
        else:
            fmt.setVerticalAlignment(QTextCharFormat.VerticalAlignment.AlignNormal)
        self.editor.setCurrentCharFormat(fmt)
        self.editor.setFocus()

    def _toggle_subscript(self):
        """Toggle subscript formatting"""
        fmt = self.editor.currentCharFormat()
        if self.subscript_btn.isChecked():
            if self.superscript_btn.isChecked():
                self.superscript_btn.setChecked(False)
            fmt.setVerticalAlignment(QTextCharFormat.VerticalAlignment.AlignSubScript)
        else:
            fmt.setVerticalAlignment(QTextCharFormat.VerticalAlignment.AlignNormal)
        self.editor.setCurrentCharFormat(fmt)
        self.editor.setFocus()

    def _toggle_smallcaps(self):
        """Toggle small caps formatting"""
        fmt = self.editor.currentCharFormat()
        if self.smallcaps_btn.isChecked():
            fmt.setFontCapitalization(QFont.Capitalization.SmallCaps)
        else:
            fmt.setFontCapitalization(QFont.Capitalization.MixedCase)
        self.editor.setCurrentCharFormat(fmt)
        self.editor.setFocus()

    def _set_alignment(self, alignment):
        """Set text alignment"""
        self.editor.setAlignment(alignment)
        # Update button states
        self.align_left_btn.setChecked(alignment == Qt.AlignmentFlag.AlignLeft)
        self.align_center_btn.setChecked(alignment == Qt.AlignmentFlag.AlignCenter)
        self.align_right_btn.setChecked(alignment == Qt.AlignmentFlag.AlignRight)
        self.align_justify_btn.setChecked(alignment == Qt.AlignmentFlag.AlignJustify)
        self.editor.setFocus()

    def _insert_text(self, text):
        """Insert text at cursor position"""
        cursor = self.editor.textCursor()
        cursor.insertText(text)
        self.editor.setFocus()

    def _insert_quotes(self, open_quote, close_quote):
        """Insert quote marks and position cursor inside"""
        cursor = self.editor.textCursor()

        if cursor.hasSelection():
            selected_text = cursor.selectedText()
            cursor.insertText(f"{open_quote}{selected_text}{close_quote}")
        else:
            cursor.insertText(f"{open_quote}{close_quote}")
            cursor.movePosition(QTextCursor.MoveOperation.Left, QTextCursor.MoveMode.MoveAnchor, len(close_quote))
            self.editor.setTextCursor(cursor)

        self.editor.setFocus()

    def _insert_current_quotes(self):
        """Insert quotes using the currently selected quote type"""
        self._insert_quotes(self.current_quote_open, self.current_quote_close)

    def _change_quote_type(self, open_quote, close_quote, display_text):
        """
        Change the current quote type and update button display

        Args:
            open_quote: Opening quote character
            close_quote: Closing quote character
            display_text: Text to display on button
        """
        self.current_quote_open = open_quote
        self.current_quote_close = close_quote
        self.quote_btn.setText(display_text)
        self._insert_quotes(open_quote, close_quote)

    def _show_keyboard_shortcuts(self):
        """Show keyboard shortcuts dialog"""
        from ui.dialogs import KeyboardShortcutsDialog
        dialog = KeyboardShortcutsDialog(self)
        dialog.exec()

    # TABLE METHODS

    def _show_insert_table_dialog(self):
        """Show dialog to insert a new table"""
        from ui.dialogs import InsertTableDialog
        dialog = InsertTableDialog(self)
        if dialog.exec():
            rows = dialog.get_rows()
            cols = dialog.get_columns()
            self._insert_table(rows, cols)

    def _insert_table(self, rows, cols):
        """
        Insert a new table at cursor position

        Args:
            rows: Number of rows
            cols: Number of columns
        """
        cursor = self.editor.textCursor()

        # Create table format
        table_format = QTextTableFormat()
        table_format.setBorder(1)
        table_format.setBorderStyle(QTextTableFormat.BorderStyle.BorderStyle_Solid)
        table_format.setCellPadding(4)
        table_format.setCellSpacing(0)
        table_format.setAlignment(Qt.AlignmentFlag.AlignLeft)

        # Insert table
        cursor.insertTable(rows, cols, table_format)
        self.editor.setFocus()

    def _is_cursor_in_table(self):
        """
        Check if cursor is inside a table

        Returns:
            bool: True if cursor is in a table
        """
        cursor = self.editor.textCursor()
        return cursor.currentTable() is not None

    def _add_table_row(self):
        """Add a row to the current table"""
        cursor = self.editor.textCursor()
        table = cursor.currentTable()
        if table:
            current_row = table.cellAt(cursor).row()
            table.insertRows(current_row + 1, 1)
            self.editor.setFocus()

    def _remove_table_row(self):
        """Remove the current row from the table"""
        cursor = self.editor.textCursor()
        table = cursor.currentTable()
        if table and table.rows() > 1:  # Don't remove if only one row
            current_row = table.cellAt(cursor).row()
            table.removeRows(current_row, 1)
            self.editor.setFocus()

    def _add_table_column(self):
        """Add a column to the current table"""
        cursor = self.editor.textCursor()
        table = cursor.currentTable()
        if table:
            current_col = table.cellAt(cursor).column()
            table.insertColumns(current_col + 1, 1)
            self.editor.setFocus()

    def _remove_table_column(self):
        """Remove the current column from the table"""
        cursor = self.editor.textCursor()
        table = cursor.currentTable()
        if table and table.columns() > 1:  # Don't remove if only one column
            current_col = table.cellAt(cursor).column()
            table.removeColumns(current_col, 1)
            self.editor.setFocus()

    def _delete_table(self):
        """Delete the entire table"""
        cursor = self.editor.textCursor()
        table = cursor.currentTable()
        if table:
            # Select entire table
            first_cell = table.cellAt(0, 0)
            last_cell = table.cellAt(table.rows() - 1, table.columns() - 1)

            cursor.setPosition(first_cell.firstPosition())
            cursor.setPosition(last_cell.lastPosition(), QTextCursor.MoveMode.KeepAnchor)

            # Delete table
            cursor.currentTable().remove()
            cursor.removeSelectedText()
            self.editor.setFocus()

    # ICON AND STYLING METHODS

    def _create_alignment_icon(self, alignment_type):
        """
        Create an icon representing text alignment with horizontal lines

        Args:
            alignment_type: 'left', 'center', 'right', or 'justify'

        Returns:
            QIcon with visual representation of alignment
        """
        pixmap = QPixmap(24, 24)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        pen = QPen(QColor(60, 60, 60))
        pen.setWidth(2)
        painter.setPen(pen)

        if alignment_type == 'left':
            lines = [
                (2, 6, 20, 6),
                (2, 11, 14, 11),
                (2, 16, 18, 16),
            ]
        elif alignment_type == 'center':
            lines = [
                (2, 6, 22, 6),
                (5, 11, 19, 11),
                (4, 16, 20, 16),
            ]
        elif alignment_type == 'right':
            lines = [
                (4, 6, 22, 6),
                (10, 11, 22, 11),
                (6, 16, 22, 16),
            ]
        else:  # justify
            lines = [
                (2, 6, 22, 6),
                (2, 11, 22, 11),
                (2, 16, 22, 16),
            ]

        for x1, y1, x2, y2 in lines:
            painter.drawLine(x1, y1, x2, y2)

        painter.end()
        return QIcon(pixmap)

    def _get_button_style(self):
        """Get standard button stylesheet with dynamic colors"""
        colors = self._get_button_colors()
        return f"""
            QPushButton {{
                background-color: {colors['bg']};
                color: {colors['text']};
                border: 1px solid {colors['border']};
                border-radius: 3px;
            }}
            QPushButton:checked {{
                background-color: #607D8B;
                color: white;
            }}
            QPushButton:hover {{
                background-color: {colors['hover_bg']};
            }}
        """

    def _get_custom_button_style(self, checked_color: str):
        """Get button stylesheet with custom checked color"""
        colors = self._get_button_colors()
        return f"""
            QPushButton {{
                background-color: {colors['bg']};
                color: {colors['text']};
                border: 1px solid {colors['border']};
                border-radius: 3px;
            }}
            QPushButton:checked {{
                background-color: {checked_color};
                color: white;
            }}
            QPushButton:hover {{
                background-color: {colors['hover_bg']};
            }}
        """

    def _get_toolbutton_style(self):
        """Get QToolButton stylesheet with dynamic colors"""
        colors = self._get_button_colors()
        return f"""
            QToolButton {{
                background-color: {colors['bg']};
                color: {colors['text']};
                border: 1px solid {colors['border']};
                border-radius: 3px;
                padding: 2px;
            }}
            QToolButton:hover {{
                background-color: {colors['hover_bg']};
            }}
            QToolButton::menu-button {{
                border: none;
                width: 12px;
            }}
        """

    def _get_separator_style(self):
        """Get separator stylesheet with dynamic colors"""
        colors = self._get_button_colors()
        separator_color = '#555555' if self._is_dark_mode() else '#CCCCCC'
        return f"color: {separator_color}; padding: 0 5px;"

    def _update_format_buttons(self):
        """Update format buttons state based on current cursor position"""
        if not self.show_toolbar:
            return

        fmt = self.editor.currentCharFormat()

        # Block signals to avoid triggering the toggle actions
        self.bold_btn.blockSignals(True)
        self.italic_btn.blockSignals(True)
        self.underline_btn.blockSignals(True)
        self.strike_btn.blockSignals(True)
        self.superscript_btn.blockSignals(True)
        self.subscript_btn.blockSignals(True)
        self.smallcaps_btn.blockSignals(True)

        # Update button states
        self.bold_btn.setChecked(fmt.fontWeight() == QFont.Weight.Bold)
        self.italic_btn.setChecked(fmt.fontItalic())
        self.underline_btn.setChecked(fmt.fontUnderline())
        self.strike_btn.setChecked(fmt.fontStrikeOut())

        # Superscript/Subscript
        valign = fmt.verticalAlignment()
        self.superscript_btn.setChecked(valign == QTextCharFormat.VerticalAlignment.AlignSuperScript)
        self.subscript_btn.setChecked(valign == QTextCharFormat.VerticalAlignment.AlignSubScript)

        # Small Caps
        self.smallcaps_btn.setChecked(fmt.fontCapitalization() == QFont.Capitalization.SmallCaps)

        # Unblock signals
        self.bold_btn.blockSignals(False)
        self.italic_btn.blockSignals(False)
        self.underline_btn.blockSignals(False)
        self.strike_btn.blockSignals(False)
        self.superscript_btn.blockSignals(False)
        self.subscript_btn.blockSignals(False)
        self.smallcaps_btn.blockSignals(False)

        # Update alignment buttons
        alignment = self.editor.alignment()
        self.align_left_btn.setChecked(alignment == Qt.AlignmentFlag.AlignLeft)
        self.align_center_btn.setChecked(alignment == Qt.AlignmentFlag.AlignCenter)
        self.align_right_btn.setChecked(alignment == Qt.AlignmentFlag.AlignRight)
        self.align_justify_btn.setChecked(alignment == Qt.AlignmentFlag.AlignJustify)

        # Update table buttons state (enable/disable based on cursor position)
        if self.enable_tables:
            in_table = self._is_cursor_in_table()
            self.add_row_btn.setEnabled(in_table)
            self.remove_row_btn.setEnabled(in_table)
            self.add_col_btn.setEnabled(in_table)
            self.remove_col_btn.setEnabled(in_table)
            self.delete_table_btn.setEnabled(in_table)

    def _update_counter(self):
        """Update word and character counter"""
        if not self.show_counter:
            return

        text = self.editor.toPlainText()
        words = len(text.split()) if text.strip() else 0
        characters = len(text)
        self.counter_info.setText(f"Words: {words} | Characters: {characters}")

    # ERROR HIGHLIGHTING METHODS

    def highlight_errors(self, errors):
        """
        Highlight errors in the editor using ExtraSelections

        Args:
            errors: List of error dictionaries
        """
        self.grammar_extra_selections = []

        if not errors:
            self._update_extra_selections()
            return

        try:
            document = self.editor.document()
            if not document:
                return

            for error in errors:
                try:
                    selection = self._create_error_selection(error, document)
                    if selection:
                        self.grammar_extra_selections.append(selection)
                except Exception as e:
                    print(f"Warning: Could not highlight error: {e}")
                    continue

            self._update_extra_selections()

        except Exception as e:
            print(f"Error in highlight_errors: {e}")

    def _create_error_selection(self, error, document):
        """Create an ExtraSelection for an error without affecting text formatting"""
        start = error.get('start', 0)
        end = error.get('end', 0)

        text_length = len(self.editor.toPlainText())
        if start < 0 or end > text_length or start >= end:
            return None

        cursor = QTextCursor(document)
        cursor.setPosition(start)
        cursor.setPosition(end, QTextCursor.MoveMode.KeepAnchor)

        selection = QTextEdit.ExtraSelection()
        selection.cursor = cursor

        color = self._get_category_color(error.get('category', 'custom'))
        selection.format.setUnderlineColor(color)
        # Use SingleUnderline for better visibility (thicker line)
        selection.format.setUnderlineStyle(QTextCharFormat.UnderlineStyle.SingleUnderline)

        # Add semi-transparent background for even better visibility
        bg_color = QColor(color)
        bg_color.setAlpha(30)  # Very light background (30/255 transparency)
        selection.format.setBackground(bg_color)

        return selection

    def _update_extra_selections(self):
        """Update all ExtraSelections (grammar + spell check)"""
        all_selections = self.grammar_extra_selections.copy()

        if hasattr(self.editor, 'get_spell_check_selections'):
            spell_selections = self.editor.get_spell_check_selections()
            if spell_selections:
                all_selections.extend(spell_selections)

        self.editor.setExtraSelections(all_selections)

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
        """Clear all grammar highlights"""
        try:
            self.grammar_extra_selections = []
            self._update_extra_selections()
            self.error_highlights = []
        except Exception as e:
            print(f"Error clearing highlights: {e}")

    # PUBLIC API METHODS

    def get_text(self):
        """Get rich text (HTML) from the editor"""
        return self.editor.toHtml()

    def get_plain_text(self):
        """Get plain text from the editor (without formatting)"""
        return self.editor.toPlainText()

    def set_text(self, text):
        """
        Set text in the editor (supports both plain text and HTML)

        Args:
            text: Content to set (HTML or plain text)
        """
        if not text:
            self.editor.clear()
        else:
            text_stripped = text.strip()
            is_html = (
                text_stripped.startswith('<!DOCTYPE') or
                text_stripped.startswith('<html') or
                '<p style=' in text or
                '<span style=' in text or
                ('<p>' in text and '</p>' in text) or
                ('</b>' in text or '</i>' in text or '</u>' in text) or
                '<table' in text  # Check for tables
            )

            if is_html:
                self.editor.setHtml(text)
            else:
                self.editor.setPlainText(text)

        if self.show_counter:
            self._update_counter()

    def eventFilter(self, obj, event):
        """
        Event filter to handle TAB navigation in tables

        Args:
            obj: Object that triggered the event
            event: Event to filter

        Returns:
            bool: True if event was handled, False otherwise
        """
        if obj == self.editor and event.type() == QEvent.Type.KeyPress:
            key_event = event

            # Handle TAB and Shift+TAB in tables
            if key_event.key() == Qt.Key.Key_Tab or key_event.key() == Qt.Key.Key_Backtab:
                cursor = self.editor.textCursor()
                table = cursor.currentTable()

                if table:
                    # Get current cell position
                    cell = table.cellAt(cursor)
                    current_row = cell.row()
                    current_col = cell.column()

                    # Determine next cell based on key
                    if key_event.key() == Qt.Key.Key_Tab:
                        # TAB: Move to next cell (right, or next row)
                        next_col = current_col + 1
                        next_row = current_row

                        if next_col >= table.columns():
                            # End of row, move to next row
                            next_col = 0
                            next_row = current_row + 1

                            if next_row >= table.rows():
                                # End of table, add new row
                                table.insertRows(table.rows(), 1)
                                next_row = table.rows() - 1
                    else:
                        # SHIFT+TAB: Move to previous cell (left, or previous row)
                        next_col = current_col - 1
                        next_row = current_row

                        if next_col < 0:
                            # Beginning of row, move to previous row
                            next_row = current_row - 1

                            if next_row < 0:
                                # Beginning of table, stay at first cell
                                next_row = 0
                                next_col = 0
                            else:
                                next_col = table.columns() - 1

                    # Move cursor to next cell
                    next_cell = table.cellAt(next_row, next_col)
                    cursor.setPosition(next_cell.firstPosition())
                    self.editor.setTextCursor(cursor)

                    # Event handled
                    return True

        # Let the event propagate
        return super().eventFilter(obj, event)

    def clear(self):
        """Clear the editor"""
        try:
            self.clear_highlights()
            self.editor.clear()
            if self.show_counter:
                self._update_counter()
        except Exception as e:
            print(f"Error in clear: {e}")

    def set_toolbar_group_visibility(self, group_name: str, visible: bool):
        """
        Show or hide a toolbar group

        Args:
            group_name: Group name ('script', 'smallcaps', 'alignment', 'special_chars', 'tables')
            visible: True to show, False to hide
        """
        if group_name in self.toolbar_groups:
            for widget in self.toolbar_groups[group_name]:
                widget.setVisible(visible)
