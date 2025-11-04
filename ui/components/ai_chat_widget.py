"""
AI Chat Widget - Interactive AI assistant for document context

Provides conversational AI interface for characters, locations, notes, etc.
Features:
- Question/Answer interface
- Conversation history
- Text selection and insertion
- Quick action prompts
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton,
    QLabel, QScrollArea, QFrame, QComboBox, QMessageBox
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QTextCursor, QFont
from typing import Optional, Dict, List


class AIMessageBubble(QFrame):
    """Message bubble for AI chat (user or AI response)"""

    text_selected = Signal(str)  # Emitted when user selects text to insert

    def __init__(self, message: str, is_user: bool = False, parent=None):
        super().__init__(parent)
        self.message = message
        self.is_user = is_user

        self._setup_ui()

    def _setup_ui(self):
        """Setup message bubble UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)

        # Message text (selectable)
        self.text_edit = QTextEdit()
        self.text_edit.setPlainText(self.message)
        self.text_edit.setReadOnly(True)
        self.text_edit.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # Auto-size height based on content (min 150px = ~5 righe, max 500px)
        doc_height = self.text_edit.document().size().height()
        calculated_height = min(max(int(doc_height) + 20, 150), 500)
        self.text_edit.setFixedHeight(calculated_height)

        # Get colors from Qt palette (adapts to system theme)
        from PySide6.QtGui import QPalette
        from PySide6.QtWidgets import QApplication

        palette = QApplication.palette()

        # Style based on sender - using palette colors
        if self.is_user:
            # User bubble: accent color (blue-ish)
            bg_color = palette.color(QPalette.ColorRole.Highlight).lighter(180).name()
            border_color = palette.color(QPalette.ColorRole.Highlight).name()
            text_color = palette.color(QPalette.ColorRole.HighlightedText).name()

            self.setStyleSheet(f"""
                QFrame {{
                    background-color: {bg_color};
                    border: 1px solid {border_color};
                    border-radius: 8px;
                    margin: 5px 20px 5px 5px;
                }}
                QTextEdit {{
                    background-color: transparent;
                    border: none;
                    color: {palette.color(QPalette.ColorRole.Text).name()};
                    font-size: 14px;
                    line-height: 1.5;
                }}
            """)
        else:
            # AI bubble: base/alternate background
            bg_color = palette.color(QPalette.ColorRole.AlternateBase).name()
            border_color = palette.color(QPalette.ColorRole.Mid).name()
            text_color = palette.color(QPalette.ColorRole.Text).name()

            self.setStyleSheet(f"""
                QFrame {{
                    background-color: {bg_color};
                    border: 1px solid {border_color};
                    border-radius: 8px;
                    margin: 5px 5px 5px 20px;
                }}
                QTextEdit {{
                    background-color: transparent;
                    border: none;
                    color: {text_color};
                    font-size: 14px;
                    line-height: 1.5;
                }}
            """)

        layout.addWidget(self.text_edit)

        # Action buttons for AI responses
        if not self.is_user:
            actions_layout = QHBoxLayout()

            copy_btn = QPushButton("📋 Copy")
            copy_btn.setToolTip("Copy to clipboard")
            copy_btn.clicked.connect(self._copy_to_clipboard)
            copy_btn.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    padding: 4px 8px;
                    border-radius: 3px;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
            """)
            actions_layout.addWidget(copy_btn)

            insert_btn = QPushButton("➕ Insert to Document")
            insert_btn.setToolTip("Insert selected text to main document")
            insert_btn.clicked.connect(self._insert_selected_text)
            insert_btn.setStyleSheet("""
                QPushButton {
                    background-color: #2196F3;
                    color: white;
                    border: none;
                    padding: 4px 8px;
                    border-radius: 3px;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background-color: #1976D2;
                }
            """)
            actions_layout.addWidget(insert_btn)

            actions_layout.addStretch()
            layout.addLayout(actions_layout)

    def _copy_to_clipboard(self):
        """Copy message to clipboard"""
        from PySide6.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        clipboard.setText(self.message)

        # Provide visual feedback
        sender = self.sender()
        if sender:
            original_text = sender.text()
            sender.setText("✅ Copied!")
            sender.setEnabled(False)

            # Reset after 2 seconds
            QTimer.singleShot(2000, lambda: self._reset_copy_button(sender, original_text))

    def _reset_copy_button(self, button, original_text):
        """Reset copy button to original state"""
        if button:
            button.setText(original_text)
            button.setEnabled(True)

    def _insert_selected_text(self):
        """Emit signal with selected text (or full text if none selected)"""
        cursor = self.text_edit.textCursor()
        selected_text = cursor.selectedText()

        if not selected_text:
            selected_text = self.message

        self.text_selected.emit(selected_text)


class AIChatWidget(QWidget):
    """
    AI Chat interface for context-aware conversations

    Signals:
        text_to_insert(str): Emitted when user wants to insert AI response
    """

    text_to_insert = Signal(str)

    def __init__(
        self,
        context_type: str = "Character",
        ai_manager=None,
        project_manager=None,
        entity_manager=None,
        parent=None
    ):
        """
        Initialize AI chat widget

        Args:
            context_type: Type of context (Character, Location, Scene, Note)
            ai_manager: AIManager instance for AI calls
            project_manager: ProjectManager instance for context
            entity_manager: Manager for the entity type (CharacterManager, LocationManager, etc.)
            parent: Parent widget
        """
        super().__init__(parent)
        self.context_type = context_type
        self.conversation_history = []
        self.ai_manager = ai_manager
        self.project_manager = project_manager
        self.entity_manager = entity_manager
        self.current_entity = None

        self._setup_ui()

    def _setup_ui(self):
        """Setup the UI - Chat messenger style"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # Conversation history area (TOP - most space)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)

        # Use palette colors for theme compatibility
        from PySide6.QtGui import QPalette
        palette = self.palette()
        bg_color = palette.color(QPalette.ColorRole.Base).name()
        border_color = palette.color(QPalette.ColorRole.Mid).name()

        self.scroll_area.setStyleSheet(f"""
            QScrollArea {{
                background-color: {bg_color};
                border: 1px solid {border_color};
                border-radius: 4px;
            }}
        """)

        self.history_widget = QWidget()
        self.history_layout = QVBoxLayout(self.history_widget)
        self.history_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.history_layout.setSpacing(8)
        self.history_layout.setContentsMargins(5, 5, 5, 5)

        self.scroll_area.setWidget(self.history_widget)
        layout.addWidget(self.scroll_area, stretch=1)  # Takes most space

        # Quick prompts (compact, collapsible)
        prompts_layout = QHBoxLayout()
        prompts_layout.setSpacing(5)

        prompts_icon = QPushButton("💡")
        prompts_icon.setFixedSize(24, 24)
        prompts_icon.setToolTip("Quick Prompts")
        prompts_icon.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                font-size: 14px;
                padding: 0px;
            }
            QPushButton:hover {
                background-color: #F0F0F0;
                border-radius: 4px;
            }
        """)
        prompts_layout.addWidget(prompts_icon)

        self.quick_prompts_combo = QComboBox()
        self.quick_prompts_combo.addItem("Quick prompts...", "")
        self._populate_quick_prompts()
        self.quick_prompts_combo.currentIndexChanged.connect(self._on_prompt_selected)

        # Use palette colors
        combo_bg = palette.color(QPalette.ColorRole.Base).name()
        combo_border = palette.color(QPalette.ColorRole.Mid).name()
        combo_hover = palette.color(QPalette.ColorRole.Highlight).name()
        combo_text = palette.color(QPalette.ColorRole.Text).name()

        self.quick_prompts_combo.setStyleSheet(f"""
            QComboBox {{
                border: 1px solid {combo_border};
                border-radius: 3px;
                padding: 3px 8px;
                font-size: 11px;
                background-color: {combo_bg};
                color: {combo_text};
                min-width: 150px;
            }}
            QComboBox:hover {{
                border: 1px solid {combo_hover};
            }}
        """)
        prompts_layout.addWidget(self.quick_prompts_combo)
        prompts_layout.addStretch()

        layout.addLayout(prompts_layout)

        # Input area (BOTTOM - fixed height)
        input_container = QFrame()

        # Use palette colors for theme compatibility
        input_bg = palette.color(QPalette.ColorRole.Base).name()
        input_border = palette.color(QPalette.ColorRole.Mid).name()
        text_color = palette.color(QPalette.ColorRole.Text).name()

        input_container.setStyleSheet(f"""
            QFrame {{
                background-color: {input_bg};
                border: 2px solid {input_border};
                border-radius: 6px;
            }}
        """)
        input_layout = QHBoxLayout(input_container)
        input_layout.setContentsMargins(8, 8, 8, 8)
        input_layout.setSpacing(8)

        # Text input
        self.question_input = QTextEdit()
        self.question_input.setPlaceholderText("Type your question or #command here...")
        self.question_input.setMaximumHeight(80)
        self.question_input.setMinimumHeight(40)
        self.question_input.setStyleSheet(f"""
            QTextEdit {{
                border: none;
                padding: 4px;
                font-size: 14px;
                background-color: transparent;
                color: {text_color};
            }}
        """)
        # Enable Ctrl/Cmd + Enter to send
        self.question_input.installEventFilter(self)
        input_layout.addWidget(self.question_input, stretch=1)

        # Send button (use Highlight color from palette)
        ask_btn = QPushButton("Send")
        ask_btn.clicked.connect(self._on_ask_ai)
        ask_btn.setFixedSize(70, 40)

        # Use palette highlight color for primary action button
        btn_color = palette.color(QPalette.ColorRole.Highlight).name()
        btn_hover = palette.color(QPalette.ColorRole.Highlight).lighter(110).name()
        btn_pressed = palette.color(QPalette.ColorRole.Highlight).darker(110).name()
        btn_text = palette.color(QPalette.ColorRole.HighlightedText).name()

        ask_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {btn_color};
                color: {btn_text};
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: {btn_hover};
            }}
            QPushButton:pressed {{
                background-color: {btn_pressed};
            }}
        """)
        input_layout.addWidget(ask_btn)

        layout.addWidget(input_container)

    def _populate_quick_prompts(self):
        """Populate quick prompts based on context type"""
        if self.context_type == "Character":
            prompts = [
                ("What's their biggest fear?", "fear"),
                ("Suggest a backstory", "backstory"),
                ("What motivates them?", "motivation"),
                ("Describe their personality in detail", "personality"),
                ("What's their fatal flaw?", "flaw"),
                ("Generate a dialogue sample", "dialogue"),
            ]
        elif self.context_type == "Location":
            prompts = [
                ("Describe the atmosphere", "atmosphere"),
                ("What secrets does this place hold?", "secrets"),
                ("Describe the architecture/layout", "layout"),
                ("What sounds/smells are present?", "sensory"),
            ]
        elif self.context_type == "Note":
            prompts = [
                ("Expand this idea", "expand"),
                ("Find potential conflicts", "conflicts"),
                ("Suggest related themes", "themes"),
            ]
        else:
            prompts = [
                ("Expand this idea", "expand"),
                ("Provide more details", "details"),
            ]

        for label, value in prompts:
            self.quick_prompts_combo.addItem(label, value)

    def eventFilter(self, obj, event):
        """Handle keyboard shortcuts in input field"""
        from PySide6.QtCore import QEvent
        from PySide6.QtGui import QKeyEvent

        if obj == self.question_input and event.type() == QEvent.Type.KeyPress:
            key_event = QKeyEvent(event)
            # Ctrl+Enter or Cmd+Enter to send
            if (key_event.key() == Qt.Key.Key_Return or key_event.key() == Qt.Key.Key_Enter):
                if key_event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                    self._on_ask_ai()
                    return True  # Event handled

        return super().eventFilter(obj, event)

    def _on_prompt_selected(self, index: int):
        """Handle quick prompt selection"""
        if index > 0:  # Skip "-- Select --"
            prompt_text = self.quick_prompts_combo.currentText()
            self.question_input.setPlainText(prompt_text)
            self.quick_prompts_combo.setCurrentIndex(0)  # Reset
            self.question_input.setFocus()  # Focus input for easy editing

    def _on_ask_ai(self):
        """Handle Ask AI button click - with REAL AI integration"""
        question = self.question_input.toPlainText().strip()

        if not question:
            QMessageBox.warning(self, "Empty Question", "Please enter a question first.")
            return

        # 🆕 Check if it's a command (#comando)
        if question.startswith('#'):
            self._handle_command(question)
            return

        # Check if AI Manager is available
        if not self.ai_manager:
            QMessageBox.warning(
                self,
                "AI Not Available",
                "AI Manager not initialized. Please check your configuration."
            )
            return

        # Check if project manager is available
        if not self.project_manager or not self.project_manager.current_project:
            QMessageBox.warning(
                self,
                "No Project",
                "Please open a project first."
            )
            return

        # Add user message bubble
        user_bubble = AIMessageBubble(question, is_user=True)
        self.history_layout.addWidget(user_bubble)
        self.conversation_history.append({"role": "user", "content": question})

        # Clear input
        self.question_input.clear()

        # Show loading indicator
        loading_bubble = AIMessageBubble("⏳ Generando risposta AI...", is_user=False)
        self.history_layout.addWidget(loading_bubble)

        # Call AI in background using QTimer to keep UI responsive
        QTimer.singleShot(100, lambda: self._call_ai_and_show_response(loading_bubble))

    def _call_ai_and_show_response(self, loading_bubble):
        """Call AI service and display response"""
        try:
            # Build messages for AI from conversation history
            from managers.ai.ai_provider import AIMessage

            messages = []
            for msg in self.conversation_history:
                messages.append(AIMessage(
                    role=msg["role"],
                    content=msg["content"]
                ))

            # Call appropriate AI method based on context type
            response = self._call_ai_for_context_type(messages)

            # Remove loading indicator
            loading_bubble.deleteLater()

            if response.success:
                # Add AI response bubble
                ai_bubble = AIMessageBubble(response.content, is_user=False)
                ai_bubble.text_selected.connect(self.text_to_insert.emit)
                self.history_layout.addWidget(ai_bubble)

                self.conversation_history.append({
                    "role": "assistant",
                    "content": response.content
                })

                # Auto-scroll to bottom
                self._scroll_to_bottom()
            else:
                # Show error
                error_msg = response.error or "Errore sconosciuto durante la generazione"
                error_bubble = AIMessageBubble(f"❌ Errore: {error_msg}", is_user=False)
                self.history_layout.addWidget(error_bubble)

                # Show detailed error in message box
                QMessageBox.warning(
                    self,
                    "AI Error",
                    f"Errore durante la generazione AI:\n\n{error_msg}"
                )

        except Exception as e:
            # Remove loading indicator
            loading_bubble.deleteLater()

            # Show error
            error_bubble = AIMessageBubble(f"❌ Errore imprevisto: {str(e)}", is_user=False)
            self.history_layout.addWidget(error_bubble)

            QMessageBox.critical(
                self,
                "Unexpected Error",
                f"Errore imprevisto:\n\n{str(e)}"
            )

    def _call_ai_for_context_type(self, messages):
        """
        Call AI service with appropriate context builder based on entity type

        Args:
            messages: List of AIMessage objects

        Returns:
            AIResponse object
        """
        from managers.ai.context_builder import (
            CharacterContextBuilder,
            LocationContextBuilder,
            NoteContextBuilder,
            SceneContextBuilder
        )
        from managers.ai.ai_provider import AIMessage

        project = self.project_manager.current_project

        if self.context_type == "Character":
            # Use CharacterContextBuilder
            if not self.current_entity or not self.entity_manager:
                # Fallback to simple generation without full context
                return self.ai_manager.generate_for_character(messages)

            # Build full context
            context_builder = CharacterContextBuilder(project, self.entity_manager)
            context = context_builder.build_full_context(self.current_entity)

            # Build enhanced system prompt
            system_prompt = f"""You are an expert creative writing assistant specializing in character development.

Your role is to help writers develop rich, complex, and believable characters.

---

{context}"""

            # Get provider and generate
            provider = self.ai_manager.get_provider()
            if not provider:
                from managers.ai.ai_provider import AIResponse
                return AIResponse(
                    content="",
                    success=False,
                    error="No AI provider available. Please configure an API key in settings."
                )

            return provider.generate(
                messages=messages,
                system_prompt=system_prompt
            )

        elif self.context_type == "Location":
            # Use LocationContextBuilder
            if not self.current_entity or not self.entity_manager:
                return self._generate_with_simple_context(messages, "location development")

            context_builder = LocationContextBuilder(project, self.entity_manager)
            context = context_builder.build_full_context(self.current_entity)

            system_prompt = f"""You are an expert creative writing assistant specializing in location and world-building.

Your role is to help writers develop rich, immersive locations and settings.

---

{context}"""

            provider = self.ai_manager.get_provider()
            if not provider:
                from managers.ai.ai_provider import AIResponse
                return AIResponse(
                    content="",
                    success=False,
                    error="No AI provider available."
                )

            return provider.generate(messages=messages, system_prompt=system_prompt)

        elif self.context_type == "Note":
            # Use NoteContextBuilder
            if not self.current_entity:
                return self._generate_with_simple_context(messages, "note expansion")

            context_builder = NoteContextBuilder(project)
            context = context_builder.build_full_context(self.current_entity)

            system_prompt = f"""You are a creative writing assistant helping to develop and expand story ideas and notes.

---

{context}"""

            provider = self.ai_manager.get_provider()
            if not provider:
                from managers.ai.ai_provider import AIResponse
                return AIResponse(
                    content="",
                    success=False,
                    error="No AI provider available."
                )

            return provider.generate(messages=messages, system_prompt=system_prompt)

        elif self.context_type == "Scene":
            # Use SceneContextBuilder
            if not self.current_entity:
                return self._generate_with_simple_context(messages, "scene writing")

            context_builder = SceneContextBuilder(project)
            context = context_builder.build_full_context(self.current_entity)

            system_prompt = f"""You are an expert creative writing assistant specializing in scene development and prose writing.

---

{context}"""

            provider = self.ai_manager.get_provider()
            if not provider:
                from managers.ai.ai_provider import AIResponse
                return AIResponse(
                    content="",
                    success=False,
                    error="No AI provider available."
                )

            return provider.generate(messages=messages, system_prompt=system_prompt)

        else:
            # Fallback
            return self._generate_with_simple_context(messages, "creative writing")

    def _generate_with_simple_context(self, messages, task_description: str):
        """Fallback method for simple AI generation without full context"""
        provider = self.ai_manager.get_provider()
        if not provider:
            from managers.ai.ai_provider import AIResponse
            return AIResponse(
                content="",
                success=False,
                error="No AI provider available."
            )

        system_prompt = f"""You are a creative writing assistant helping with {task_description}.

Provide helpful, detailed, and creative suggestions."""

        return provider.generate(messages=messages, system_prompt=system_prompt)

    def _scroll_to_bottom(self):
        """Scroll conversation history to bottom"""
        if self.scroll_area and hasattr(self.scroll_area, 'verticalScrollBar'):
            QTimer.singleShot(100, lambda: self.scroll_area.verticalScrollBar().setValue(
                self.scroll_area.verticalScrollBar().maximum()
            ))

    def clear_history(self):
        """Clear conversation history"""
        # Remove all bubbles
        for i in reversed(range(self.history_layout.count())):
            widget = self.history_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        self.conversation_history.clear()

    def set_context(self, context_data: Dict, entity=None):
        """
        Set the context for AI (character data, location data, etc.)

        Args:
            context_data: Dictionary with context information
            entity: The actual entity object (Character, Location, Note, or scene dict)
        """
        # Store context for AI calls
        self.context_data = context_data
        self.current_entity = entity

    def _handle_command(self, command_text: str):
        """
        Handle AI custom commands (#comando)

        Args:
            command_text: Command text (e.g., "#sinossi" or "#espandi")
        """
        from managers.ai.command_parser import AICommandParser

        # Check prerequisites
        if not self.project_manager or not self.project_manager.current_project:
            QMessageBox.warning(self, "No Project", "Please open a project first.")
            return

        if not self.ai_manager:
            QMessageBox.warning(self, "AI Not Available",
                              "AI Manager not initialized. Please check your configuration.")
            return

        parser = AICommandParser()

        # Parse command
        parsed = parser.parse_command(command_text)
        if not parsed:
            self._show_unknown_command(command_text)
            return

        command_name = parsed['command']

        # Handle #help command
        if command_name == 'help':
            self._show_help()
            return

        # Get available commands for this context
        project = self.project_manager.current_project
        available_commands = parser.get_available_commands(
            self.context_type,
            project.ai_commands
        )

        # Find the command
        command = parser.find_command(command_name, available_commands)

        if not command:
            self._show_unknown_command(command_name)
            return

        # Add user message
        user_bubble = AIMessageBubble(command_text, is_user=True)
        self.history_layout.addWidget(user_bubble)

        # Clear input
        self.question_input.clear()

        # Gather variables
        variables = self._gather_variables()

        # Replace variables in template
        final_prompt = parser.replace_variables(command['prompt_template'], variables)

        # Show loading
        loading_bubble = AIMessageBubble("⏳ Generando risposta AI...", is_user=False)
        self.history_layout.addWidget(loading_bubble)

        # Call AI with custom prompt
        QTimer.singleShot(100, lambda: self._call_ai_with_custom_prompt(final_prompt, loading_bubble))

    def _gather_variables(self) -> Dict[str, str]:
        """
        Gather variables for command template replacement

        Returns:
            Dict with variable names and values
        """
        variables = {}

        if self.context_type == "Scene":
            variables['scene_content'] = self.context_data.get('content', '')
            variables['scene_title'] = self.context_data.get('scene_title', '')
            variables['chapter_title'] = self.context_data.get('chapter_title', '')
            variables['word_count'] = str(len(variables['scene_content'].split()))
            # Try to get selected text from parent ManuscriptView
            variables['selected_text'] = self._get_selected_text_from_editor()

        elif self.context_type == "Character":
            variables['character_name'] = self.context_data.get('name', '')
            variables['character_description'] = self.context_data.get('description', '')
            variables['selected_text'] = ''

        elif self.context_type == "Location":
            variables['location_name'] = self.context_data.get('name', '')
            variables['location_description'] = self.context_data.get('description', '')
            variables['location_type'] = self.context_data.get('type', '')
            variables['selected_text'] = ''

        elif self.context_type == "Note":
            variables['note_title'] = self.context_data.get('title', '')
            variables['note_content'] = self.context_data.get('content', '')
            variables['note_tags'] = ', '.join(self.context_data.get('tags', []))
            variables['selected_text'] = ''

        return variables

    def _get_selected_text_from_editor(self) -> str:
        """
        Try to get selected text from editor if available

        Returns:
            Selected text or empty string
        """
        try:
            # Try to get from parent ManuscriptView
            parent = self.parent()
            while parent:
                if hasattr(parent, 'get_selected_text'):
                    return parent.get_selected_text()
                parent = parent.parent() if hasattr(parent, 'parent') else None
        except:
            pass
        return ''

    def _show_help(self):
        """Show available commands help"""
        from managers.ai.command_parser import AICommandParser

        parser = AICommandParser()
        project = self.project_manager.current_project

        available_commands = parser.get_available_commands(
            self.context_type,
            project.ai_commands
        )

        help_text = parser.get_help_text(available_commands, self.context_type)

        help_bubble = AIMessageBubble(help_text, is_user=False)
        self.history_layout.addWidget(help_bubble)
        self._scroll_to_bottom()

        # Clear input
        self.question_input.clear()

    def _show_unknown_command(self, command_name: str):
        """
        Show error for unknown command

        Args:
            command_name: Name of unknown command
        """
        error_text = f"❌ Comando sconosciuto: **#{command_name}**\n\n"
        error_text += "Digita **#help** per vedere i comandi disponibili."

        error_bubble = AIMessageBubble(error_text, is_user=False)
        self.history_layout.addWidget(error_bubble)
        self._scroll_to_bottom()

        # Clear input
        self.question_input.clear()

    def _call_ai_with_custom_prompt(self, prompt: str, loading_bubble):
        """
        Call AI with a custom prompt (for commands)

        Args:
            prompt: Custom prompt to send
            loading_bubble: Loading bubble to replace with response
        """
        try:
            from managers.ai.ai_provider import AIMessage

            # Create message with custom prompt
            messages = [AIMessage(role="user", content=prompt)]

            # Get AI provider
            provider = self.ai_manager.get_provider()
            if not provider:
                loading_bubble.deleteLater()
                error_bubble = AIMessageBubble(
                    "❌ Nessun provider AI disponibile. Configura l'AI in Preferenze.",
                    is_user=False
                )
                self.history_layout.addWidget(error_bubble)
                self._scroll_to_bottom()
                return

            # Call AI (use simple context, command already has full context in prompt)
            response = provider.generate(messages=messages)

            # Remove loading bubble
            loading_bubble.deleteLater()

            if response.success:
                # Add AI response
                ai_bubble = AIMessageBubble(response.content, is_user=False)
                ai_bubble.text_selected.connect(self.text_to_insert.emit)
                self.history_layout.addWidget(ai_bubble)
                self._scroll_to_bottom()
            else:
                # Show error
                error_text = f"❌ Errore AI: {response.error}"
                error_bubble = AIMessageBubble(error_text, is_user=False)
                self.history_layout.addWidget(error_bubble)
                self._scroll_to_bottom()

        except Exception as e:
            loading_bubble.deleteLater()
            error_text = f"❌ Errore durante la chiamata AI: {str(e)}"
            error_bubble = AIMessageBubble(error_text, is_user=False)
            self.history_layout.addWidget(error_bubble)
            self._scroll_to_bottom()
