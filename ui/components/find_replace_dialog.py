"""
Find & Replace Dialog Component
"""
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                               QLineEdit, QPushButton, QCheckBox, QMessageBox, QWidget)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QTextDocument, QTextCursor, QColor


class FindReplaceDialog(QDialog):
    """
    Dialog for finding and replacing text in the editor

    Features:
    - Find next/previous
    - Replace current/all
    - Case sensitive search
    - Whole words only search
    - Match counter
    """

    def __init__(self, text_edit, show_replace=True, parent=None):
        """
        Initialize the Find & Replace dialog

        Args:
            text_edit: QTextEdit widget to search in
            show_replace: If True, show replace controls
            parent: Parent widget
        """
        super().__init__(parent)
        self.text_edit = text_edit
        self.show_replace = show_replace
        self.current_match_index = -1
        self.total_matches = 0
        self.match_positions = []  # List of QTextCursor positions

        self._setup_ui()
        self._connect_signals()

        # Set dialog properties
        self.setModal(False)  # Non-modal so user can interact with editor
        self.setWindowTitle("Find & Replace" if show_replace else "Find")
        self.resize(450, 200 if not show_replace else 280)

    def _setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # Find input
        find_layout = QHBoxLayout()
        find_layout.addWidget(QLabel("Find what:"))
        self.find_input = QLineEdit()
        self.find_input.setPlaceholderText("Enter text to find...")
        find_layout.addWidget(self.find_input)
        layout.addLayout(find_layout)

        # Replace input (always created, visibility controlled later)
        self.replace_widget = QWidget()
        replace_layout = QHBoxLayout()
        replace_layout.setContentsMargins(0, 0, 0, 0)
        self.replace_label = QLabel("Replace with:")
        replace_layout.addWidget(self.replace_label)
        self.replace_input = QLineEdit()
        self.replace_input.setPlaceholderText("Enter replacement text...")
        replace_layout.addWidget(self.replace_input)
        self.replace_widget.setLayout(replace_layout)
        layout.addWidget(self.replace_widget)

        # Set initial visibility
        self.replace_widget.setVisible(self.show_replace)

        # Options
        options_layout = QHBoxLayout()
        self.case_sensitive_check = QCheckBox("Case sensitive")
        self.whole_words_check = QCheckBox("Whole words only")
        options_layout.addWidget(self.case_sensitive_check)
        options_layout.addWidget(self.whole_words_check)
        options_layout.addStretch()
        layout.addLayout(options_layout)

        # Match counter
        self.match_label = QLabel("Matches: 0")
        self.match_label.setStyleSheet("color: #666; font-size: 11px;")
        layout.addWidget(self.match_label)

        # Separator line
        layout.addSpacing(5)

        # Buttons
        buttons_layout = QHBoxLayout()

        self.find_prev_button = QPushButton("◀ Find Previous")
        self.find_next_button = QPushButton("Find Next ▶")
        self.find_next_button.setDefault(True)

        buttons_layout.addWidget(self.find_prev_button)
        buttons_layout.addWidget(self.find_next_button)

        # Always create replace buttons, control visibility
        self.replace_button = QPushButton("Replace")
        self.replace_all_button = QPushButton("Replace All")
        buttons_layout.addWidget(self.replace_button)
        buttons_layout.addWidget(self.replace_all_button)

        # Set initial visibility for replace buttons
        self.replace_button.setVisible(self.show_replace)
        self.replace_all_button.setVisible(self.show_replace)

        buttons_layout.addStretch()

        self.close_button = QPushButton("Close")
        buttons_layout.addWidget(self.close_button)

        layout.addLayout(buttons_layout)

    def _connect_signals(self):
        """Connect signals to slots"""
        self.find_input.textChanged.connect(self._on_find_text_changed)
        self.find_input.returnPressed.connect(self.find_next)

        self.find_next_button.clicked.connect(self.find_next)
        self.find_prev_button.clicked.connect(self.find_previous)

        # Always connect replace buttons (they're always created now)
        self.replace_button.clicked.connect(self.replace_current)
        self.replace_all_button.clicked.connect(self.replace_all)

        self.case_sensitive_check.toggled.connect(self._on_options_changed)
        self.whole_words_check.toggled.connect(self._on_options_changed)

        self.close_button.clicked.connect(self.close)

    def _on_find_text_changed(self):
        """Handle find text changes"""
        # Reset search when text changes
        self.current_match_index = -1
        self.match_positions = []
        self.total_matches = 0

        # Find all matches to update counter
        if self.find_input.text():
            self.find_all()
            self.highlight_all_matches()
        else:
            self.clear_highlights()
            self.match_label.setText("Matches: 0")

    def _on_options_changed(self):
        """Handle options checkbox changes"""
        # Re-search with new options
        self._on_find_text_changed()

    def _get_find_flags(self):
        """
        Get QTextDocument find flags based on options

        Returns:
            QTextDocument.FindFlags
        """
        flags = QTextDocument.FindFlag(0)

        if self.case_sensitive_check.isChecked():
            flags |= QTextDocument.FindFlag.FindCaseSensitively

        if self.whole_words_check.isChecked():
            flags |= QTextDocument.FindFlag.FindWholeWords

        return flags

    def find_all(self) -> list:
        """
        Find all occurrences of the search term

        Returns:
            List of QTextCursor objects at match positions
        """
        search_text = self.find_input.text()
        if not search_text:
            return []

        self.match_positions = []
        flags = self._get_find_flags()

        # Start from beginning of document
        cursor = QTextCursor(self.text_edit.document())
        cursor.movePosition(QTextCursor.MoveOperation.Start)

        # Find all matches
        while True:
            cursor = self.text_edit.document().find(search_text, cursor, flags)
            if cursor.isNull():
                break
            self.match_positions.append(QTextCursor(cursor))

        self.total_matches = len(self.match_positions)
        self._update_match_label()

        return self.match_positions

    def find_next(self) -> bool:
        """
        Find the next occurrence

        Returns:
            True if found, False otherwise
        """
        search_text = self.find_input.text()
        if not search_text:
            return False

        # If no matches found yet, find all first
        if not self.match_positions:
            self.find_all()

        if not self.match_positions:
            self.match_label.setText("No matches found")
            return False

        # Move to next match
        self.current_match_index = (self.current_match_index + 1) % self.total_matches

        # Select the match
        cursor = self.match_positions[self.current_match_index]
        self.text_edit.setTextCursor(cursor)

        # Update label
        self._update_match_label()

        # Highlight all matches with current one emphasized
        self.highlight_all_matches()

        return True

    def find_previous(self) -> bool:
        """
        Find the previous occurrence

        Returns:
            True if found, False otherwise
        """
        search_text = self.find_input.text()
        if not search_text:
            return False

        # If no matches found yet, find all first
        if not self.match_positions:
            self.find_all()

        if not self.match_positions:
            self.match_label.setText("No matches found")
            return False

        # Move to previous match
        self.current_match_index = (self.current_match_index - 1) % self.total_matches

        # Select the match
        cursor = self.match_positions[self.current_match_index]
        self.text_edit.setTextCursor(cursor)

        # Update label
        self._update_match_label()

        # Highlight all matches
        self.highlight_all_matches()

        return True

    def replace_current(self):
        """Replace the currently selected occurrence"""
        if not self.show_replace:
            return

        search_text = self.find_input.text()
        replace_text = self.replace_input.text()

        if not search_text:
            return

        # Get current cursor
        cursor = self.text_edit.textCursor()

        # Check if current selection matches search text
        selected_text = cursor.selectedText()

        # Check if it matches (considering case sensitivity)
        matches = False
        if self.case_sensitive_check.isChecked():
            matches = selected_text == search_text
        else:
            matches = selected_text.lower() == search_text.lower()

        if matches:
            # Replace the text
            cursor.insertText(replace_text)

            # Update match positions
            self._on_find_text_changed()

            # Find next occurrence
            self.find_next()
        else:
            # No valid selection, find next
            self.find_next()

    def replace_all(self) -> int:
        """
        Replace all occurrences

        Returns:
            Number of replacements made
        """
        if not self.show_replace:
            return 0

        search_text = self.find_input.text()
        replace_text = self.replace_input.text()

        if not search_text:
            return 0

        # Find all matches first
        self.find_all()

        if not self.match_positions:
            QMessageBox.information(self, "Replace All", "No matches found.")
            return 0

        count = len(self.match_positions)

        # Start editing block for undo
        cursor = self.text_edit.textCursor()
        cursor.beginEditBlock()

        # Replace from end to beginning to maintain positions
        for match_cursor in reversed(self.match_positions):
            match_cursor.insertText(replace_text)

        cursor.endEditBlock()

        # Clear match positions
        self.match_positions = []
        self.current_match_index = -1
        self.total_matches = 0

        # Update UI
        self._on_find_text_changed()

        # Show confirmation
        QMessageBox.information(
            self,
            "Replace All",
            f"Replaced {count} occurrence{'s' if count != 1 else ''}."
        )

        return count

    def highlight_all_matches(self):
        """Highlight all matches in the editor"""
        extra_selections = []

        if not self.match_positions:
            self.text_edit.setExtraSelections(extra_selections)
            return

        for i, cursor in enumerate(self.match_positions):
            selection = self.text_edit.ExtraSelection()
            selection.cursor = cursor

            # Current match gets orange background, others get yellow
            if i == self.current_match_index:
                selection.format.setBackground(QColor("#FFA500"))  # Orange
            else:
                selection.format.setBackground(QColor("#FFFF00"))  # Yellow

            extra_selections.append(selection)

        self.text_edit.setExtraSelections(extra_selections)

    def clear_highlights(self):
        """Clear all highlights from the editor"""
        self.text_edit.setExtraSelections([])

    def _update_match_label(self):
        """Update the match counter label"""
        if self.total_matches == 0:
            self.match_label.setText("Matches: 0")
        else:
            current = self.current_match_index + 1 if self.current_match_index >= 0 else 0
            self.match_label.setText(f"Matches: {current}/{self.total_matches}")

    def set_replace_visible(self, visible: bool):
        """
        Show or hide replace controls

        Args:
            visible: True to show replace controls
        """
        self.show_replace = visible

        # Show/hide replace input widget
        self.replace_widget.setVisible(visible)

        # Show/hide replace buttons
        self.replace_button.setVisible(visible)
        self.replace_all_button.setVisible(visible)

        # Update window title
        self.setWindowTitle("Find & Replace" if visible else "Find")

        # Resize dialog based on mode
        if visible:
            self.resize(450, 280)
        else:
            self.resize(450, 200)

    def showEvent(self, event):
        """Override show event to focus find input"""
        super().showEvent(event)
        self.find_input.setFocus()
        self.find_input.selectAll()

    def closeEvent(self, event):
        """Override close event to clear highlights"""
        self.clear_highlights()
        super().closeEvent(event)
