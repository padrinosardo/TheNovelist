"""
AI Writing Guide View - Templates and custom commands with auto-save
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea,
                               QFrame, QComboBox, QTextEdit, QPushButton, QGroupBox,
                               QFormLayout)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QFont
from typing import Optional
from models.project import Project
from managers.ai.template_manager import TemplateManager
from ui.dialogs.ai_commands_dialog import AICommandsDialog


class AIWritingGuideView(QWidget):
    """AI Writing Guide with templates and commands - left-aligned layout"""

    # Signal emesso quando i dati devono essere salvati
    auto_save_requested = Signal(dict)  # {selected_template: str, custom_commands: list}

    def __init__(self, template_manager: TemplateManager = None, parent=None):
        super().__init__(parent)
        self._current_project: Optional[Project] = None
        self.template_manager = template_manager or TemplateManager()
        self._setup_ui()

    def _setup_ui(self):
        """Setup UI with left alignment"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Header with status indicator
        header_layout = QHBoxLayout()

        title_label = QLabel("✍️  AI Writing Guide")
        title_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        self.status_label = QLabel("✓ Saved")
        self.status_label.setStyleSheet("color: #4CAF50; font-size: 12px;")
        header_layout.addWidget(self.status_label)

        main_layout.addLayout(header_layout)

        # Description
        desc_label = QLabel(
            "Configure AI writing templates and custom commands for your project. "
            "Templates guide the AI on genre-specific writing style and conventions."
        )
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #666; font-size: 12px; margin-bottom: 10px;")
        main_layout.addWidget(desc_label)

        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        scroll_widget = QWidget()
        layout = QVBoxLayout(scroll_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)

        # === WRITING TEMPLATE SECTION ===
        template_section = self._create_template_section()
        layout.addWidget(template_section)

        # === AI CUSTOM COMMANDS SECTION (OPT #5) ===
        commands_section = self._create_commands_section()
        layout.addWidget(commands_section)

        layout.addStretch()

        scroll.setWidget(scroll_widget)
        main_layout.addWidget(scroll)

    def _create_template_section(self) -> QWidget:
        """Create the writing template section"""
        group = QGroupBox("📝 Writing Template")
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                border: 2px solid #ddd;
                border-radius: 6px;
                margin-top: 12px;
                padding: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)

        layout = QVBoxLayout()

        # Template selector
        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)

        self.template_combo = QComboBox()
        self.template_combo.setToolTip("Choose a genre-specific writing template")

        # Load available templates
        templates = self.template_manager.get_available_templates()
        for template in templates:
            display_name = f"{template['name']} - {template['description']}"
            self.template_combo.addItem(display_name, template['id'])

        self.template_combo.currentIndexChanged.connect(self._on_template_changed)
        form.addRow("Template Genre:", self.template_combo)

        layout.addLayout(form)

        # Template preview
        preview_label = QLabel("Template Preview:")
        preview_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        preview_label.setStyleSheet("margin-top: 10px;")
        layout.addWidget(preview_label)

        self.template_preview = QTextEdit()
        self.template_preview.setReadOnly(True)
        self.template_preview.setMaximumHeight(300)
        self.template_preview.setStyleSheet("""
            QTextEdit {
                background-color: palette(base);
                color: palette(text);
                border: 1px solid palette(mid);
                border-radius: 4px;
                padding: 10px;
                font-family: 'Courier New', monospace;
                font-size: 11px;
            }
        """)
        self.template_preview.setPlaceholderText("Template content will appear here...")
        layout.addWidget(self.template_preview)

        # Template info
        info_text = QLabel(
            "💡 Templates provide genre-specific guidance to the AI assistant. "
            "The AI will use this template to understand the tone, style, and conventions "
            "appropriate for your project's genre."
        )
        info_text.setWordWrap(True)
        info_text.setStyleSheet("""
            QLabel {
                color: #444;
                font-size: 11px;
                padding: 10px;
                background-color: #e8f4f8;
                border-radius: 4px;
                border-left: 3px solid #2196F3;
                margin-top: 5px;
            }
        """)
        layout.addWidget(info_text)

        group.setLayout(layout)
        return group

    def _create_commands_section(self) -> QWidget:
        """Create the AI Custom Commands section (OPT #5)"""
        group = QGroupBox("⚡ Custom AI Commands")
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                border: 2px solid #ddd;
                border-radius: 6px;
                margin-top: 12px;
                padding: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)

        layout = QVBoxLayout()

        # Commands description
        desc = QLabel(
            "Create custom AI commands for repetitive tasks. Use commands like #expand, "
            "#summarize, or #dialogue in your text to trigger AI assistance."
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #666; font-size: 12px; margin-bottom: 10px;")
        layout.addWidget(desc)

        # Commands summary
        self.commands_summary = QLabel()
        self.commands_summary.setWordWrap(True)
        self.commands_summary.setStyleSheet("""
            QLabel {
                background-color: #f5f5f5;
                padding: 12px;
                border-radius: 4px;
                border: 1px solid #ddd;
                font-size: 12px;
                color: #333;
            }
        """)
        layout.addWidget(self.commands_summary)

        # Manage commands button
        buttons_layout = QHBoxLayout()

        self.manage_commands_btn = QPushButton("⚙️  Manage Custom Commands")
        self.manage_commands_btn.setToolTip("Open dialog to create, edit, and delete custom AI commands")
        self.manage_commands_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #0b7dda;
            }
        """)
        self.manage_commands_btn.clicked.connect(self._on_manage_commands)
        buttons_layout.addWidget(self.manage_commands_btn)
        buttons_layout.addStretch()

        layout.addLayout(buttons_layout)

        # Commands info
        info_text = QLabel(
            "💡 Custom commands let you define reusable AI prompts. For example, "
            "create a #expand command to elaborate on brief notes, or #tone_check "
            "to verify narrative consistency."
        )
        info_text.setWordWrap(True)
        info_text.setStyleSheet("""
            QLabel {
                color: #444;
                font-size: 11px;
                padding: 10px;
                background-color: #fff8e1;
                border-radius: 4px;
                border-left: 3px solid #FFC107;
                margin-top: 5px;
            }
        """)
        layout.addWidget(info_text)

        group.setLayout(layout)
        return group

    def _on_template_changed(self):
        """Handle template selection change"""
        if not self._current_project:
            return

        template_id = self.template_combo.currentData()

        # Load and preview template
        try:
            # Use get_template_with_project_data which expects a Project object
            template_content = self.template_manager.get_template_with_project_data(
                template_id,
                self._current_project
            )

            if template_content:
                # Show first 1000 chars in preview
                preview_text = template_content[:1000]
                if len(template_content) > 1000:
                    preview_text += "\n\n... (template continues)"

                self.template_preview.setPlainText(preview_text)
            else:
                self.template_preview.setPlainText("Template not found or empty")
        except Exception as e:
            import traceback
            print(f"Error loading template '{template_id}': {str(e)}")
            traceback.print_exc()
            self.template_preview.setPlainText(f"Error loading template: {str(e)}")

        # Update status and trigger auto-save
        self.status_label.setText("📝 Editing...")
        self.status_label.setStyleSheet("color: #FF9800; font-size: 12px;")

        data = self._collect_form_data()
        self.auto_save_requested.emit(data)

    def _on_manage_commands(self):
        """Open AI Commands management dialog"""
        if not self._current_project:
            return

        # Get current commands from project (use ai_commands)
        commands = self._current_project.ai_commands or []

        # Open dialog
        dialog = AICommandsDialog(commands, parent=self)
        if dialog.exec():
            # User clicked Save - update project
            updated_commands = dialog.get_commands()
            self._current_project.ai_commands = updated_commands

            # Update summary display
            self._update_commands_summary()

            # Trigger auto-save
            self.status_label.setText("📝 Saving...")
            self.status_label.setStyleSheet("color: #FF9800; font-size: 12px;")

            data = self._collect_form_data()
            self.auto_save_requested.emit(data)

    def _update_commands_summary(self):
        """Update the commands summary display"""
        if not self._current_project:
            self.commands_summary.setText("No project loaded")
            return

        commands = self._current_project.ai_commands or []

        if not commands:
            self.commands_summary.setText("📋 No custom commands defined yet. Click 'Manage Custom Commands' to create your first command.")
        else:
            command_names = [f"#{cmd['name']}" for cmd in commands]
            summary = f"📋 {len(commands)} custom command(s) defined:\n"
            summary += ", ".join(command_names[:10])  # Show first 10
            if len(commands) > 10:
                summary += f", ... and {len(commands) - 10} more"
            self.commands_summary.setText(summary)

    def _collect_form_data(self) -> dict:
        """Collect all form data"""
        return {
            'selected_template': self.template_combo.currentData(),
            'custom_commands': self._current_project.ai_commands if self._current_project else []
        }

    def load_project(self, project: Project):
        """Load project AI writing guide settings"""
        self._current_project = project

        # Block signals during load
        self.template_combo.blockSignals(True)

        # Load selected template (use ai_writing_template)
        if project.ai_writing_template:
            template_idx = self.template_combo.findData(project.ai_writing_template)
            if template_idx >= 0:
                self.template_combo.setCurrentIndex(template_idx)
        else:
            # Default to first template (default.md)
            self.template_combo.setCurrentIndex(0)

        # Re-enable signals
        self.template_combo.blockSignals(False)

        # Load template preview by calling _on_template_changed without triggering auto-save
        # We temporarily disconnect the auto_save_requested signal
        try:
            self.template_combo.currentIndexChanged.disconnect(self._on_template_changed)
        except:
            pass

        # Manually load the template preview
        template_id = self.template_combo.currentData()
        if template_id:
            try:
                # Use get_template_with_project_data which expects a Project object
                template_content = self.template_manager.get_template_with_project_data(
                    template_id,
                    self._current_project
                )

                if template_content:
                    # Show first 1000 chars in preview
                    preview_text = template_content[:1000]
                    if len(template_content) > 1000:
                        preview_text += "\n\n... (template continues)"

                    self.template_preview.setPlainText(preview_text)
                else:
                    self.template_preview.setPlainText("Template not found or empty")
            except Exception as e:
                import traceback
                print(f"Error loading template '{template_id}': {str(e)}")
                traceback.print_exc()
                self.template_preview.setPlainText(f"Error loading template: {str(e)}")

        # Reconnect the signal
        self.template_combo.currentIndexChanged.connect(self._on_template_changed)

        # Update commands summary
        self._update_commands_summary()

        # Update status
        self.status_label.setText("✓ Saved")
        self.status_label.setStyleSheet("color: #4CAF50; font-size: 12px;")

    def on_save_success(self):
        """Called when save completes successfully"""
        from datetime import datetime
        time_str = datetime.now().strftime("%H:%M")
        self.status_label.setText(f"✓ Saved {time_str}")
        self.status_label.setStyleSheet("color: #4CAF50; font-size: 12px;")

    def on_save_error(self, error_msg: str):
        """Called when save fails"""
        self.status_label.setText("⚠️ Error saving")
        self.status_label.setStyleSheet("color: #f44336; font-size: 12px;")
        self.status_label.setToolTip(error_msg)
