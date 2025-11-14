"""
AI Configuration Widget - Reusable component for AI provider selection

This widget provides a unified interface for configuring AI providers
(Claude, OpenAI, Ollama) and can be used in multiple places:
- New Project Dialog
- Project Info View
- Global AI Settings
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QComboBox, QLineEdit,
    QPushButton, QLabel, QHBoxLayout, QMessageBox, QCheckBox
)
from PySide6.QtCore import Signal
from PySide6.QtGui import QClipboard
from typing import Optional


class AIConfigWidget(QWidget):
    """Reusable widget for AI provider configuration"""

    # Signal emitted when config changes
    config_changed = Signal()

    def __init__(self, ai_manager=None, parent=None):
        """
        Initialize AI Config Widget

        Args:
            ai_manager: AIManager instance (optional, for testing connection)
            parent: Parent widget
        """
        super().__init__(parent)
        self.ai_manager = ai_manager
        self._is_using_global_key = False  # Track if using global API key
        self._api_key_visible = False  # Track API key visibility
        self._global_configs = {}  # Store global configs for all providers
        self._project_configs = {}  # Store project configs for all providers
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        """Setup UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # Enable AI checkbox
        self.enable_ai_checkbox = QCheckBox("Enable AI assistance for this project")
        self.enable_ai_checkbox.setChecked(True)
        self.enable_ai_checkbox.setToolTip("Uncheck to disable all AI features for this project")
        self.enable_ai_checkbox.setStyleSheet("""
            QCheckBox {
                font-weight: bold;
                font-size: 13px;
                padding: 5px;
            }
        """)
        layout.addWidget(self.enable_ai_checkbox)

        form = QFormLayout()
        form.setSpacing(10)

        # Provider selection
        self.provider_combo = QComboBox()
        self.provider_combo.addItem("🟣 Claude (Anthropic)", "claude")
        self.provider_combo.addItem("🟢 OpenAI (GPT)", "openai")
        self.provider_combo.addItem("🔵 Ollama (Local)", "ollama")
        self.provider_combo.setToolTip("Choose which AI provider to use for this project")
        form.addRow("AI Provider *:", self.provider_combo)

        # API Key (dynamic visibility based on provider)
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_input.setPlaceholderText("Leave empty to use global API key...")
        self.api_key_input.setToolTip("API key for cloud AI providers. Leave empty to use global configuration.")

        # API Key layout with Show/Hide and Copy buttons
        api_key_layout = QHBoxLayout()
        api_key_layout.addWidget(self.api_key_input, stretch=1)

        # Show/Hide button
        self.show_api_btn = QPushButton("👁")
        self.show_api_btn.setFixedWidth(40)
        self.show_api_btn.setToolTip("Show/Hide API key")
        self.show_api_btn.setStyleSheet("""
            QPushButton {
                background-color: #9E9E9E;
                color: white;
                border: none;
                padding: 5px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #757575;
            }
        """)
        api_key_layout.addWidget(self.show_api_btn)

        # Copy button
        self.copy_api_btn = QPushButton("📋")
        self.copy_api_btn.setFixedWidth(40)
        self.copy_api_btn.setToolTip("Copy API key to clipboard")
        self.copy_api_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 5px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        api_key_layout.addWidget(self.copy_api_btn)

        self.api_key_label = QLabel("API Key:")
        form.addRow(self.api_key_label, api_key_layout)

        # API Key status indicator (global vs project)
        self.api_key_status_label = QLabel()
        self.api_key_status_label.setWordWrap(True)
        self.api_key_status_label.setStyleSheet("""
            QLabel {
                color: #666;
                font-size: 11px;
                font-style: italic;
                padding: 4px 8px;
                background-color: #f0f8ff;
                border-radius: 4px;
                border-left: 3px solid #2196F3;
            }
        """)
        form.addRow("", self.api_key_status_label)

        # Model selection (dynamic based on provider)
        self.model_combo = QComboBox()
        self.model_combo.setToolTip("AI model to use")
        self.model_combo_label = QLabel("Model:")
        form.addRow(self.model_combo_label, self.model_combo)

        layout.addLayout(form)

        # Store form container for enabling/disabling
        self.form_container = form

        # Test connection button
        test_layout = QHBoxLayout()
        self.test_btn = QPushButton("🧪 Test Connection")
        self.test_btn.setMaximumWidth(150)
        self.test_btn.setToolTip("Test connection to the selected AI provider")
        self.test_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0b7dda;
            }
            QPushButton:disabled {
                background-color: #ccc;
            }
        """)
        test_layout.addWidget(self.test_btn)
        test_layout.addStretch()
        layout.addLayout(test_layout)

        # Info label
        self.info_label = QLabel()
        self.info_label.setWordWrap(True)
        self.info_label.setStyleSheet("""
            QLabel {
                color: #666;
                font-style: italic;
                font-size: 11px;
                padding: 8px;
                background-color: #f9f9f9;
                border-radius: 4px;
            }
        """)
        layout.addWidget(self.info_label)

        # Initialize provider fields
        self._update_provider_fields()

    def _connect_signals(self):
        """Connect signals"""
        self.enable_ai_checkbox.stateChanged.connect(self._on_enable_ai_changed)
        self.enable_ai_checkbox.stateChanged.connect(lambda: self.config_changed.emit())
        self.provider_combo.currentIndexChanged.connect(self._update_provider_fields)
        self.provider_combo.currentIndexChanged.connect(lambda: self.config_changed.emit())
        self.api_key_input.textChanged.connect(self._on_api_key_changed)
        self.model_combo.currentIndexChanged.connect(lambda: self.config_changed.emit())
        self.test_btn.clicked.connect(self._test_connection)
        self.show_api_btn.clicked.connect(self._toggle_api_visibility)
        self.copy_api_btn.clicked.connect(self._copy_api_key)

    def _on_enable_ai_changed(self):
        """Handle enable/disable AI checkbox state change"""
        enabled = self.enable_ai_checkbox.isChecked()

        # Enable/disable all AI provider fields
        self.provider_combo.setEnabled(enabled)
        self.api_key_input.setEnabled(enabled)
        self.model_combo.setEnabled(enabled)
        self.test_btn.setEnabled(enabled)
        self.info_label.setEnabled(enabled)
        self.show_api_btn.setEnabled(enabled)
        self.copy_api_btn.setEnabled(enabled)

    def _on_api_key_changed(self):
        """Handle API key text change"""
        # Update status when user types
        self._update_api_key_status()
        self.config_changed.emit()

    def _toggle_api_visibility(self):
        """Toggle API key visibility (show/hide password)"""
        if self._api_key_visible:
            self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.show_api_btn.setText("👁")
            self.show_api_btn.setToolTip("Show API key")
            self._api_key_visible = False
        else:
            self.api_key_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.show_api_btn.setText("🙈")
            self.show_api_btn.setToolTip("Hide API key")
            self._api_key_visible = True

    def _copy_api_key(self):
        """Copy API key to clipboard"""
        api_key = self.api_key_input.text().strip()
        if api_key:
            from PySide6.QtWidgets import QApplication
            clipboard = QApplication.clipboard()
            clipboard.setText(api_key)

            # Visual feedback
            original_text = self.copy_api_btn.text()
            self.copy_api_btn.setText("✓")
            self.copy_api_btn.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    padding: 5px;
                    border-radius: 4px;
                }
            """)

            # Reset after 1 second
            from PySide6.QtCore import QTimer
            QTimer.singleShot(1000, lambda: self._reset_copy_button(original_text))
        else:
            QMessageBox.information(
                self,
                "No API Key",
                "No API key to copy. The field is empty."
            )

    def _reset_copy_button(self, original_text):
        """Reset copy button to original state"""
        self.copy_api_btn.setText(original_text)
        self.copy_api_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 5px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)

    def _reload_api_key_for_provider(self, provider_name: str):
        """
        Reload API key when provider changes

        This ensures that when switching providers, we show the correct API key
        (either from project config or global config fallback).

        Args:
            provider_name: Provider name to reload key for
        """
        # Skip for Ollama (no API key needed)
        if provider_name == 'ollama':
            self.api_key_input.setText('')
            self._is_using_global_key = False
            return

        # Get stored configs for this provider
        project_config = self._project_configs.get(provider_name, {})
        global_config = self._global_configs.get(provider_name, {})

        # Determine which API key to show
        project_api_key = project_config.get('api_key', '').strip()
        global_api_key = global_config.get('api_key', '').strip()

        # Block signals to avoid triggering config_changed
        self.api_key_input.blockSignals(True)

        if project_api_key:
            # Project has its own API key for this provider
            self.api_key_input.setText(project_api_key)
            self._is_using_global_key = False
        elif global_api_key:
            # Project doesn't have key, use global key
            self.api_key_input.setText(global_api_key)
            self._is_using_global_key = True
        else:
            # No API key available for this provider
            self.api_key_input.setText('')
            self._is_using_global_key = False

        self.api_key_input.blockSignals(False)

        # Update status indicator
        self._update_api_key_status()

    def _update_api_key_status(self):
        """Update API key status label based on current state"""
        provider = self.provider_combo.currentData()

        # Hide for Ollama (no API key needed)
        if provider == 'ollama':
            self.api_key_status_label.hide()
            return

        self.api_key_status_label.show()

        project_key = self.api_key_input.text().strip()

        if project_key:
            # User has entered a project-specific API key
            self._is_using_global_key = False
            self.api_key_status_label.setText(
                "📋 Using project-specific API key"
            )
            self.api_key_status_label.setStyleSheet("""
                QLabel {
                    color: #666;
                    font-size: 11px;
                    font-style: italic;
                    padding: 4px 8px;
                    background-color: #e8f5e9;
                    border-radius: 4px;
                    border-left: 3px solid #4CAF50;
                }
            """)
        else:
            # Field is empty - using global key
            if self._is_using_global_key:
                self.api_key_status_label.setText(
                    "🌐 Using global API key (leave empty to use global configuration)"
                )
                self.api_key_status_label.setStyleSheet("""
                    QLabel {
                        color: #666;
                        font-size: 11px;
                        font-style: italic;
                        padding: 4px 8px;
                        background-color: #f0f8ff;
                        border-radius: 4px;
                        border-left: 3px solid #2196F3;
                    }
                """)
            else:
                # No global key available
                self.api_key_status_label.setText(
                    "⚠️ No API key configured. Please enter an API key or configure global settings."
                )
                self.api_key_status_label.setStyleSheet("""
                    QLabel {
                        color: #666;
                        font-size: 11px;
                        font-style: italic;
                        padding: 4px 8px;
                        background-color: #fff3e0;
                        border-radius: 4px;
                        border-left: 3px solid #FF9800;
                    }
                """)

    def _update_provider_fields(self):
        """Update fields based on selected provider"""
        provider = self.provider_combo.currentData()

        # Reload API key from stored configs when provider changes
        self._reload_api_key_for_provider(provider)

        # Update model combo
        self.model_combo.clear()
        if provider == 'claude':
            self.model_combo.addItem("Claude 3.5 Sonnet (Best)", "claude-3-5-sonnet-20240620")
            self.model_combo.addItem("Claude 3 Opus", "claude-3-opus-20240229")
            self.model_combo.addItem("Claude 3 Sonnet", "claude-3-sonnet-20240229")
            self.model_combo.addItem("Claude 3 Haiku (Fast)", "claude-3-haiku-20240307")
            self.model_combo.setCurrentIndex(3)  # Default to Haiku (economico)
            self.api_key_input.show()
            self.api_key_label.show()
            self.show_api_btn.show()
            self.copy_api_btn.show()
            self.api_key_input.setPlaceholderText("sk-ant-...")
            self.info_label.setText(
                "💡 Claude by Anthropic - Excellent for creative writing and character development.\n"
                "Get your API key at: https://console.anthropic.com/"
            )
        elif provider == 'openai':
            self.model_combo.addItem("GPT-4 Turbo (Best)", "gpt-4-turbo-preview")
            self.model_combo.addItem("GPT-4", "gpt-4")
            self.model_combo.addItem("GPT-3.5 Turbo (Fast)", "gpt-3.5-turbo")
            self.model_combo.addItem("GPT-3.5 Turbo 16K", "gpt-3.5-turbo-16k")
            self.api_key_input.show()
            self.api_key_label.show()
            self.show_api_btn.show()
            self.copy_api_btn.show()
            self.api_key_input.setPlaceholderText("sk-...")
            self.info_label.setText(
                "💡 OpenAI - Versatile and widely used for various writing tasks.\n"
                "Get your API key at: https://platform.openai.com/api-keys"
            )
        elif provider == 'ollama':
            self.model_combo.addItem("Llama 3 (Recommended)", "llama3")
            self.model_combo.addItem("Llama 2", "llama2")
            self.model_combo.addItem("Mistral", "mistral")
            self.model_combo.addItem("CodeLlama", "codellama")
            self.model_combo.addItem("Phi", "phi")
            self.api_key_input.hide()  # No API key for Ollama
            self.api_key_label.hide()
            self.show_api_btn.hide()
            self.copy_api_btn.hide()
            self.info_label.setText(
                "💡 Ollama - Run AI models locally on your machine (free and private!).\n"
                "Perfect for IP protection. Install from: https://ollama.ai/\n"
                "After installation, run: ollama pull llama3"
            )

        # Update API key status when provider changes
        self._update_api_key_status()
        self.config_changed.emit()

    def _test_connection(self):
        """Test connection to selected provider"""
        if not self.ai_manager:
            QMessageBox.information(
                self,
                "Test Not Available",
                "AI Manager not provided. Connection test is not available."
            )
            return

        provider_name = self.provider_combo.currentData()
        config = self.get_config()

        # Validate config first
        valid, error_msg = self.validate()
        if not valid:
            QMessageBox.warning(self, "Validation Error", error_msg)
            return

        # Import providers
        try:
            from managers.ai.claude_provider import ClaudeProvider
            from managers.ai.openai_provider import OpenAIProvider
            from managers.ai.ollama_provider import OllamaProvider

            providers = {
                'claude': ClaudeProvider,
                'openai': OpenAIProvider,
                'ollama': OllamaProvider
            }

            self.test_btn.setEnabled(False)
            self.test_btn.setText("Testing...")

            try:
                provider_class = providers[provider_name]
                provider = provider_class(config)

                if provider.is_available():
                    QMessageBox.information(
                        self,
                        "Connection Successful",
                        f"✅ Successfully connected to {provider.get_provider_name()}!\n\n"
                        "You can now use this AI provider for character development."
                    )
                else:
                    QMessageBox.warning(
                        self,
                        "Connection Failed",
                        f"❌ Could not connect to {provider.get_provider_name()}.\n\n"
                        "Please check:\n"
                        "- API key is correct (for cloud providers)\n"
                        "- Ollama server is running (for local AI)\n"
                        "- Internet connection is working"
                    )
            finally:
                self.test_btn.setEnabled(True)
                self.test_btn.setText("🧪 Test Connection")

        except Exception as e:
            self.test_btn.setEnabled(True)
            self.test_btn.setText("🧪 Test Connection")
            QMessageBox.critical(
                self,
                "Error",
                f"Error testing connection:\n{str(e)}"
            )

    def get_config(self) -> dict:
        """
        Get current AI configuration

        Returns:
            dict: AI provider configuration with 'ai_enabled' field
        """
        provider = self.provider_combo.currentData()
        config = {
            'ai_enabled': self.enable_ai_checkbox.isChecked(),
            'model': self.model_combo.currentData(),
            'temperature': 0.7,
            'max_tokens': 2000
        }

        # Add API key for cloud providers
        if provider in ['claude', 'openai']:
            config['api_key'] = self.api_key_input.text().strip()

        # Add base_url for Ollama
        if provider == 'ollama':
            config['base_url'] = 'http://localhost:11434'

        return config

    def get_provider_name(self) -> str:
        """
        Get selected provider name

        Returns:
            str: Provider name ('claude', 'openai', 'ollama')
        """
        return self.provider_combo.currentData()

    def set_config(self, provider_name: str, config: dict, ai_enabled: bool = True):
        """
        Load configuration into widget (legacy method, calls set_config_with_fallback)

        Args:
            provider_name: Provider name to select
            config: Configuration dictionary
            ai_enabled: Whether AI is enabled (default: True)
        """
        # Call new method with empty global config (backward compatibility)
        self.set_config_with_fallback(provider_name, config, {}, ai_enabled)

    def set_config_with_fallback(
        self,
        provider_name: str,
        project_config: dict,
        global_config: dict,
        ai_enabled: bool = True
    ):
        """
        Load configuration into widget with global config fallback

        This method shows the global API key if the project config doesn't have one,
        allowing users to see what key is being used while keeping the project config clean.

        Args:
            provider_name: Provider name to select
            project_config: Project-specific configuration dictionary
            global_config: Global configuration dictionary (fallback)
            ai_enabled: Whether AI is enabled (default: True)
        """
        # Store configs for later use when provider changes
        self._project_configs[provider_name] = project_config.copy()
        self._global_configs[provider_name] = global_config.copy()

        # Load ALL global configs from ai_manager if available (for provider switching)
        if self.ai_manager:
            all_global_configs = self.ai_manager.config.get('providers', {})
            for prov_name, prov_config in all_global_configs.items():
                if prov_name not in self._global_configs:
                    self._global_configs[prov_name] = prov_config.copy()

        # Set AI enabled state
        self.enable_ai_checkbox.setChecked(ai_enabled)
        self._on_enable_ai_changed()  # Update widget states

        # Set provider (block signals to avoid triggering reload)
        self.provider_combo.blockSignals(True)
        index = self.provider_combo.findData(provider_name)
        if index >= 0:
            self.provider_combo.setCurrentIndex(index)
        self.provider_combo.blockSignals(False)

        # IMPORTANT: Update provider fields manually since signals were blocked
        # This ensures model combo is populated with correct models for the provider
        self._update_provider_fields()

        # Determine which API key to show
        project_api_key = project_config.get('api_key', '').strip()
        global_api_key = global_config.get('api_key', '').strip()

        if project_api_key:
            # Project has its own API key
            self.api_key_input.setText(project_api_key)
            self._is_using_global_key = False
        elif global_api_key:
            # Project doesn't have API key, show global key
            self.api_key_input.setText(global_api_key)
            self._is_using_global_key = True
        else:
            # No API key available
            self.api_key_input.setText('')
            self._is_using_global_key = False

        # Set model (prefer project, fallback to global)
        model = project_config.get('model') or global_config.get('model', '')
        if model:
            model_index = self.model_combo.findData(model)
            if model_index >= 0:
                self.model_combo.setCurrentIndex(model_index)
            else:
                # Model not found in the list (e.g., wrong provider model)
                # Select the first model as default
                if self.model_combo.count() > 0:
                    self.model_combo.setCurrentIndex(0)

        # Update status indicator
        self._update_api_key_status()

    def validate(self, require_api_key: bool = False) -> tuple[bool, str]:
        """
        Validate current configuration

        Args:
            require_api_key: If True, API key is required for cloud providers.
                           If False (default), API key is optional.

        Returns:
            tuple: (is_valid, error_message)
        """
        provider = self.provider_combo.currentData()

        # Check API key for cloud providers (only if required)
        if require_api_key and provider in ['claude', 'openai']:
            api_key = self.api_key_input.text().strip()
            if not api_key:
                provider_label = self.provider_combo.currentText()
                return False, f"Please enter {provider_label} API key"

            # Basic validation of API key format
            if provider == 'claude' and not api_key.startswith('sk-ant-'):
                return False, "Claude API keys should start with 'sk-ant-'"
            if provider == 'openai' and not api_key.startswith('sk-'):
                return False, "OpenAI API keys should start with 'sk-'"

        return True, ""

    def clear(self):
        """Clear all fields"""
        self.provider_combo.setCurrentIndex(0)
        self.api_key_input.clear()
