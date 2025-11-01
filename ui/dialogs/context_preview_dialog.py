"""
Context Preview Dialog - Shows what AI context will receive

Allows users to preview the exact context that will be sent to the AI,
helping them understand how their Story Context or Writing Guide is formatted.
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton,
    QLabel, QWidget, QApplication
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


class ContextPreviewDialog(QDialog):
    """
    Dialog to preview AI context

    Shows:
    - Full formatted context as AI receives it
    - Character and word count
    - Estimated token count
    - Copy to clipboard button
    """

    def __init__(self, context: str, context_type: str = "Context", parent=None):
        """
        Initialize preview dialog

        Args:
            context: The context string to preview
            context_type: Type of context (e.g., "Story Context", "Writing Guide")
            parent: Parent widget
        """
        super().__init__(parent)
        self.context = context
        self.context_type = context_type

        self._setup_ui()
        self._load_context()

    def _setup_ui(self):
        """Setup the user interface"""
        self.setWindowTitle(f"Preview: {self.context_type}")
        self.setMinimumSize(800, 600)

        layout = QVBoxLayout(self)

        # Header
        header_label = QLabel(f"📋 {self.context_type} Preview")
        header_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #2196F3;
                padding: 10px;
            }
        """)
        layout.addWidget(header_label)

        # Description
        desc_label = QLabel(
            "This is exactly what the AI will receive as context. "
            "Review this to ensure all information is correct and formatted properly."
        )
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #666; padding: 0 10px 10px 10px;")
        layout.addWidget(desc_label)

        # Preview text area
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setFont(QFont("Courier New", 11))
        self.preview_text.setStyleSheet("""
            QTextEdit {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 10px;
                background-color: #f9f9f9;
            }
        """)
        layout.addWidget(self.preview_text)

        # Stats bar
        stats_widget = self._create_stats_bar()
        layout.addWidget(stats_widget)

        # Buttons
        buttons_layout = QHBoxLayout()

        copy_btn = QPushButton("📋 Copy to Clipboard")
        copy_btn.clicked.connect(self._copy_to_clipboard)
        copy_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
        """)
        buttons_layout.addWidget(copy_btn)

        buttons_layout.addStretch()

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #f5f5f5;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        buttons_layout.addWidget(close_btn)

        layout.addLayout(buttons_layout)

    def _create_stats_bar(self) -> QWidget:
        """Create statistics bar showing context metrics"""
        stats_widget = QWidget()
        stats_layout = QHBoxLayout(stats_widget)
        stats_layout.setContentsMargins(10, 10, 10, 10)

        # Character count
        chars = len(self.context)
        chars_label = QLabel(f"Characters: {chars:,}")
        chars_label.setStyleSheet("font-weight: bold; color: #333;")
        stats_layout.addWidget(chars_label)

        stats_layout.addWidget(QLabel("•"))

        # Word count
        words = len(self.context.split())
        words_label = QLabel(f"Words: {words:,}")
        words_label.setStyleSheet("font-weight: bold; color: #333;")
        stats_layout.addWidget(words_label)

        stats_layout.addWidget(QLabel("•"))

        # Token estimate (rough estimate: ~4 chars per token)
        estimated_tokens = chars // 4
        tokens_label = QLabel(f"~Tokens: {estimated_tokens:,}")
        tokens_label.setToolTip("Estimated tokens (rough: ~4 characters per token)")

        # Color-code based on size
        if estimated_tokens > 100000:
            tokens_label.setStyleSheet("font-weight: bold; color: #f44336;")  # Red - very large
        elif estimated_tokens > 50000:
            tokens_label.setStyleSheet("font-weight: bold; color: #ff9800;")  # Orange - large
        else:
            tokens_label.setStyleSheet("font-weight: bold; color: #4CAF50;")  # Green - good size

        stats_layout.addWidget(tokens_label)

        stats_layout.addStretch()

        # Size warning if needed
        if estimated_tokens > 50000:
            warning_label = QLabel("⚠️ Large context - may impact AI performance")
            warning_label.setStyleSheet("color: #ff9800; font-weight: bold;")
            stats_layout.addWidget(warning_label)

        stats_widget.setStyleSheet("""
            QWidget {
                background-color: #e3f2fd;
                border: 1px solid #2196F3;
                border-radius: 4px;
            }
        """)

        return stats_widget

    def _load_context(self):
        """Load context into preview"""
        self.preview_text.setPlainText(self.context)

    def _copy_to_clipboard(self):
        """Copy context to clipboard"""
        clipboard = QApplication.clipboard()
        clipboard.setText(self.context)

        # Temporarily change button text
        sender = self.sender()
        original_text = sender.text()
        sender.setText("✅ Copied!")
        sender.setEnabled(False)

        # Reset after 2 seconds
        from PySide6.QtCore import QTimer
        QTimer.singleShot(2000, lambda: self._reset_copy_button(sender, original_text))

    def _reset_copy_button(self, button, original_text):
        """Reset copy button to original state"""
        button.setText(original_text)
        button.setEnabled(True)
