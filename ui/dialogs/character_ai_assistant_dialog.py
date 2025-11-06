"""
Character AI Assistant Dialog - AI-powered character development
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton,
    QLabel, QScrollArea, QWidget, QFrame, QMessageBox, QProgressBar
)
from PySide6.QtCore import Qt, Signal, QThread
from PySide6.QtGui import QFont, QTextCursor
from typing import Optional, List
from models.character import Character
from managers.ai import AIManager, AIMessage, AIResponse
from utils.logger import AppLogger
from shared.license import premium_feature


class AIWorkerThread(QThread):
    """
    Worker thread for AI generation to avoid blocking UI

    🆕 MILESTONE 3: Usa generate_for_character_with_context per contesto completo
    """
    finished = Signal(object)  # AIResponse
    error = Signal(str)

    def __init__(
        self,
        ai_manager: AIManager,
        character,
        project,
        character_manager,
        messages: List[AIMessage]
    ):
        super().__init__()
        self.ai_manager = ai_manager
        self.character = character
        self.project = project
        self.character_manager = character_manager
        self.messages = messages

    def run(self):
        """Generate AI response in background with full context"""
        try:
            # 🆕 Use new method with context!
            response = self.ai_manager.generate_for_character_with_context(
                character=self.character,
                project=self.project,
                character_manager=self.character_manager,
                messages=self.messages
            )
            self.finished.emit(response)
        except Exception as e:
            self.error.emit(str(e))


@premium_feature("ai_character_assistant")
class CharacterAIAssistantDialog(QDialog):
    """
    Dialog for AI-assisted character development

    Provides a conversational interface where the user can collaborate
    with an AI to develop character details (physical description,
    psychology, background, etc.)
    """

    # Signals
    character_updated = Signal(Character)  # Emitted when character should be updated

    def __init__(
        self,
        character: Character,
        project,
        character_manager,
        ai_manager: AIManager,
        parent=None
    ):
        """
        Initialize Character AI Assistant Dialog

        Args:
            character: Character to develop
            project: Project instance (for Story Context)
            character_manager: CharacterManager (for related characters)
            ai_manager: AIManager instance
            parent: Parent widget
        """
        super().__init__(parent)
        self.character = character
        self.project = project
        self.character_manager = character_manager
        self.ai_manager = ai_manager
        self.messages: List[AIMessage] = []
        self.worker_thread: Optional[AIWorkerThread] = None

        # Load conversation history if exists
        self._load_conversation_history()

        self._setup_ui()
        self._display_conversation_history()

        # Check if AI is available
        if not self.ai_manager.get_available_providers():
            self._show_no_provider_warning()

    def _setup_ui(self):
        """Setup the UI"""
        self.setWindowTitle(f"🤖 AI Character Assistant - {self.character.name}")
        self.setMinimumSize(900, 700)

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)

        # Header
        header = QLabel("AI Character Development Assistant")
        header.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        main_layout.addWidget(header)

        # AI Provider Indicator (shows which AI is configured for this project)
        ai_provider_indicator = self._create_ai_provider_indicator()
        main_layout.addWidget(ai_provider_indicator)

        info = QLabel("Collaborate with AI to develop your character's details")
        info.setStyleSheet("color: #666; font-style: italic;")
        main_layout.addWidget(info)

        # Conversation area
        self.conversation_area = QTextEdit()
        self.conversation_area.setReadOnly(True)
        self.conversation_area.setStyleSheet("""
            QTextEdit {
                background-color: #f9f9f9;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 10px;
                font-size: 13px;
            }
        """)
        main_layout.addWidget(self.conversation_area)

        # Progress bar (hidden by default)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #ddd;
                border-radius: 3px;
                text-align: center;
                height: 20px;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
            }
        """)
        main_layout.addWidget(self.progress_bar)

        # Input area
        input_label = QLabel("Your message:")
        input_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        main_layout.addWidget(input_label)

        self.input_area = QTextEdit()
        self.input_area.setMaximumHeight(100)
        self.input_area.setPlaceholderText(
            "Describe your character context or ask for help developing specific aspects...\n\n"
            "Example: I'm writing a medical thriller about a doctor who discovers something "
            "alarming while researching a patient. Help me develop the protagonist."
        )
        self.input_area.setStyleSheet("""
            QTextEdit {
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 8px;
                font-size: 13px;
            }
        """)
        main_layout.addWidget(self.input_area)

        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)

        self.send_btn = QPushButton("📤 Send")
        self.send_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px 24px;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        self.send_btn.clicked.connect(self._on_send)
        buttons_layout.addWidget(self.send_btn)

        self.clear_btn = QPushButton("🗑️ Clear History")
        self.clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff9800;
                color: white;
                border: none;
                padding: 10px 24px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #e68900;
            }
        """)
        self.clear_btn.clicked.connect(self._on_clear_history)
        buttons_layout.addWidget(self.clear_btn)

        buttons_layout.addStretch()

        self.settings_btn = QPushButton("⚙️ AI Settings")
        self.settings_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 10px 24px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #0b7dda;
            }
        """)
        self.settings_btn.clicked.connect(self._on_settings)
        buttons_layout.addWidget(self.settings_btn)

        self.close_btn = QPushButton("Close")
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                padding: 10px 24px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        self.close_btn.clicked.connect(self.accept)
        buttons_layout.addWidget(self.close_btn)

        main_layout.addLayout(buttons_layout)

        # Tips
        tips = QLabel(
            "💡 Tip: Be specific about genre, context, and what aspects you need help with. "
            "The AI will ask clarifying questions and provide detailed suggestions."
        )
        tips.setWordWrap(True)
        tips.setStyleSheet("color: #666; font-size: 11px; font-style: italic; padding: 5px;")
        main_layout.addWidget(tips)

    def _create_ai_provider_indicator(self) -> QLabel:
        """
        Create a visual indicator showing which AI provider is configured for this project

        Returns:
            QLabel: Styled label with provider icon and name
        """
        # Get provider from project configuration
        provider_name = getattr(self.project, 'ai_provider_name', 'claude')
        provider_config = getattr(self.project, 'ai_provider_config', {})

        # Map provider names to icons and display names
        provider_info = {
            'claude': ('🟣', 'Claude (Anthropic)'),
            'openai': ('🟢', 'OpenAI (GPT)'),
            'ollama': ('🔵', 'Ollama (Local)')
        }

        icon, display_name = provider_info.get(provider_name, ('🤖', provider_name.capitalize()))

        # Get model info if available
        model = provider_config.get('model', '')
        model_info = f" - {model}" if model else ""

        # Create styled label
        indicator = QLabel(f"{icon} <b>AI Provider:</b> {display_name}{model_info}")
        indicator.setStyleSheet("""
            QLabel {
                background-color: #e8f5e9;
                border: 1px solid #4CAF50;
                border-radius: 5px;
                padding: 8px 12px;
                font-size: 12px;
                color: #2e7d32;
            }
        """)
        indicator.setToolTip(
            f"This project is configured to use {display_name} for AI character development.\n"
            f"You can change this in Project Info → AI Provider Configuration."
        )

        return indicator

    def _load_conversation_history(self):
        """Load conversation history from character"""
        if self.character.ai_conversation_history:
            self.messages = [
                AIMessage.from_dict(msg)
                for msg in self.character.ai_conversation_history
            ]
            AppLogger.info(f"Loaded {len(self.messages)} messages from character history")

    def _display_conversation_history(self):
        """Display conversation history in the conversation area"""
        self.conversation_area.clear()

        if not self.messages:
            self.conversation_area.setHtml(
                "<p style='color: #999; font-style: italic;'>"
                "No conversation history yet. Start by describing your character context or "
                "ask for help developing specific aspects."
                "</p>"
            )
            return

        html_parts = []
        for msg in self.messages:
            if msg.role == 'user':
                html_parts.append(
                    f"<div style='margin-bottom: 15px;'>"
                    f"<b style='color: #2196F3;'>👤 You:</b><br>"
                    f"<div style='background-color: #e3f2fd; padding: 10px; "
                    f"border-radius: 5px; margin-top: 5px;'>{self._format_text(msg.content)}</div>"
                    f"</div>"
                )
            elif msg.role == 'assistant':
                html_parts.append(
                    f"<div style='margin-bottom: 15px;'>"
                    f"<b style='color: #4CAF50;'>🤖 AI Assistant:</b><br>"
                    f"<div style='background-color: #f1f8e9; padding: 10px; "
                    f"border-radius: 5px; margin-top: 5px;'>{self._format_text(msg.content)}</div>"
                    f"</div>"
                )

        self.conversation_area.setHtml("".join(html_parts))

        # Scroll to bottom
        cursor = self.conversation_area.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.conversation_area.setTextCursor(cursor)

    def _format_text(self, text: str) -> str:
        """Format text for HTML display"""
        # Replace newlines with <br>
        text = text.replace('\n', '<br>')
        # Basic markdown-like formatting (optional)
        # Could add more sophisticated formatting here
        return text

    def _show_no_provider_warning(self):
        """Show warning if no AI provider is available"""
        self.conversation_area.setHtml(
            "<div style='background-color: #fff3cd; padding: 15px; border-radius: 5px; "
            "border: 1px solid #ffc107;'>"
            "<b style='color: #856404;'>⚠️ No AI Provider Configured</b><br><br>"
            "To use the AI Character Assistant, you need to configure an AI provider:<br><br>"
            "1. Click <b>'⚙️ AI Settings'</b> button below<br>"
            "2. Enter your API key for Claude, OpenAI, or configure Ollama<br>"
            "3. Save and return to start the conversation<br><br>"
            "The AI assistant helps you develop rich character details through collaborative dialogue."
            "</div>"
        )

    def _on_send(self):
        """Handle send button click"""
        user_input = self.input_area.toPlainText().strip()

        if not user_input:
            QMessageBox.warning(self, "Empty Message", "Please enter a message to send to the AI.")
            return

        # Check if provider is available
        if not self.ai_manager.get_available_providers():
            QMessageBox.warning(
                self,
                "No AI Provider",
                "No AI provider is configured. Please click 'AI Settings' to configure an API key."
            )
            return

        # Add user message to conversation
        user_message = AIMessage(role='user', content=user_input)
        self.messages.append(user_message)

        # Display user message
        self._display_conversation_history()

        # Clear input
        self.input_area.clear()

        # Disable UI during generation
        self._set_generating(True)

        # Start AI generation in background thread (with full context!)
        self.worker_thread = AIWorkerThread(
            ai_manager=self.ai_manager,
            character=self.character,
            project=self.project,
            character_manager=self.character_manager,
            messages=self.messages.copy()
        )
        self.worker_thread.finished.connect(self._on_ai_response)
        self.worker_thread.error.connect(self._on_ai_error)
        self.worker_thread.start()

        AppLogger.info("AI generation started")

    def _on_ai_response(self, response: AIResponse):
        """Handle AI response"""
        self._set_generating(False)

        if not response.success:
            self._on_ai_error(response.error or "Unknown error")
            return

        # Add assistant message to conversation
        assistant_message = AIMessage(role='assistant', content=response.content)
        self.messages.append(assistant_message)

        # Save conversation to character
        self._save_conversation_to_character()

        # Display updated conversation
        self._display_conversation_history()

        # Log usage
        if response.usage:
            AppLogger.info(
                f"AI response received. Tokens: {response.usage.get('input_tokens', 0)} input, "
                f"{response.usage.get('output_tokens', 0)} output"
            )

    def _on_ai_error(self, error: str):
        """Handle AI error"""
        self._set_generating(False)

        AppLogger.error(f"AI generation error: {error}")

        QMessageBox.critical(
            self,
            "AI Error",
            f"An error occurred while generating AI response:\n\n{error}\n\n"
            "Please check your API key configuration in AI Settings."
        )

    def _set_generating(self, generating: bool):
        """Enable/disable UI during generation"""
        self.send_btn.setEnabled(not generating)
        self.input_area.setEnabled(not generating)
        self.clear_btn.setEnabled(not generating)
        self.progress_bar.setVisible(generating)

        if generating:
            self.send_btn.setText("⏳ Generating...")
        else:
            self.send_btn.setText("📤 Send")

    def _save_conversation_to_character(self):
        """Save conversation history to character"""
        self.character.ai_conversation_history = [msg.to_dict() for msg in self.messages]
        AppLogger.info(f"Saved {len(self.messages)} messages to character history")

    def _on_clear_history(self):
        """Clear conversation history"""
        reply = QMessageBox.question(
            self,
            "Clear History",
            "Are you sure you want to clear the entire conversation history?\n\n"
            "This action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.messages.clear()
            self._save_conversation_to_character()
            self._display_conversation_history()
            AppLogger.info("Conversation history cleared")

    def _on_settings(self):
        """Open AI settings dialog"""
        from ui.dialogs.ai_settings_dialog import AISettingsDialog

        dialog = AISettingsDialog(self.ai_manager, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Refresh available providers
            if self.ai_manager.get_available_providers():
                self.conversation_area.clear()
                self._display_conversation_history()
                QMessageBox.information(
                    self,
                    "Settings Saved",
                    "AI settings saved successfully. You can now use the AI Assistant."
                )

    def get_updated_character(self) -> Character:
        """
        Get the character with updated conversation history

        Returns:
            Character: Updated character
        """
        return self.character

    def closeEvent(self, event):
        """Handle dialog close"""
        # Ensure conversation is saved
        self._save_conversation_to_character()
        event.accept()
