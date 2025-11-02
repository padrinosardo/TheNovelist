"""
Spell Check Highlighter - Real-time spell checking with red wavy underline
"""
from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
from PySide6.QtCore import Qt, QRegularExpression
from spellchecker import SpellChecker
import re


class SpellCheckHighlighter(QSyntaxHighlighter):
    """
    Syntax highlighter that underlines misspelled words in real-time
    Uses PySpellChecker for spell checking
    """

    def __init__(self, document, language='it'):
        super().__init__(document)

        # Initialize spell checker
        self.spell_checker = SpellChecker(language=language)

        # Custom dictionary for project-specific terms
        self.custom_words = set()

        # Format for misspelled words (red wavy underline)
        self.error_format = QTextCharFormat()
        self.error_format.setUnderlineColor(QColor(255, 0, 0))  # Red
        self.error_format.setUnderlineStyle(QTextCharFormat.UnderlineStyle.WaveUnderline)

        # Enabled state
        self._enabled = True

        # Word pattern (letters, apostrophes for contractions)
        self.word_pattern = QRegularExpression(r"\b[\w']+\b")

    def highlightBlock(self, text):
        """
        Highlight misspelled words in the given text block

        Args:
            text: Text block to check
        """
        if not self._enabled:
            return

        # Find all words in the text
        iterator = self.word_pattern.globalMatch(text)

        while iterator.hasNext():
            match = iterator.next()
            word = match.captured(0)
            start = match.capturedStart(0)
            length = match.capturedLength(0)

            # Skip if word is a number or too short
            if word.isdigit() or len(word) < 2:
                continue

            # Skip if word is all uppercase (acronyms like IA, GPS, etc.)
            if word.isupper() and len(word) > 1:
                continue

            # Skip if word starts with uppercase (likely proper noun)
            # Always skip proper nouns regardless of position
            if word[0].isupper():
                continue

            # Check spelling
            word_lower = word.lower()

            # Skip if in custom dictionary
            if word_lower in self.custom_words:
                continue

            # Check if misspelled
            if self.spell_checker.unknown([word_lower]):
                # Apply error formatting
                self.setFormat(start, length, self.error_format)

    def set_language(self, language: str):
        """
        Change the spell checker language

        Args:
            language: Language code (e.g., 'it', 'en', 'es')
        """
        self.spell_checker = SpellChecker(language=language)
        self.rehighlight()

    def add_word_to_dictionary(self, word: str):
        """
        Add a word to the custom dictionary

        Args:
            word: Word to add (case-insensitive)
        """
        self.custom_words.add(word.lower())
        self.rehighlight()

    def remove_word_from_dictionary(self, word: str):
        """
        Remove a word from the custom dictionary

        Args:
            word: Word to remove
        """
        self.custom_words.discard(word.lower())
        self.rehighlight()

    def add_words_to_dictionary(self, words: list):
        """
        Add multiple words to the custom dictionary

        Args:
            words: List of words to add
        """
        for word in words:
            self.custom_words.add(word.lower())
        self.rehighlight()

    def clear_custom_dictionary(self):
        """Clear all custom words"""
        self.custom_words.clear()
        self.rehighlight()

    def get_suggestions(self, word: str) -> list:
        """
        Get spelling suggestions for a misspelled word

        Args:
            word: The misspelled word

        Returns:
            List of suggested corrections
        """
        return list(self.spell_checker.candidates(word.lower()))

    def set_enabled(self, enabled: bool):
        """
        Enable or disable spell checking

        Args:
            enabled: True to enable, False to disable
        """
        self._enabled = enabled
        self.rehighlight()

    def is_enabled(self) -> bool:
        """Check if spell checking is enabled"""
        return self._enabled

    def is_word_misspelled(self, word: str) -> bool:
        """
        Check if a word is misspelled

        Args:
            word: Word to check

        Returns:
            True if misspelled, False otherwise
        """
        word_lower = word.lower()

        # Check custom dictionary first
        if word_lower in self.custom_words:
            return False

        # Check with spell checker
        return bool(self.spell_checker.unknown([word_lower]))
