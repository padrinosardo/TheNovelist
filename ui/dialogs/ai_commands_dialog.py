"""
AI Commands Management Dialog
Allows users to create, edit, and delete custom AI commands
"""
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                               QListWidget, QLineEdit, QTextEdit, QLabel,
                               QCheckBox, QGroupBox, QMessageBox, QSplitter,
                               QWidget, QFormLayout)
from PySide6.QtCore import Qt
from typing import List, Dict, Optional
from managers.ai.command_parser import AICommandParser


class AICommandsDialog(QDialog):
    """
    Dialog for managing AI custom commands
    """

    def __init__(self, commands: List[Dict], parent=None):
        """
        Initialize dialog

        Args:
            commands: List of command dictionaries
            parent: Parent widget
        """
        super().__init__(parent)
        self.commands = commands.copy()  # Work on a copy
        self.current_command_index: Optional[int] = None
        self.parser = AICommandParser()

        self.setWindowTitle("Gestione Comandi AI")
        self.setMinimumSize(900, 600)

        self._setup_ui()
        self._load_commands()

    def _setup_ui(self):
        """Setup the user interface"""
        layout = QHBoxLayout(self)

        # Create splitter for list and editor
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left side: Commands list
        left_widget = self._create_commands_list()
        splitter.addWidget(left_widget)

        # Right side: Command editor
        right_widget = self._create_command_editor()
        splitter.addWidget(right_widget)

        # Set proportions (30% list, 70% editor)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 7)

        layout.addWidget(splitter)

    def _create_commands_list(self) -> QWidget:
        """Create the commands list widget"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Title
        title = QLabel("Comandi Disponibili")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title)

        # List
        self.commands_list = QListWidget()
        self.commands_list.currentRowChanged.connect(self._on_command_selected)
        layout.addWidget(self.commands_list)

        # Buttons
        buttons_layout = QHBoxLayout()

        self.add_button = QPushButton("➕ Nuovo")
        self.add_button.clicked.connect(self._on_add_command)
        buttons_layout.addWidget(self.add_button)

        self.delete_button = QPushButton("🗑️ Elimina")
        self.delete_button.clicked.connect(self._on_delete_command)
        self.delete_button.setEnabled(False)
        buttons_layout.addWidget(self.delete_button)

        layout.addLayout(buttons_layout)

        return widget

    def _create_command_editor(self) -> QWidget:
        """Create the command editor widget"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Title
        title = QLabel("Dettagli Comando")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title)

        # Form layout
        form = QFormLayout()

        # Name
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("es: sinossi, espandi, dialoghi")
        self.name_input.textChanged.connect(self._on_editor_changed)
        form.addRow("Nome comando (#):", self.name_input)

        # Description
        self.description_input = QLineEdit()
        self.description_input.setPlaceholderText("Breve descrizione del comando")
        self.description_input.textChanged.connect(self._on_editor_changed)
        form.addRow("Descrizione:", self.description_input)

        layout.addLayout(form)

        # Context types
        context_group = QGroupBox("Disponibile in:")
        context_layout = QHBoxLayout()

        self.context_scene = QCheckBox("Scene")
        self.context_scene.stateChanged.connect(self._on_editor_changed)
        context_layout.addWidget(self.context_scene)

        self.context_character = QCheckBox("Personaggi")
        self.context_character.stateChanged.connect(self._on_editor_changed)
        context_layout.addWidget(self.context_character)

        self.context_location = QCheckBox("Luoghi")
        self.context_location.stateChanged.connect(self._on_editor_changed)
        context_layout.addWidget(self.context_location)

        self.context_note = QCheckBox("Note")
        self.context_note.stateChanged.connect(self._on_editor_changed)
        context_layout.addWidget(self.context_note)

        context_layout.addStretch()
        context_group.setLayout(context_layout)
        layout.addWidget(context_group)

        # Prompt template
        template_label = QLabel("Template del prompt:")
        template_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(template_label)

        self.template_input = QTextEdit()
        self.template_input.setPlaceholderText(
            "Inserisci il prompt template. Puoi usare variabili come:\n"
            "- {scene_content}\n"
            "- {scene_title}\n"
            "- {chapter_title}\n"
            "- {character_name}\n"
            "- {selected_text}\n"
            "ecc..."
        )
        self.template_input.textChanged.connect(self._on_editor_changed)
        layout.addWidget(self.template_input)

        # Variables help
        help_label = QLabel(
            "💡 <a href='#'>Vedi variabili disponibili per contesto</a>"
        )
        help_label.setStyleSheet("color: #666; font-size: 11px;")
        help_label.linkActivated.connect(self._show_variables_help)
        layout.addWidget(help_label)

        # Enabled checkbox
        self.enabled_checkbox = QCheckBox("Comando abilitato")
        self.enabled_checkbox.setChecked(True)
        self.enabled_checkbox.stateChanged.connect(self._on_editor_changed)
        layout.addWidget(self.enabled_checkbox)

        # Action buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()

        self.save_button = QPushButton("💾 Salva Modifiche")
        self.save_button.clicked.connect(self._on_save_command)
        self.save_button.setEnabled(False)
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:disabled {
                background-color: #ccc;
            }
        """)
        buttons_layout.addWidget(self.save_button)

        layout.addLayout(buttons_layout)

        # Initially disable editor
        self._set_editor_enabled(False)

        return widget

    def _load_commands(self):
        """Load commands into the list"""
        self.commands_list.clear()

        for cmd in self.commands:
            contexts = ", ".join(cmd.get('context_types', []))
            enabled_icon = "✅" if cmd.get('enabled', True) else "❌"
            item_text = f"{enabled_icon} #{cmd['name']} ({contexts})"
            self.commands_list.addItem(item_text)

    def _on_command_selected(self, index: int):
        """Handle command selection"""
        if index < 0 or index >= len(self.commands):
            return

        self.current_command_index = index
        cmd = self.commands[index]

        # Disable change tracking
        self._block_editor_signals(True)

        # Load command into editor
        self.name_input.setText(cmd.get('name', ''))
        self.description_input.setText(cmd.get('description', ''))
        self.template_input.setPlainText(cmd.get('prompt_template', ''))
        self.enabled_checkbox.setChecked(cmd.get('enabled', True))

        # Load context types
        context_types = cmd.get('context_types', [])
        self.context_scene.setChecked('Scene' in context_types)
        self.context_character.setChecked('Character' in context_types)
        self.context_location.setChecked('Location' in context_types)
        self.context_note.setChecked('Note' in context_types)

        # Re-enable change tracking
        self._block_editor_signals(False)

        # Enable editor and buttons
        self._set_editor_enabled(True)
        self.delete_button.setEnabled(True)
        self.save_button.setEnabled(False)

    def _on_add_command(self):
        """Add a new command"""
        # Create new command
        new_command = {
            'name': 'nuovo_comando',
            'description': 'Nuova descrizione',
            'prompt_template': '',
            'enabled': True,
            'context_types': ['Scene']
        }

        self.commands.append(new_command)
        self._load_commands()

        # Select the new command
        self.commands_list.setCurrentRow(len(self.commands) - 1)

    def _on_delete_command(self):
        """Delete the selected command"""
        if self.current_command_index is None:
            return

        cmd = self.commands[self.current_command_index]

        reply = QMessageBox.question(
            self,
            "Conferma eliminazione",
            f"Sei sicuro di voler eliminare il comando '#{cmd['name']}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            del self.commands[self.current_command_index]
            self._load_commands()
            self.current_command_index = None
            self._set_editor_enabled(False)
            self.delete_button.setEnabled(False)

    def _on_editor_changed(self):
        """Handle editor changes"""
        if self.current_command_index is not None:
            self.save_button.setEnabled(True)

    def _on_save_command(self):
        """Save the current command"""
        if self.current_command_index is None:
            return

        # Validate name
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Errore", "Il nome del comando è obbligatorio.")
            return

        # Check for duplicate names (excluding current)
        for i, cmd in enumerate(self.commands):
            if i != self.current_command_index and cmd['name'].lower() == name.lower():
                QMessageBox.warning(
                    self,
                    "Errore",
                    f"Esiste già un comando con il nome '{name}'."
                )
                return

        # Get context types
        context_types = []
        if self.context_scene.isChecked():
            context_types.append('Scene')
        if self.context_character.isChecked():
            context_types.append('Character')
        if self.context_location.isChecked():
            context_types.append('Location')
        if self.context_note.isChecked():
            context_types.append('Note')

        if not context_types:
            QMessageBox.warning(
                self,
                "Errore",
                "Seleziona almeno un tipo di contesto."
            )
            return

        # Validate template variables
        template = self.template_input.toPlainText()
        for context_type in context_types:
            is_valid, error_msg = self.parser.validate_template(template, context_type)
            if not is_valid:
                reply = QMessageBox.warning(
                    self,
                    "Variabili non valide",
                    f"{error_msg}\n\nVuoi salvare comunque?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.No:
                    return
                break

        # Update command
        self.commands[self.current_command_index] = {
            'name': name,
            'description': self.description_input.text().strip(),
            'prompt_template': template,
            'enabled': self.enabled_checkbox.isChecked(),
            'context_types': context_types
        }

        # Reload list
        self._load_commands()

        # Keep selection
        self.commands_list.setCurrentRow(self.current_command_index)

        self.save_button.setEnabled(False)

        QMessageBox.information(
            self,
            "Salvato",
            f"Comando '#{name}' salvato con successo!"
        )

    def _show_variables_help(self):
        """Show available variables for each context"""
        help_text = self.parser.get_help_text([], 'Scene')  # Get generic help

        # Create custom help with all contexts
        help_text = "# Variabili Disponibili per Contesto\n\n"

        for context_type in ['Scene', 'Character', 'Location', 'Note']:
            variables = self.parser.get_variables_for_context(context_type)
            help_text += f"## {context_type}\n\n"
            for var_name, var_desc in variables:
                help_text += f"- `{{{var_name}}}` - {var_desc}\n"
            help_text += "\n"

        QMessageBox.information(
            self,
            "Variabili Template",
            help_text
        )

    def _set_editor_enabled(self, enabled: bool):
        """Enable or disable the editor"""
        self.name_input.setEnabled(enabled)
        self.description_input.setEnabled(enabled)
        self.template_input.setEnabled(enabled)
        self.enabled_checkbox.setEnabled(enabled)
        self.context_scene.setEnabled(enabled)
        self.context_character.setEnabled(enabled)
        self.context_location.setEnabled(enabled)
        self.context_note.setEnabled(enabled)

    def _block_editor_signals(self, block: bool):
        """Block or unblock editor signals"""
        self.name_input.blockSignals(block)
        self.description_input.blockSignals(block)
        self.template_input.blockSignals(block)
        self.enabled_checkbox.blockSignals(block)
        self.context_scene.blockSignals(block)
        self.context_character.blockSignals(block)
        self.context_location.blockSignals(block)
        self.context_note.blockSignals(block)

    def get_commands(self) -> List[Dict]:
        """Get the modified commands list"""
        return self.commands

    def exec(self) -> bool:
        """
        Execute dialog and return whether changes were accepted

        Returns:
            bool: True if accepted, False if rejected
        """
        # Add dialog buttons at the bottom
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()

        cancel_button = QPushButton("Annulla")
        cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_button)

        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        ok_button.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                padding: 8px 20px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        buttons_layout.addWidget(ok_button)

        # Add to main layout
        self.layout().addLayout(buttons_layout)

        return super().exec() == QDialog.DialogCode.Accepted
