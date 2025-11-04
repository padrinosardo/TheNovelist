"""
AI Settings Dialog - Configure AI providers and API keys
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel,
    QLineEdit, QComboBox, QDoubleSpinBox, QSpinBox, QPushButton,
    QGroupBox, QMessageBox, QTabWidget, QWidget, QTextEdit
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from managers.ai import AIManager
from utils.logger import AppLogger


class AISettingsDialog(QDialog):
    """
    Dialog for configuring AI providers

    Allows users to:
    - Select active provider (Claude, OpenAI, Ollama)
    - Configure API keys
    - Adjust generation parameters (temperature, max_tokens)
    """

    def __init__(self, ai_manager: AIManager, parent=None):
        super().__init__(parent)
        self.ai_manager = ai_manager
        self.config = ai_manager.get_config()

        self._setup_ui()
        self._load_current_settings()

    def _setup_ui(self):
        """Setup the UI"""
        self.setWindowTitle("⚙️ AI Settings")
        self.setMinimumSize(600, 500)

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)

        # Header
        header = QLabel("AI Provider Configuration")
        header.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        main_layout.addWidget(header)

        info = QLabel("Configure API keys and settings for AI-powered character development")
        info.setStyleSheet("color: #666; font-style: italic;")
        main_layout.addWidget(info)

        # Tab widget for different providers
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        # Claude tab
        self.tabs.addTab(self._create_claude_tab(), "🟣 Claude")

        # OpenAI tab
        self.tabs.addTab(self._create_openai_tab(), "🟢 OpenAI")

        # Ollama tab
        self.tabs.addTab(self._create_ollama_tab(), "🔵 Ollama")

        # Active provider selection
        active_group = QGroupBox("Active Provider")
        active_layout = QFormLayout()

        self.active_provider_combo = QComboBox()
        self.active_provider_combo.addItem("🟣 Claude (Anthropic)", "claude")
        self.active_provider_combo.addItem("🟢 OpenAI (GPT)", "openai")
        self.active_provider_combo.addItem("🔵 Ollama (Local)", "ollama")
        active_layout.addRow("Active Provider:", self.active_provider_combo)

        active_group.setLayout(active_layout)
        main_layout.addWidget(active_group)

        # Buttons
        buttons_layout = QHBoxLayout()

        self.test_btn = QPushButton("🧪 Test Connection")
        self.test_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #0b7dda;
            }
        """)
        self.test_btn.clicked.connect(self._on_test_connection)
        buttons_layout.addWidget(self.test_btn)

        buttons_layout.addStretch()

        self.save_btn = QPushButton("💾 Save")
        self.save_btn.setStyleSheet("""
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
        """)
        self.save_btn.clicked.connect(self._on_save)
        buttons_layout.addWidget(self.save_btn)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setStyleSheet("""
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
        self.cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(self.cancel_btn)

        main_layout.addLayout(buttons_layout)

    def _create_claude_tab(self) -> QWidget:
        """Create Claude configuration tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Info
        info = QLabel(
            "Claude by Anthropic is recommended for creative writing and character development.\n"
            "Get your API key at: https://console.anthropic.com/"
        )
        info.setWordWrap(True)
        info.setStyleSheet("color: #666; padding: 10px; background-color: #f0f0f0; border-radius: 5px;")
        layout.addWidget(info)

        # Form
        form = QFormLayout()
        form.setSpacing(10)

        self.claude_api_key = QLineEdit()
        self.claude_api_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.claude_api_key.setPlaceholderText("sk-ant-...")
        form.addRow("API Key *:", self.claude_api_key)

        self.claude_model = QComboBox()
        self.claude_model.addItem("Claude 3.5 Sonnet (Recommended)", "claude-3-5-sonnet-20240620")
        self.claude_model.addItem("Claude 3 Opus", "claude-3-opus-20240229")
        self.claude_model.addItem("Claude 3 Sonnet", "claude-3-sonnet-20240229")
        self.claude_model.addItem("Claude 3 Haiku", "claude-3-haiku-20240307")
        form.addRow("Model:", self.claude_model)

        self.claude_temperature = QDoubleSpinBox()
        self.claude_temperature.setRange(0.0, 1.0)
        self.claude_temperature.setSingleStep(0.1)
        self.claude_temperature.setValue(0.7)
        self.claude_temperature.setToolTip("Higher = more creative, Lower = more focused")
        form.addRow("Temperature:", self.claude_temperature)

        self.claude_max_tokens = QSpinBox()
        self.claude_max_tokens.setRange(100, 4000)
        self.claude_max_tokens.setSingleStep(100)
        self.claude_max_tokens.setValue(2000)
        self.claude_max_tokens.setToolTip("Maximum length of AI response")
        form.addRow("Max Tokens:", self.claude_max_tokens)

        layout.addLayout(form)
        layout.addStretch()

        return widget

    def _create_openai_tab(self) -> QWidget:
        """Create OpenAI configuration tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Info
        info = QLabel(
            "OpenAI GPT models are versatile and widely used for creative writing.\n"
            "Get your API key at: https://platform.openai.com/api-keys"
        )
        info.setWordWrap(True)
        info.setStyleSheet("color: #666; padding: 10px; background-color: #f0f0f0; border-radius: 5px;")
        layout.addWidget(info)

        # Form
        form = QFormLayout()
        form.setSpacing(10)

        self.openai_api_key = QLineEdit()
        self.openai_api_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.openai_api_key.setPlaceholderText("sk-...")
        form.addRow("API Key *:", self.openai_api_key)

        self.openai_model = QComboBox()
        self.openai_model.addItem("GPT-4 Turbo (Recommended)", "gpt-4-turbo-preview")
        self.openai_model.addItem("GPT-4", "gpt-4")
        self.openai_model.addItem("GPT-3.5 Turbo", "gpt-3.5-turbo")
        self.openai_model.addItem("GPT-3.5 Turbo 16K", "gpt-3.5-turbo-16k")
        form.addRow("Model:", self.openai_model)

        self.openai_temperature = QDoubleSpinBox()
        self.openai_temperature.setRange(0.0, 1.0)
        self.openai_temperature.setSingleStep(0.1)
        self.openai_temperature.setValue(0.7)
        self.openai_temperature.setToolTip("Higher = more creative, Lower = more focused")
        form.addRow("Temperature:", self.openai_temperature)

        self.openai_max_tokens = QSpinBox()
        self.openai_max_tokens.setRange(100, 4000)
        self.openai_max_tokens.setSingleStep(100)
        self.openai_max_tokens.setValue(2000)
        self.openai_max_tokens.setToolTip("Maximum length of AI response")
        form.addRow("Max Tokens:", self.openai_max_tokens)

        layout.addLayout(form)
        layout.addStretch()

        return widget

    def _create_ollama_tab(self) -> QWidget:
        """Create Ollama configuration tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Info
        info = QLabel(
            "Ollama runs AI models locally on your machine. Free and private.\n"
            "Install from: https://ollama.ai/"
        )
        info.setWordWrap(True)
        info.setStyleSheet("color: #666; padding: 10px; background-color: #f0f0f0; border-radius: 5px;")
        layout.addWidget(info)

        # Coming soon notice
        notice = QLabel("🚧 Ollama provider coming in Step 2")
        notice.setStyleSheet(
            "color: #ff9800; font-weight: bold; padding: 20px; "
            "background-color: #fff3cd; border-radius: 5px; margin: 20px;"
        )
        notice.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(notice)

        # Form (disabled for now)
        form = QFormLayout()
        form.setSpacing(10)

        self.ollama_url = QLineEdit()
        self.ollama_url.setPlaceholderText("http://localhost:11434")
        self.ollama_url.setEnabled(False)
        form.addRow("Base URL:", self.ollama_url)

        self.ollama_model = QComboBox()
        self.ollama_model.addItem("Llama 2", "llama2")
        self.ollama_model.addItem("Mistral", "mistral")
        self.ollama_model.setEnabled(False)
        form.addRow("Model:", self.ollama_model)

        layout.addLayout(form)
        layout.addStretch()

        return widget

    def _load_current_settings(self):
        """Load current settings from config"""
        # Active provider
        active_provider = self.config.get('active_provider', 'claude')
        index = self.active_provider_combo.findData(active_provider)
        if index >= 0:
            self.active_provider_combo.setCurrentIndex(index)

        # Claude settings
        claude_config = self.config.get('providers', {}).get('claude', {})
        self.claude_api_key.setText(claude_config.get('api_key', ''))

        model_index = self.claude_model.findData(claude_config.get('model', 'claude-3-5-sonnet-20241022'))
        if model_index >= 0:
            self.claude_model.setCurrentIndex(model_index)

        self.claude_temperature.setValue(claude_config.get('temperature', 0.7))
        self.claude_max_tokens.setValue(claude_config.get('max_tokens', 2000))

        # OpenAI settings
        openai_config = self.config.get('providers', {}).get('openai', {})
        self.openai_api_key.setText(openai_config.get('api_key', ''))

        openai_model_index = self.openai_model.findData(openai_config.get('model', 'gpt-4-turbo-preview'))
        if openai_model_index >= 0:
            self.openai_model.setCurrentIndex(openai_model_index)

        self.openai_temperature.setValue(openai_config.get('temperature', 0.7))
        self.openai_max_tokens.setValue(openai_config.get('max_tokens', 2000))

        # Ollama settings (when implemented)
        # ollama_config = self.config.get('providers', {}).get('ollama', {})
        # ...

    def _on_test_connection(self):
        """Test connection to active provider"""
        # Get current active provider from combo
        provider_name = self.active_provider_combo.currentData()

        # Save current settings temporarily
        self._save_settings_to_manager()

        # Try to get provider
        provider = self.ai_manager.get_provider(provider_name)

        if not provider:
            QMessageBox.warning(
                self,
                "Connection Failed",
                f"Could not connect to {provider_name}. Please check your configuration."
            )
            return

        if not provider.is_available():
            QMessageBox.warning(
                self,
                "Provider Not Available",
                f"{provider.get_provider_name()} is not available. "
                "Please check your API key and internet connection."
            )
            return

        QMessageBox.information(
            self,
            "Connection Successful",
            f"✅ Successfully connected to {provider.get_provider_name()}!\n\n"
            "You can now use the AI Character Assistant."
        )

    def _save_settings_to_manager(self):
        """Save settings to AI manager (without persisting to disk yet)"""
        # Update Claude config
        claude_config = {
            'api_key': self.claude_api_key.text().strip(),
            'model': self.claude_model.currentData(),
            'temperature': self.claude_temperature.value(),
            'max_tokens': self.claude_max_tokens.value()
        }
        self.ai_manager.update_provider_config('claude', claude_config)

        # Update OpenAI config
        openai_config = {
            'api_key': self.openai_api_key.text().strip(),
            'model': self.openai_model.currentData(),
            'temperature': self.openai_temperature.value(),
            'max_tokens': self.openai_max_tokens.value()
        }
        self.ai_manager.update_provider_config('openai', openai_config)

        # Set active provider
        active_provider = self.active_provider_combo.currentData()
        self.ai_manager.set_active_provider(active_provider)

    def _on_save(self):
        """Save settings"""
        # Validate
        active_provider = self.active_provider_combo.currentData()

        if active_provider == 'claude':
            api_key = self.claude_api_key.text().strip()
            if not api_key:
                QMessageBox.warning(
                    self,
                    "Validation Error",
                    "Please enter your Claude API key."
                )
                return
        elif active_provider == 'openai':
            api_key = self.openai_api_key.text().strip()
            if not api_key:
                QMessageBox.warning(
                    self,
                    "Validation Error",
                    "Please enter your OpenAI API key."
                )
                return

        # Save to manager (this persists to disk)
        self._save_settings_to_manager()

        AppLogger.info(f"AI settings saved. Active provider: {active_provider}")

        self.accept()


