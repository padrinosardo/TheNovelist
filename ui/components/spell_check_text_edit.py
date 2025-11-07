"""
Spell Check Text Edit - QTextEdit with spell checking context menu
"""
from PySide6.QtWidgets import QTextEdit, QMenu
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QTextCursor, QAction, QContextMenuEvent, QMouseEvent, QTextCharFormat, QColor
from spellchecker import SpellChecker
import re


class SpellCheckTextEdit(QTextEdit):
    """
    QTextEdit with integrated spell checking and context menu for suggestions
    Uses ExtraSelections instead of QSyntaxHighlighter to preserve user formatting
    """

    # Signal emitted when a word is added to the custom dictionary
    word_added_to_dictionary = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        # Initialize spell checker (no highlighter - we use ExtraSelections)
        self.spell_checker = SpellChecker(language='it')
        self.custom_words = set()
        self._spell_check_enabled = True
        self.spell_check_selections = []  # Store spell check selections

        # UI language (default: Italian)
        self._ui_language = 'it'

        # Disable default context menu to use our custom one
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)

        # Timer to delay spell checking (avoids checking on every keystroke)
        self.spell_check_timer = QTimer()
        self.spell_check_timer.setSingleShot(True)
        self.spell_check_timer.timeout.connect(self._perform_spell_check)

        # Connect to text changes
        self.textChanged.connect(self._on_text_changed)

    def _on_text_changed(self):
        """Handle text changes - schedule spell check"""
        if self._spell_check_enabled:
            # Delay spell checking by 500ms to avoid checking on every keystroke
            self.spell_check_timer.stop()
            self.spell_check_timer.start(500)

    def _perform_spell_check(self):
        """Perform spell checking using ExtraSelections (preserves user formatting)"""
        self.spell_check_selections = []

        if not self._spell_check_enabled:
            self._notify_selections_updated()
            return

        # Get document text
        text = self.toPlainText()

        # Find all words
        word_pattern = re.compile(r"\b[\w']+\b")
        for match in word_pattern.finditer(text):
            word = match.group(0)
            start = match.start()
            length = len(word)

            # Skip if word is a number or too short
            if word.isdigit() or len(word) < 2:
                continue

            # Skip if word is all uppercase (acronyms)
            if word.isupper() and len(word) > 1:
                continue

            # Skip if word starts with uppercase (proper noun)
            if word[0].isupper():
                continue

            # Check spelling
            word_lower = word.lower()

            # Skip if in custom dictionary
            if word_lower in self.custom_words:
                continue

            # Check if misspelled
            if self.spell_checker.unknown([word_lower]):
                # Create selection for this misspelled word
                cursor = QTextCursor(self.document())
                cursor.setPosition(start)
                cursor.setPosition(start + length, QTextCursor.MoveMode.KeepAnchor)

                # Create format for underline (does NOT affect text formatting)
                selection = QTextEdit.ExtraSelection()
                selection.cursor = cursor
                underline_color = QColor(255, 0, 0)
                selection.format.setUnderlineColor(underline_color)
                # Use SingleUnderline for better visibility (thicker line)
                selection.format.setUnderlineStyle(QTextCharFormat.UnderlineStyle.SingleUnderline)

                # Add semi-transparent background for even better visibility
                bg_color = QColor(underline_color)
                bg_color.setAlpha(30)  # Very light background (30/255 transparency)
                selection.format.setBackground(bg_color)

                self.spell_check_selections.append(selection)

        # Notify parent to update all selections
        self._notify_selections_updated()

    def _notify_selections_updated(self):
        """Notify parent TextEditor to update all ExtraSelections"""
        # Try to find parent TextEditor and call its update method
        parent = self.parent()
        while parent:
            if hasattr(parent, '_update_extra_selections'):
                parent._update_extra_selections()
                break
            parent = parent.parent()

    def get_spell_check_selections(self):
        """Get current spell check ExtraSelections"""
        return self.spell_check_selections

    def enable_spell_checking(self, language='it'):
        """
        Enable spell checking with the specified language

        Args:
            language: Language code (e.g., 'it', 'en', 'es')
        """
        self.spell_checker = SpellChecker(language=language)
        self._spell_check_enabled = True
        self._perform_spell_check()

    def disable_spell_checking(self):
        """Disable spell checking"""
        self._spell_check_enabled = False
        self.spell_check_selections = []

    def is_spell_checking_enabled(self) -> bool:
        """Check if spell checking is enabled"""
        return self._spell_check_enabled

    def add_word_to_dictionary(self, word: str):
        """
        Add a word to the custom dictionary

        Args:
            word: Word to add
        """
        word_lower = word.lower()
        self.custom_words.add(word_lower)
        self.word_added_to_dictionary.emit(word)
        # Refresh spell checking to remove underline
        self._perform_spell_check()

    def is_word_misspelled(self, word: str) -> bool:
        """
        Check if a word is misspelled

        Args:
            word: Word to check

        Returns:
            bool: True if misspelled
        """
        if not word or len(word) < 2:
            return False

        word_lower = word.lower()

        # Skip if in custom dictionary
        if word_lower in self.custom_words:
            return False

        # Check with spell checker
        return bool(self.spell_checker.unknown([word_lower]))

    def get_suggestions(self, word: str, max_suggestions: int = 5) -> list:
        """
        Get spelling suggestions for a misspelled word

        Args:
            word: Misspelled word
            max_suggestions: Maximum number of suggestions

        Returns:
            list: List of suggestions
        """
        word_lower = word.lower()
        candidates = self.spell_checker.candidates(word_lower)
        if candidates:
            return list(candidates)[:max_suggestions]
        return []

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

        # Get UI labels
        ui_labels = self._get_ui_labels()

        # Get cursor at position
        cursor = self.cursorForPosition(position)

        # Get word under cursor
        word, word_cursor = self._get_word_under_cursor(cursor)

        # Check if spell checking is enabled and word is misspelled
        if (self._spell_check_enabled and
            word and
            len(word) > 1 and
            not word[0].isupper()):  # Only show suggestions for non-proper nouns

            # Check if word is actually misspelled
            if self.is_word_misspelled(word):
                # Add suggestions
                suggestions = self.get_suggestions(word)

                if suggestions:
                    # Add header
                    header = QAction(f"{ui_labels['suggestions_for']} '{word}':", self)
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
                        # QAction doesn't support setStyleSheet in PySide6
                        menu.addAction(action)

                    menu.addSeparator()

                # Add "Add to dictionary" option
                add_to_dict_action = QAction(f"➕ {ui_labels['add_to_dict']} '{word}' {ui_labels['to_dictionary']}", self)
                add_to_dict_action.triggered.connect(
                    lambda: self.add_word_to_dictionary(word)
                )
                menu.addAction(add_to_dict_action)

                menu.addSeparator()

        # Add standard edit actions
        undo_action = menu.addAction(ui_labels['undo'])
        undo_action.triggered.connect(self.undo)
        undo_action.setEnabled(self.document().isUndoAvailable())

        redo_action = menu.addAction(ui_labels['redo'])
        redo_action.triggered.connect(self.redo)
        redo_action.setEnabled(self.document().isRedoAvailable())

        menu.addSeparator()

        cut_action = menu.addAction(ui_labels['cut'])
        cut_action.triggered.connect(self.cut)
        cut_action.setEnabled(self.textCursor().hasSelection())

        copy_action = menu.addAction(ui_labels['copy'])
        copy_action.triggered.connect(self.copy)
        copy_action.setEnabled(self.textCursor().hasSelection())

        paste_action = menu.addAction(ui_labels['paste'])
        paste_action.triggered.connect(self.paste)

        menu.addSeparator()

        select_all_action = menu.addAction(ui_labels['select_all'])
        select_all_action.triggered.connect(self.selectAll)

        # Add spell checking toggle
        menu.addSeparator()
        toggle_spell_check = QAction(
            ui_labels['spell_check_on'] if self.is_spell_checking_enabled()
            else ui_labels['spell_check_off'],
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
        if self._spell_check_enabled:
            self.disable_spell_checking()
        else:
            self.enable_spell_checking(self._ui_language)

    def set_language(self, language: str):
        """
        Set the spell checking language

        Args:
            language: Language code (e.g., 'it', 'en', 'es')
        """
        self._ui_language = language
        self.spell_checker = SpellChecker(language=language)
        if self._spell_check_enabled:
            self._perform_spell_check()

    def add_words_to_dictionary(self, words: list):
        """
        Add multiple words to the custom dictionary

        Args:
            words: List of words to add
        """
        for word in words:
            word_lower = word.lower()
            self.custom_words.add(word_lower)
        # Refresh spell checking
        if self._spell_check_enabled:
            self._perform_spell_check()

    def set_ui_language(self, language: str):
        """
        Set the UI language for context menus

        Args:
            language: Language code (e.g., 'it', 'en', 'es', 'fr', 'de')
        """
        self._ui_language = language

    def _get_ui_labels(self) -> dict:
        """
        Get UI labels translated to the current UI language

        Returns:
            dict: Dictionary of translated labels
        """
        labels = {
            'it': {
                'suggestions_for': 'Suggerimenti per',
                'add_to_dict': 'Aggiungi',
                'to_dictionary': 'al dizionario',
                'undo': 'Annulla',
                'redo': 'Ripeti',
                'cut': 'Taglia',
                'copy': 'Copia',
                'paste': 'Incolla',
                'select_all': 'Seleziona tutto',
                'spell_check_on': '☑ Controllo ortografia',
                'spell_check_off': '☐ Controllo ortografia'
            },
            'en': {
                'suggestions_for': 'Suggestions for',
                'add_to_dict': 'Add',
                'to_dictionary': 'to dictionary',
                'undo': 'Undo',
                'redo': 'Redo',
                'cut': 'Cut',
                'copy': 'Copy',
                'paste': 'Paste',
                'select_all': 'Select All',
                'spell_check_on': '☑ Spell Check',
                'spell_check_off': '☐ Spell Check'
            },
            'es': {
                'suggestions_for': 'Sugerencias para',
                'add_to_dict': 'Agregar',
                'to_dictionary': 'al diccionario',
                'undo': 'Deshacer',
                'redo': 'Rehacer',
                'cut': 'Cortar',
                'copy': 'Copiar',
                'paste': 'Pegar',
                'select_all': 'Seleccionar Todo',
                'spell_check_on': '☑ Revisión Ortográfica',
                'spell_check_off': '☐ Revisión Ortográfica'
            },
            'fr': {
                'suggestions_for': 'Suggestions pour',
                'add_to_dict': 'Ajouter',
                'to_dictionary': 'au dictionnaire',
                'undo': 'Annuler',
                'redo': 'Rétablir',
                'cut': 'Couper',
                'copy': 'Copier',
                'paste': 'Coller',
                'select_all': 'Tout Sélectionner',
                'spell_check_on': '☑ Vérification Orthographique',
                'spell_check_off': '☐ Vérification Orthographique'
            },
            'de': {
                'suggestions_for': 'Vorschläge für',
                'add_to_dict': 'Hinzufügen',
                'to_dictionary': 'zum Wörterbuch',
                'undo': 'Rückgängig',
                'redo': 'Wiederholen',
                'cut': 'Ausschneiden',
                'copy': 'Kopieren',
                'paste': 'Einfügen',
                'select_all': 'Alles Auswählen',
                'spell_check_on': '☑ Rechtschreibprüfung',
                'spell_check_off': '☐ Rechtschreibprüfung'
            }
        }
        return labels.get(self._ui_language, labels['en'])

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
