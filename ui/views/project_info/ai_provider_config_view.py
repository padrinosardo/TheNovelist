"""
AI Provider Config View - Per-project AI configuration with auto-save
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QFrame
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QFont
from typing import Optional
from models.project import Project
from ui.components.ai_config_widget import AIConfigWidget


class AIProviderConfigView(QWidget):
    """Per-project AI provider configuration with auto-save - left-aligned layout"""

    # Signal emesso quando i dati devono essere salvati
    auto_save_requested = Signal(dict)  # {provider_name: str, config: dict}

    def __init__(self, ai_manager=None, parent=None):
        super().__init__(parent)
        self._current_project: Optional[Project] = None
        self.ai_manager = ai_manager
        self._setup_ui()

    def _setup_ui(self):
        """Setup UI with left alignment"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Header with status indicator
        header_layout = QHBoxLayout()

        title_label = QLabel("🤖 AI Provider Configuration")
        title_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        self.status_label = QLabel("✓ Saved")
        self.status_label.setStyleSheet("color: #4CAF50; font-size: 12px;")
        header_layout.addWidget(self.status_label)

        main_layout.addLayout(header_layout)

        # Description
        desc_label = QLabel(
            "Configure which AI provider to use for this project. "
            "Each project can have its own AI settings."
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

        # === AI PROVIDER SETTINGS ===
        settings_label = QLabel("PROVIDER SETTINGS")
        settings_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(settings_label)

        # Embedded AI Config Widget (reusable component)
        self.ai_config_widget = AIConfigWidget(ai_manager=self.ai_manager)
        self.ai_config_widget.config_changed.connect(self._on_config_changed)
        layout.addWidget(self.ai_config_widget)

        # === ADDITIONAL INFO ===
        info_label = QLabel("💡 Per-Project AI Configuration")
        info_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(info_label)

        info_text = QLabel(
            "• Each project can use a different AI provider and model\n"
            "• Changes are saved automatically as you edit\n"
            "• You can switch providers at any time\n"
            "• Global AI settings can be configured in Preferences"
        )
        info_text.setWordWrap(True)
        info_text.setStyleSheet("""
            QLabel {
                color: #444;
                font-size: 12px;
                padding: 12px;
                background-color: #f0f8ff;
                border-radius: 6px;
                border-left: 4px solid #2196F3;
            }
        """)
        layout.addWidget(info_text)

        layout.addStretch()

        scroll.setWidget(scroll_widget)
        main_layout.addWidget(scroll)

    def _on_config_changed(self):
        """Called when AI config changes - trigger auto-save"""
        if not self._current_project:
            return

        self.status_label.setText("📝 Editing...")
        self.status_label.setStyleSheet("color: #FF9800; font-size: 12px;")

        # Collect data and emit save request
        data = self._collect_form_data()
        self.auto_save_requested.emit(data)

    def _collect_form_data(self) -> dict:
        """Collect all form data"""
        provider_name = self.ai_config_widget.get_provider_name()
        config = self.ai_config_widget.get_config()

        return {
            'provider_name': provider_name,
            'config': config
        }

    def load_project(self, project: Project):
        """Load project AI configuration with global config fallback"""
        self._current_project = project

        # Block signals during load
        self.ai_config_widget.blockSignals(True)

        # Get AI enabled state
        ai_enabled = getattr(project, 'ai_enabled', True)  # Default to True for backward compatibility

        # Get project config
        project_provider_name = project.ai_provider_name or 'claude'
        project_provider_config = project.ai_provider_config or {}

        # Get global config for fallback (if ai_manager is available)
        global_config = {}
        if self.ai_manager and project_provider_name:
            global_config = self.ai_manager.config.get('providers', {}).get(
                project_provider_name, {}
            )

        # Load config with fallback
        self.ai_config_widget.set_config_with_fallback(
            project_provider_name,
            project_provider_config,
            global_config,
            ai_enabled
        )

        # Re-enable signals
        self.ai_config_widget.blockSignals(False)

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
