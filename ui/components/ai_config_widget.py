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
    QPushButton, QLabel, QHBoxLayout, QMessageBox
)
from PySide6.QtCore import Signal
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
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        """Setup UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

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
        self.api_key_input.setPlaceholderText("Enter API key...")
        self.api_key_input.setToolTip("API key for cloud AI providers")
        self.api_key_label = QLabel("API Key *:")
        form.addRow(self.api_key_label, self.api_key_input)

        # Model selection (dynamic based on provider)
        self.model_combo = QComboBox()
        self.model_combo.setToolTip("AI model to use")
        form.addRow("Model:", self.model_combo)

        layout.addLayout(form)

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
        self.provider_combo.currentIndexChanged.connect(self._update_provider_fields)
        self.provider_combo.currentIndexChanged.connect(lambda: self.config_changed.emit())
        self.api_key_input.textChanged.connect(lambda: self.config_changed.emit())
        self.model_combo.currentIndexChanged.connect(lambda: self.config_changed.emit())
        self.test_btn.clicked.connect(self._test_connection)

    def _update_provider_fields(self):
        """Update fields based on selected provider"""
        provider = self.provider_combo.currentData()

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
            self.info_label.setText(
                "💡 Ollama - Run AI models locally on your machine (free and private!).\n"
                "Perfect for IP protection. Install from: https://ollama.ai/\n"
                "After installation, run: ollama pull llama3"
            )

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
            dict: AI provider configuration
        """
        provider = self.provider_combo.currentData()
        config = {
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

    def set_config(self, provider_name: str, config: dict):
        """
        Load configuration into widget

        Args:
            provider_name: Provider name to select
            config: Configuration dictionary
        """
        # Set provider
        index = self.provider_combo.findData(provider_name)
        if index >= 0:
            self.provider_combo.setCurrentIndex(index)

        # Set API key (if present)
        api_key = config.get('api_key', '')
        self.api_key_input.setText(api_key)

        # Set model
        model = config.get('model', '')
        if model:
            model_index = self.model_combo.findData(model)
            if model_index >= 0:
                self.model_combo.setCurrentIndex(model_index)

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
