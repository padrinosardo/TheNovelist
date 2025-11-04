# Multi-AI Integration Plan

## Overview
Integrate multiple AI providers (OpenAI, Anthropic, Ollama) to give users choice and demonstrate architectural capabilities.

---

## Phase 1: OpenAI Integration (Week 1-2)

### Architecture Refactoring

#### 1.1 Create AI Provider Abstraction
**File**: `managers/ai/base_provider.py`

```python
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from dataclasses import dataclass

@dataclass
class AIMessage:
    role: str  # 'system', 'user', 'assistant'
    content: str

@dataclass
class AIResponse:
    content: str
    model: str
    tokens_used: int
    cost: float
    provider: str

class BaseAIProvider(ABC):
    """Base class for all AI providers"""

    @abstractmethod
    def generate(self,
                 messages: List[AIMessage],
                 temperature: float = 0.7,
                 max_tokens: int = 2000) -> AIResponse:
        """Generate completion from messages"""
        pass

    @abstractmethod
    def get_available_models(self) -> List[str]:
        """List available models for this provider"""
        pass

    @abstractmethod
    def validate_credentials(self) -> bool:
        """Check if API credentials are valid"""
        pass

    @abstractmethod
    def get_cost_estimate(self, tokens: int) -> float:
        """Estimate cost for token count"""
        pass
```

**Effort**: 2 hours

---

#### 1.2 Refactor Existing Claude Provider
**File**: `managers/ai/claude_provider.py`

Convert existing `AIManager` to implement `BaseAIProvider`:

```python
from .base_provider import BaseAIProvider, AIMessage, AIResponse
import anthropic

class ClaudeProvider(BaseAIProvider):
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-3-5-sonnet-20240620"

    def generate(self, messages, temperature=0.7, max_tokens=2000):
        # Convert AIMessage to Claude format
        claude_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages if msg.role != "system"
        ]

        system_msg = next((m.content for m in messages if m.role == "system"), None)

        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_msg,
            messages=claude_messages
        )

        return AIResponse(
            content=response.content[0].text,
            model=self.model,
            tokens_used=response.usage.input_tokens + response.usage.output_tokens,
            cost=self._calculate_cost(response.usage),
            provider="anthropic"
        )

    def get_available_models(self):
        return [
            "claude-3-5-sonnet-20240620",
            "claude-3-haiku-20240307",
            "claude-3-opus-20240229"
        ]

    def validate_credentials(self):
        try:
            self.client.messages.create(
                model=self.model,
                max_tokens=10,
                messages=[{"role": "user", "content": "test"}]
            )
            return True
        except:
            return False

    def get_cost_estimate(self, tokens):
        # Claude 3.5 Sonnet pricing (as of 2024)
        input_cost = (tokens * 0.003) / 1000  # $3 per 1M tokens
        output_cost = (tokens * 0.015) / 1000  # $15 per 1M tokens
        return input_cost + output_cost

    def _calculate_cost(self, usage):
        input_cost = (usage.input_tokens * 0.003) / 1000
        output_cost = (usage.output_tokens * 0.015) / 1000
        return input_cost + output_cost
```

**Effort**: 3 hours

---

#### 1.3 Implement OpenAI Provider
**File**: `managers/ai/openai_provider.py`

```python
from .base_provider import BaseAIProvider, AIMessage, AIResponse
from openai import OpenAI

class OpenAIProvider(BaseAIProvider):
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-4-turbo-preview"

    def generate(self, messages, temperature=0.7, max_tokens=2000):
        # Convert AIMessage to OpenAI format
        openai_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]

        response = self.client.chat.completions.create(
            model=self.model,
            messages=openai_messages,
            temperature=temperature,
            max_tokens=max_tokens
        )

        return AIResponse(
            content=response.choices[0].message.content,
            model=self.model,
            tokens_used=response.usage.total_tokens,
            cost=self._calculate_cost(response.usage),
            provider="openai"
        )

    def get_available_models(self):
        return [
            "gpt-4-turbo-preview",
            "gpt-4",
            "gpt-3.5-turbo",
            "gpt-3.5-turbo-16k"
        ]

    def validate_credentials(self):
        try:
            self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "test"}],
                max_tokens=10
            )
            return True
        except:
            return False

    def get_cost_estimate(self, tokens):
        # GPT-4 Turbo pricing
        input_cost = (tokens * 0.01) / 1000  # $10 per 1M tokens
        output_cost = (tokens * 0.03) / 1000  # $30 per 1M tokens
        return input_cost + output_cost

    def _calculate_cost(self, usage):
        input_cost = (usage.prompt_tokens * 0.01) / 1000
        output_cost = (usage.completion_tokens * 0.03) / 1000
        return input_cost + output_cost
```

**Dependencies**: Add to `requirements.txt`:
```
openai>=1.0.0
```

**Effort**: 4 hours

---

#### 1.4 Provider Factory & Manager
**File**: `managers/ai/provider_factory.py`

```python
from typing import Optional
from .base_provider import BaseAIProvider
from .claude_provider import ClaudeProvider
from .openai_provider import OpenAIProvider
from utils.settings import SettingsManager

class AIProviderFactory:
    """Factory for creating AI provider instances"""

    PROVIDERS = {
        'anthropic': ClaudeProvider,
        'openai': OpenAIProvider,
    }

    @staticmethod
    def create(provider_name: str, api_key: str) -> Optional[BaseAIProvider]:
        """Create provider instance"""
        provider_class = AIProviderFactory.PROVIDERS.get(provider_name)
        if provider_class:
            return provider_class(api_key)
        return None

    @staticmethod
    def get_available_providers() -> list:
        """Get list of available provider names"""
        return list(AIProviderFactory.PROVIDERS.keys())
```

**File**: `managers/ai/ai_manager.py` (refactored)

```python
from .provider_factory import AIProviderFactory
from .base_provider import AIMessage
from utils.settings import SettingsManager

class AIManager:
    """Manages AI interactions across multiple providers"""

    def __init__(self):
        self.settings = SettingsManager()
        self.provider = None
        self._initialize_provider()

    def _initialize_provider(self):
        """Initialize the active AI provider"""
        provider_name = self.settings.get('ai_provider', 'anthropic')
        api_key = self.settings.get(f'{provider_name}_api_key', '')

        if api_key:
            self.provider = AIProviderFactory.create(provider_name, api_key)

    def switch_provider(self, provider_name: str, api_key: str):
        """Switch to a different AI provider"""
        new_provider = AIProviderFactory.create(provider_name, api_key)
        if new_provider and new_provider.validate_credentials():
            self.provider = new_provider
            self.settings.set('ai_provider', provider_name)
            self.settings.set(f'{provider_name}_api_key', api_key)
            return True
        return False

    def generate_text(self, prompt: str, context: str = "", **kwargs):
        """Generate text using active provider"""
        if not self.provider:
            raise Exception("No AI provider configured")

        messages = []
        if context:
            messages.append(AIMessage(role="system", content=context))
        messages.append(AIMessage(role="user", content=prompt))

        response = self.provider.generate(messages, **kwargs)
        return response.content

    def get_current_provider(self) -> str:
        """Get name of current provider"""
        return self.settings.get('ai_provider', 'anthropic')

    def get_available_models(self) -> list:
        """Get available models for current provider"""
        if self.provider:
            return self.provider.get_available_models()
        return []
```

**Effort**: 3 hours

---

### UI Implementation

#### 2.1 Settings Dialog Enhancement
**File**: `ui/dialogs/ai_settings_dialog.py`

```python
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout,
                               QLabel, QLineEdit, QPushButton, QComboBox,
                               QGroupBox, QFormLayout, QMessageBox)
from PySide6.QtCore import Qt
from managers.ai.provider_factory import AIProviderFactory

class AISettingsDialog(QDialog):
    """Dialog for configuring AI providers"""

    def __init__(self, ai_manager, parent=None):
        super().__init__(parent)
        self.ai_manager = ai_manager
        self.setWindowTitle("AI Provider Settings")
        self.setMinimumWidth(500)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        # Provider Selection
        provider_group = QGroupBox("AI Provider")
        provider_layout = QFormLayout()

        self.provider_combo = QComboBox()
        self.provider_combo.addItems(AIProviderFactory.get_available_providers())
        current = self.ai_manager.get_current_provider()
        self.provider_combo.setCurrentText(current)
        self.provider_combo.currentTextChanged.connect(self._on_provider_changed)

        provider_layout.addRow("Provider:", self.provider_combo)
        provider_group.setLayout(provider_layout)
        layout.addWidget(provider_group)

        # API Keys
        self.api_key_groups = {}
        for provider in AIProviderFactory.get_available_providers():
            group = self._create_api_key_group(provider)
            self.api_key_groups[provider] = group
            layout.addWidget(group)

        # Model Selection
        model_group = QGroupBox("Model")
        model_layout = QFormLayout()

        self.model_combo = QComboBox()
        self._update_models()

        model_layout.addRow("Model:", self.model_combo)
        model_group.setLayout(model_layout)
        layout.addWidget(model_group)

        # Buttons
        button_layout = QHBoxLayout()

        test_btn = QPushButton("Test Connection")
        test_btn.clicked.connect(self._test_connection)
        button_layout.addWidget(test_btn)

        button_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self._save_settings)
        save_btn.setDefault(True)
        button_layout.addWidget(save_btn)

        layout.addLayout(button_layout)

        self._on_provider_changed(current)

    def _create_api_key_group(self, provider):
        """Create API key input group for provider"""
        group = QGroupBox(f"{provider.title()} API Key")
        layout = QFormLayout()

        api_key_input = QLineEdit()
        api_key_input.setEchoMode(QLineEdit.Password)
        api_key_input.setPlaceholderText(f"Enter your {provider} API key...")

        # Load existing key
        from utils.settings import SettingsManager
        settings = SettingsManager()
        existing_key = settings.get(f'{provider}_api_key', '')
        if existing_key:
            api_key_input.setText(existing_key)

        layout.addRow("API Key:", api_key_input)
        group.setLayout(layout)
        group.setProperty('provider', provider)
        group.setProperty('api_key_input', api_key_input)

        return group

    def _on_provider_changed(self, provider):
        """Handle provider change"""
        # Show/hide relevant API key groups
        for p, group in self.api_key_groups.items():
            group.setVisible(p == provider)

        self._update_models()

    def _update_models(self):
        """Update available models for current provider"""
        self.model_combo.clear()
        models = self.ai_manager.get_available_models()
        self.model_combo.addItems(models)

    def _test_connection(self):
        """Test API connection"""
        provider = self.provider_combo.currentText()
        group = self.api_key_groups[provider]
        api_key_input = group.property('api_key_input')
        api_key = api_key_input.text().strip()

        if not api_key:
            QMessageBox.warning(self, "Missing API Key",
                              f"Please enter your {provider} API key")
            return

        # Test connection
        from managers.ai.provider_factory import AIProviderFactory
        test_provider = AIProviderFactory.create(provider, api_key)

        if test_provider and test_provider.validate_credentials():
            QMessageBox.information(self, "Success",
                                  f"Connection to {provider} successful!")
        else:
            QMessageBox.warning(self, "Failed",
                              f"Failed to connect to {provider}. Check your API key.")

    def _save_settings(self):
        """Save settings"""
        provider = self.provider_combo.currentText()
        group = self.api_key_groups[provider]
        api_key_input = group.property('api_key_input')
        api_key = api_key_input.text().strip()

        if not api_key:
            QMessageBox.warning(self, "Missing API Key",
                              "Please enter an API key")
            return

        # Switch provider
        if self.ai_manager.switch_provider(provider, api_key):
            QMessageBox.information(self, "Saved",
                                  f"AI provider switched to {provider}")
            self.accept()
        else:
            QMessageBox.warning(self, "Failed",
                              "Failed to switch provider. Check your API key.")
```

**Effort**: 5 hours

---

#### 2.2 Menu Integration
**File**: `ui/components/menu_bar.py` (update)

Add to Tools menu:
```python
ai_settings_action = QAction("AI Provider Settings...", self)
ai_settings_action.triggered.connect(self._open_ai_settings)
tools_menu.addAction(ai_settings_action)

def _open_ai_settings(self):
    from ui.dialogs.ai_settings_dialog import AISettingsDialog
    dialog = AISettingsDialog(self.ai_manager)
    dialog.exec()
```

**Effort**: 1 hour

---

### Testing & Documentation

#### 3.1 Unit Tests
**File**: `tests/test_ai_providers.py`

```python
import pytest
from managers.ai.base_provider import AIMessage
from managers.ai.claude_provider import ClaudeProvider
from managers.ai.openai_provider import OpenAIProvider

@pytest.fixture
def mock_claude_key():
    return "test-key-claude"

@pytest.fixture
def mock_openai_key():
    return "test-key-openai"

def test_claude_provider_creation(mock_claude_key):
    provider = ClaudeProvider(mock_claude_key)
    assert provider is not None
    assert len(provider.get_available_models()) > 0

def test_openai_provider_creation(mock_openai_key):
    provider = OpenAIProvider(mock_openai_key)
    assert provider is not None
    assert len(provider.get_available_models()) > 0

def test_cost_estimation():
    provider = OpenAIProvider("test")
    cost = provider.get_cost_estimate(1000)
    assert cost > 0
```

**Effort**: 2 hours

---

#### 3.2 Documentation
**File**: `docs/AI_PROVIDERS.md`

Document:
- How to get API keys for each provider
- Pricing comparison
- Model recommendations for different tasks
- Troubleshooting

**Effort**: 2 hours

---

## Phase 2: Ollama Integration (Week 3)

### Local AI Support

#### 2.1 Ollama Provider
**File**: `managers/ai/ollama_provider.py`

```python
from .base_provider import BaseAIProvider, AIMessage, AIResponse
import requests

class OllamaProvider(BaseAIProvider):
    """Provider for local Ollama models"""

    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.model = "llama3"

    def generate(self, messages, temperature=0.7, max_tokens=2000):
        # Convert to Ollama format
        prompt = "\n".join([f"{m.role}: {m.content}" for m in messages])

        response = requests.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens
                }
            }
        )

        data = response.json()

        return AIResponse(
            content=data['response'],
            model=self.model,
            tokens_used=data.get('eval_count', 0),
            cost=0.0,  # Local = free
            provider="ollama"
        )

    def get_available_models(self):
        """Get locally installed models"""
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            data = response.json()
            return [m['name'] for m in data.get('models', [])]
        except:
            return ["llama3", "mistral", "codellama"]

    def validate_credentials(self):
        """Check if Ollama is running"""
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            return response.status_code == 200
        except:
            return False

    def get_cost_estimate(self, tokens):
        return 0.0  # Local models are free
```

**Effort**: 3 hours

---

## Timeline Summary

### Week 1
- Day 1-2: Architecture refactoring (BaseProvider, ClaudeProvider refactor)
- Day 3-4: OpenAI provider implementation
- Day 5: Provider factory & manager

### Week 2
- Day 1-3: UI implementation (Settings dialog)
- Day 4: Testing & bug fixes
- Day 5: Documentation

### Week 3 (Optional - Ollama)
- Day 1-2: Ollama provider
- Day 3: UI updates for Ollama
- Day 4-5: Testing local models

---

## Success Criteria

- [x] User can switch between Claude and OpenAI seamlessly
- [x] API keys stored securely
- [x] Cost tracking per provider
- [x] Model selection per provider
- [x] Graceful error handling
- [x] Provider validation before switching
- [x] Clean architecture (easily add more providers)

---

## Future Providers (Post-MVP)

- **Google Gemini**: `gemini_provider.py`
- **Cohere**: `cohere_provider.py`
- **Hugging Face**: `huggingface_provider.py`
- **Azure OpenAI**: `azure_openai_provider.py`

Each new provider = 1 file + 1 UI group = ~4 hours effort
