"""
Error Dialog Component - User-friendly error display
"""
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QTextEdit, QFrame, QWidget)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QIcon
from enum import IntEnum


class ErrorDialog(QDialog):
    """
    Professional error dialog with expandable technical details

    Features:
    - User-friendly error message
    - Collapsible technical details
    - Suggestions for resolution
    - Context-aware buttons (Retry, Cancel, Help)
    - Appropriate icons for error types
    """

    class DialogCode(IntEnum):
        """Dialog result codes"""
        Cancel = 0
        Retry = 1
        Help = 2
        RestoreBackup = 3

    def __init__(
        self,
        error_type,
        severity,
        message: str,
        technical_details: str,
        suggestions: list,
        recoverable: bool = False,
        context: str = "",
        parent=None
    ):
        """
        Initialize error dialog

        Args:
            error_type: ErrorType enum value
            severity: ErrorSeverity enum value
            message: User-friendly error message
            technical_details: Technical details (stack trace)
            suggestions: List of suggestion strings
            recoverable: Whether error is recoverable (show Retry)
            context: Context where error occurred
            parent: Parent widget
        """
        super().__init__(parent)
        self.error_type = error_type
        self.severity = severity
        self.message = message
        self.technical_details = technical_details
        self.suggestions = suggestions
        self.recoverable = recoverable
        self.context = context
        self.selected_backup = None

        self._setup_ui()
        self.setModal(True)
        self.resize(550, 300)

    def _setup_ui(self):
        """Setup the user interface"""
        # Window title based on severity
        title_map = {
            "info": "Information",
            "warning": "Warning",
            "error": "Error",
            "critical": "Critical Error"
        }
        self.setWindowTitle(title_map.get(str(self.severity.value), "Error"))

        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Header with icon and message
        header_layout = QHBoxLayout()

        # Icon based on severity
        icon_label = QLabel()
        icon_map = {
            "info": "ℹ️",
            "warning": "⚠️",
            "error": "❌",
            "critical": "🛑"
        }
        icon_text = icon_map.get(str(self.severity.value), "❌")
        icon_label.setText(icon_text)
        icon_font = QFont()
        icon_font.setPointSize(32)
        icon_label.setFont(icon_font)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        header_layout.addWidget(icon_label)

        # Message
        message_label = QLabel(self.message)
        message_label.setWordWrap(True)
        message_label.setTextFormat(Qt.TextFormat.PlainText)
        message_font = QFont()
        message_font.setPointSize(11)
        message_label.setFont(message_font)
        header_layout.addWidget(message_label, 1)

        layout.addLayout(header_layout)

        # Separator
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(line)

        # Suggestions section (if available)
        if self.suggestions:
            suggestions_label = QLabel("Suggestions:")
            suggestions_label.setStyleSheet("font-weight: bold; margin-top: 5px;")
            layout.addWidget(suggestions_label)

            suggestions_text = "\n".join([f"• {s}" for s in self.suggestions])
            suggestions_display = QLabel(suggestions_text)
            suggestions_display.setWordWrap(True)
            suggestions_display.setStyleSheet("margin-left: 15px; color: #555;")
            layout.addWidget(suggestions_display)

        # Technical details (collapsible)
        self.details_widget = QWidget()
        details_layout = QVBoxLayout(self.details_widget)
        details_layout.setContentsMargins(0, 0, 0, 0)

        self.details_text = QTextEdit()
        self.details_text.setPlainText(self.technical_details)
        self.details_text.setReadOnly(True)
        self.details_text.setMaximumHeight(200)
        self.details_text.setStyleSheet("""
            QTextEdit {
                background-color: #f5f5f5;
                border: 1px solid #ccc;
                font-family: monospace;
                font-size: 10px;
            }
        """)
        details_layout.addWidget(self.details_text)

        self.details_widget.setVisible(False)

        # Toggle button for details
        self.toggle_details_btn = QPushButton("▶ Show Technical Details")
        self.toggle_details_btn.setFlat(True)
        self.toggle_details_btn.setStyleSheet("""
            QPushButton {
                text-align: left;
                padding: 5px;
                border: none;
                color: #2196F3;
            }
            QPushButton:hover {
                background-color: #e3f2fd;
            }
        """)
        self.toggle_details_btn.clicked.connect(self._toggle_details)
        layout.addWidget(self.toggle_details_btn)

        layout.addWidget(self.details_widget)

        layout.addStretch()

        # Separator
        line2 = QFrame()
        line2.setFrameShape(QFrame.Shape.HLine)
        line2.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(line2)

        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()

        # Retry button (only if recoverable)
        if self.recoverable:
            self.retry_btn = QPushButton("Retry")
            self.retry_btn.setDefault(True)
            self.retry_btn.clicked.connect(lambda: self.done(self.DialogCode.Retry))
            self.retry_btn.setStyleSheet("""
                QPushButton {
                    background-color: #2196F3;
                    color: white;
                    padding: 8px 20px;
                    border: none;
                    border-radius: 4px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #1976D2;
                }
            """)
            buttons_layout.addWidget(self.retry_btn)

        # Cancel/Close button
        close_text = "Cancel" if self.recoverable else "Close"
        self.cancel_btn = QPushButton(close_text)
        if not self.recoverable:
            self.cancel_btn.setDefault(True)
        self.cancel_btn.clicked.connect(lambda: self.done(self.DialogCode.Cancel))
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                padding: 8px 20px;
                border: 1px solid #ccc;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #f5f5f5;
            }
        """)
        buttons_layout.addWidget(self.cancel_btn)

        # Help button
        self.help_btn = QPushButton("Help")
        self.help_btn.clicked.connect(self._show_help)
        self.help_btn.setStyleSheet("""
            QPushButton {
                padding: 8px 20px;
                border: 1px solid #ccc;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #f5f5f5;
            }
        """)
        buttons_layout.addWidget(self.help_btn)

        layout.addLayout(buttons_layout)

    def _toggle_details(self):
        """Toggle technical details visibility"""
        visible = self.details_widget.isVisible()
        self.details_widget.setVisible(not visible)

        if visible:
            self.toggle_details_btn.setText("▶ Show Technical Details")
            self.resize(550, 300)
        else:
            self.toggle_details_btn.setText("▼ Hide Technical Details")
            self.resize(550, 500)

    def _show_help(self):
        """Show help information"""
        from PySide6.QtWidgets import QMessageBox

        help_text = (
            f"<h3>Error Help</h3>"
            f"<p><b>Context:</b> {self.context}</p>"
            f"<p><b>Error Type:</b> {self.error_type.value}</p>"
            f"<p><b>Suggestions:</b></p>"
            f"<ul>"
        )

        for suggestion in self.suggestions:
            help_text += f"<li>{suggestion}</li>"

        help_text += (
            f"</ul>"
            f"<p>For more help, check the error log or visit the documentation.</p>"
        )

        QMessageBox.information(self, "Help", help_text)

    def copy_technical_details(self):
        """Copy technical details to clipboard"""
        from PySide6.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        clipboard.setText(self.technical_details)

    @staticmethod
    def show_error(
        error_type,
        severity,
        message: str,
        technical_details: str = "",
        suggestions: list = None,
        recoverable: bool = False,
        context: str = "",
        parent=None
    ) -> int:
        """
        Static method to show error dialog

        Args:
            error_type: ErrorType enum value
            severity: ErrorSeverity enum value
            message: User-friendly message
            technical_details: Technical details
            suggestions: List of suggestions
            recoverable: Whether error is recoverable
            context: Context where error occurred
            parent: Parent widget

        Returns:
            int: Dialog result code
        """
        dialog = ErrorDialog(
            error_type=error_type,
            severity=severity,
            message=message,
            technical_details=technical_details,
            suggestions=suggestions or [],
            recoverable=recoverable,
            context=context,
            parent=parent
        )
        return dialog.exec()
