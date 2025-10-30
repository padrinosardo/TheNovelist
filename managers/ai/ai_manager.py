"""
AI Manager - Factory and configuration management for AI providers
"""
from typing import Optional, Dict, Any, List
from .ai_provider import AIProvider, AIMessage, AIResponse
from .claude_provider import ClaudeProvider
from utils.logging_config import AppLogger
import json
import os


class AIManager:
    """
    Factory and manager for AI providers

    Handles:
    - Provider instantiation based on configuration
    - Configuration storage and loading
    - Provider availability checking
    """

    # Provider registry
    PROVIDERS = {
        'claude': ClaudeProvider,
        # Future: 'openai': OpenAIProvider, 'ollama': OllamaProvider
    }

    # Character development system prompt
    CHARACTER_SYSTEM_PROMPT = """You are an expert creative writing assistant specializing in character development for novels, screenplays, and other narrative works.

Your role is to help writers develop rich, complex, and believable characters through collaborative dialogue. When helping to develop a character:

1. Ask clarifying questions about the story context, genre, and themes
2. Suggest detailed physical descriptions that match the character's background and role
3. Develop psychological profiles including personality traits, fears, desires, and internal conflicts
4. Create comprehensive backgrounds including education, family, formative experiences
5. Suggest character arcs and development opportunities
6. Ensure consistency with the narrative context provided
7. Provide specific, actionable suggestions that can be directly used

Always maintain a collaborative tone, asking for the writer's input and preferences. Format your suggestions clearly with sections like "Physical Description:", "Psychology:", "Background:", etc. when providing comprehensive character details."""

    def __init__(self, config_dir: Optional[str] = None):
        """
        Initialize AI Manager

        Args:
            config_dir: Directory to store configuration (default: ~/.thenovelist/ai_config.json)
        """
        if config_dir is None:
            home = os.path.expanduser("~")
            config_dir = os.path.join(home, ".thenovelist")

        os.makedirs(config_dir, exist_ok=True)
        self.config_file = os.path.join(config_dir, "ai_config.json")

        self.config = self._load_config()
        self._current_provider: Optional[AIProvider] = None

        AppLogger.info("AIManager initialized")

    def _load_config(self) -> Dict[str, Any]:
        """
        Load AI configuration from file

        Returns:
            dict: Configuration dictionary
        """
        default_config = {
            'active_provider': 'claude',
            'providers': {
                'claude': {
                    'api_key': '',
                    'model': 'claude-3-5-sonnet-20241022',
                    'temperature': 0.7,
                    'max_tokens': 2000
                },
                'openai': {
                    'api_key': '',
                    'model': 'gpt-4',
                    'temperature': 0.7,
                    'max_tokens': 2000
                },
                'ollama': {
                    'base_url': 'http://localhost:11434',
                    'model': 'llama2',
                    'temperature': 0.7,
                    'max_tokens': 2000
                }
            }
        }

        if not os.path.exists(self.config_file):
            AppLogger.info("AI config not found, creating default")
            self._save_config(default_config)
            return default_config

        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                AppLogger.info("AI config loaded successfully")
                return config
        except Exception as e:
            AppLogger.error(f"Error loading AI config: {e}")
            return default_config

    def _save_config(self, config: Dict[str, Any]) -> bool:
        """
        Save AI configuration to file

        Args:
            config: Configuration dictionary

        Returns:
            bool: True if saved successfully
        """
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
            AppLogger.info("AI config saved successfully")
            return True
        except Exception as e:
            AppLogger.error(f"Error saving AI config: {e}")
            return False

    def get_provider(self, provider_name: Optional[str] = None) -> Optional[AIProvider]:
        """
        Get an AI provider instance

        Args:
            provider_name: Provider name ('claude', 'openai', 'ollama')
                          If None, uses active_provider from config

        Returns:
            AIProvider: Provider instance or None if not available
        """
        if provider_name is None:
            provider_name = self.config.get('active_provider', 'claude')

        if provider_name not in self.PROVIDERS:
            AppLogger.error(f"Unknown provider: {provider_name}")
            return None

        # Get provider configuration
        provider_config = self.config.get('providers', {}).get(provider_name, {})

        if not provider_config:
            AppLogger.error(f"No configuration for provider: {provider_name}")
            return None

        try:
            provider_class = self.PROVIDERS[provider_name]
            provider = provider_class(provider_config)

            if not provider.is_available():
                AppLogger.warning(f"Provider {provider_name} is not available")
                return None

            AppLogger.info(f"Provider {provider_name} instantiated successfully")
            return provider

        except Exception as e:
            AppLogger.error(f"Error creating provider {provider_name}: {e}")
            return None

    def set_active_provider(self, provider_name: str) -> bool:
        """
        Set the active provider

        Args:
            provider_name: Provider name

        Returns:
            bool: True if set successfully
        """
        if provider_name not in self.PROVIDERS:
            AppLogger.error(f"Unknown provider: {provider_name}")
            return False

        self.config['active_provider'] = provider_name
        return self._save_config(self.config)

    def update_provider_config(self, provider_name: str, config: Dict[str, Any]) -> bool:
        """
        Update configuration for a specific provider

        Args:
            provider_name: Provider name
            config: Configuration dictionary to update

        Returns:
            bool: True if updated successfully
        """
        if provider_name not in self.PROVIDERS:
            AppLogger.error(f"Unknown provider: {provider_name}")
            return False

        if 'providers' not in self.config:
            self.config['providers'] = {}

        if provider_name not in self.config['providers']:
            self.config['providers'][provider_name] = {}

        # Update configuration
        self.config['providers'][provider_name].update(config)

        return self._save_config(self.config)

    def get_available_providers(self) -> List[str]:
        """
        Get list of available (properly configured) providers

        Returns:
            List[str]: List of provider names that are available
        """
        available = []
        for provider_name in self.PROVIDERS.keys():
            provider = self.get_provider(provider_name)
            if provider and provider.is_available():
                available.append(provider_name)

        return available

    def generate_for_character(
        self,
        messages: List[AIMessage],
        provider_name: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> AIResponse:
        """
        Generate AI response for character development

        Uses the character development system prompt automatically

        Args:
            messages: Conversation history
            provider_name: Optional provider name (uses active if None)
            temperature: Override temperature
            max_tokens: Override max tokens

        Returns:
            AIResponse: Generated response
        """
        provider = self.get_provider(provider_name)

        if not provider:
            return AIResponse(
                content="",
                success=False,
                error="No AI provider available. Please configure an API key in settings."
            )

        return provider.generate(
            messages=messages,
            system_prompt=self.CHARACTER_SYSTEM_PROMPT,
            temperature=temperature,
            max_tokens=max_tokens
        )

    def get_config(self) -> Dict[str, Any]:
        """
        Get current configuration

        Returns:
            dict: Configuration dictionary
        """
        return self.config.copy()
