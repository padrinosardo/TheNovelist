"""
Spell Check Text Edit - QTextEdit with spell checking context menu
"""
from PySide6.QtWidgets import QTextEdit, QMenu
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QTextCursor, QAction, QContextMenuEvent, QMouseEvent
from ui.components.spell_check_highlighter import SpellCheckHighlighter


class SpellCheckTextEdit(QTextEdit):
    """
    QTextEdit with integrated spell checking and context menu for suggestions
    """

    # Signal emitted when a word is added to the custom dictionary
    word_added_to_dictionary = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        # Initialize spell checker highlighter
        self.spell_highlighter = None

        # Disable default context menu to use our custom one
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)

    def enable_spell_checking(self, language='it'):
        """
        Enable spell checking with the specified language

        Args:
            language: Language code (e.g., 'it', 'en', 'es')
        """
        if self.spell_highlighter is None:
            self.spell_highlighter = SpellCheckHighlighter(self.document(), language)
        else:
            self.spell_highlighter.set_language(language)
            self.spell_highlighter.set_enabled(True)

    def disable_spell_checking(self):
        """Disable spell checking"""
        if self.spell_highlighter:
            self.spell_highlighter.set_enabled(False)

    def is_spell_checking_enabled(self) -> bool:
        """Check if spell checking is enabled"""
        return self.spell_highlighter and self.spell_highlighter.is_enabled()

    def add_word_to_dictionary(self, word: str):
        """
        Add a word to the custom dictionary

        Args:
            word: Word to add
        """
        if self.spell_highlighter:
            self.spell_highlighter.add_word_to_dictionary(word)
            self.word_added_to_dictionary.emit(word)

    def _get_word_under_cursor(self, cursor: QTextCursor = None) -> tuple:
        """
        Get the word under the cursor

        Args:
            cursor: Text cursor (uses current cursor if None)

        Returns:
            Tuple of (word, cursor_with_word_selected)
        """
        if cursor is None:
            cursor = self.textCursor()

        # Move to start of word
        cursor.select(QTextCursor.SelectionType.WordUnderCursor)
        word = cursor.selectedText()

        return word, cursor

    def _show_context_menu(self, position):
        """
        Show context menu with spell checking suggestions

        Args:
            position: Position where the menu was requested (QPoint in widget coordinates)
        """
        # Create context menu
        menu = QMenu(self)

        # Get cursor at position
        cursor = self.cursorForPosition(position)

        # Get word under cursor
        word, word_cursor = self._get_word_under_cursor(cursor)

        # Check if spell checking is enabled and word is misspelled
        if (self.spell_highlighter and
            self.spell_highlighter.is_enabled() and
            word and
            len(word) > 1 and
            not word[0].isupper()):  # Only show suggestions for non-proper nouns

            # Check if word is actually misspelled
            if self.spell_highlighter.is_word_misspelled(word):
                # Add suggestions
                suggestions = self.spell_highlighter.get_suggestions(word)

                if suggestions:
                    # Add header
                    header = QAction(f"Suggerimenti per '{word}':", self)
                    header.setEnabled(False)
                    menu.addAction(header)

                    # Limit to top 5 suggestions
                    for suggestion in suggestions[:5]:
                        action = QAction(f"  ✓  {suggestion}", self)
                        # Capture word and suggestion
                        action.triggered.connect(
                            lambda checked=False, s=suggestion, w=word:
                            self._replace_current_word(w, s)
                        )
                        action.setStyleSheet("font-weight: bold; color: #2196F3;")
                        menu.addAction(action)

                    menu.addSeparator()

                # Add "Add to dictionary" option
                add_to_dict_action = QAction(f"➕ Aggiungi '{word}' al dizionario", self)
                add_to_dict_action.triggered.connect(
                    lambda: self.add_word_to_dictionary(word)
                )
                menu.addAction(add_to_dict_action)

                menu.addSeparator()

        # Add standard edit actions
        undo_action = menu.addAction("Annulla")
        undo_action.triggered.connect(self.undo)
        undo_action.setEnabled(self.document().isUndoAvailable())

        redo_action = menu.addAction("Ripeti")
        redo_action.triggered.connect(self.redo)
        redo_action.setEnabled(self.document().isRedoAvailable())

        menu.addSeparator()

        cut_action = menu.addAction("Taglia")
        cut_action.triggered.connect(self.cut)
        cut_action.setEnabled(self.textCursor().hasSelection())

        copy_action = menu.addAction("Copia")
        copy_action.triggered.connect(self.copy)
        copy_action.setEnabled(self.textCursor().hasSelection())

        paste_action = menu.addAction("Incolla")
        paste_action.triggered.connect(self.paste)

        menu.addSeparator()

        select_all_action = menu.addAction("Seleziona tutto")
        select_all_action.triggered.connect(self.selectAll)

        # Add spell checking toggle
        if self.spell_highlighter:
            menu.addSeparator()
            toggle_spell_check = QAction(
                "☑ Controllo ortografia" if self.is_spell_checking_enabled()
                else "☐ Controllo ortografia",
                self
            )
            toggle_spell_check.triggered.connect(self._toggle_spell_checking)
            menu.addAction(toggle_spell_check)

        # Show menu at global position
        global_pos = self.mapToGlobal(position)
        menu.exec_(global_pos)

    def _replace_word(self, cursor: QTextCursor, new_word: str):
        """
        Replace word at cursor position with new word

        Args:
            cursor: Cursor with word selected
            new_word: Word to replace with
        """
        cursor.beginEditBlock()
        cursor.removeSelectedText()
        cursor.insertText(new_word)
        cursor.endEditBlock()

    def _replace_word_at_position(self, position, new_word: str):
        """
        Replace word at a specific position with new word

        Args:
            position: QPoint position in the widget
            new_word: Word to replace with
        """
        cursor = self.cursorForPosition(position)
        cursor.select(QTextCursor.SelectionType.WordUnderCursor)

        cursor.beginEditBlock()
        cursor.removeSelectedText()
        cursor.insertText(new_word)
        cursor.endEditBlock()

    def _replace_current_word(self, old_word: str, new_word: str):
        """
        Replace the word under cursor that matches old_word

        Args:
            old_word: Word to find and replace
            new_word: Word to replace with
        """
        cursor = self.textCursor()
        cursor.select(QTextCursor.SelectionType.WordUnderCursor)

        selected_text = cursor.selectedText()
        # Only replace if the selected word matches (case-insensitive)
        if selected_text.lower() == old_word.lower():
            cursor.beginEditBlock()
            cursor.removeSelectedText()
            cursor.insertText(new_word)
            cursor.endEditBlock()
            # Update cursor position
            self.setTextCursor(cursor)

    def _toggle_spell_checking(self):
        """Toggle spell checking on/off"""
        if self.spell_highlighter:
            if self.spell_highlighter.is_enabled():
                self.disable_spell_checking()
            else:
                self.spell_highlighter.set_enabled(True)

    def set_language(self, language: str):
        """
        Set the spell checking language

        Args:
            language: Language code (e.g., 'it', 'en', 'es')
        """
        if self.spell_highlighter:
            self.spell_highlighter.set_language(language)
        else:
            self.enable_spell_checking(language)

    def add_words_to_dictionary(self, words: list):
        """
        Add multiple words to the custom dictionary

        Args:
            words: List of words to add
        """
        if self.spell_highlighter:
            self.spell_highlighter.add_words_to_dictionary(words)

    def mousePressEvent(self, event: QMouseEvent):
        """
        Override mouse press event to handle right-click

        Args:
            event: Mouse event
        """
        # Check for right-click (or Control+click on Mac)
        if event.button() == Qt.MouseButton.RightButton:
            event.accept()
            self._show_context_menu(event.pos())
        else:
            # Pass other mouse events to parent
            super().mousePressEvent(event)

    def contextMenuEvent(self, event: QContextMenuEvent):
        """
        Override context menu event to show custom spell checking menu
        This works better with Mac trackpad than customContextMenuRequested signal

        Args:
            event: Context menu event
        """
        # Always show our custom menu instead of the default one
        event.accept()  # Accept the event to prevent default menu
        self._show_context_menu(event.pos())
