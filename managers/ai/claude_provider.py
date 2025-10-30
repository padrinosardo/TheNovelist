"""
Claude AI Provider (Anthropic API)
"""
from typing import List, Optional, Dict, Any
from .ai_provider import AIProvider, AIMessage, AIResponse
from utils.logger import AppLogger


class ClaudeProvider(AIProvider):
    """
    Provider for Claude AI (Anthropic API)

    Configuration:
        - api_key: Anthropic API key (required)
        - model: Model name (default: 'claude-3-5-sonnet-20241022')
        - temperature: Creativity (default: 0.7)
        - max_tokens: Max response length (default: 2000)
    """

    DEFAULT_MODEL = 'claude-3-5-sonnet-20241022'

    def _validate_config(self) -> None:
        """Validate Claude-specific configuration"""
        if 'api_key' not in self.config or not self.config['api_key']:
            raise ValueError("Claude provider requires 'api_key' in configuration")

        # Set defaults
        if 'model' not in self.config:
            self.config['model'] = self.DEFAULT_MODEL
        if 'temperature' not in self.config:
            self.config['temperature'] = 0.7
        if 'max_tokens' not in self.config:
            self.config['max_tokens'] = 2000

        AppLogger.info(f"Claude provider initialized with model: {self.config['model']}")

    def generate(
        self,
        messages: List[AIMessage],
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> AIResponse:
        """
        Generate response using Claude API

        Args:
            messages: Conversation history
            system_prompt: Optional system prompt
            temperature: Override temperature
            max_tokens: Override max tokens

        Returns:
            AIResponse: Generated response with metadata
        """
        try:
            # Import anthropic here to avoid requiring it if not using Claude
            import anthropic
        except ImportError:
            error_msg = "anthropic package not installed. Install with: pip install anthropic"
            AppLogger.error(error_msg)
            return AIResponse(
                content="",
                success=False,
                error=error_msg
            )

        try:
            # Initialize client
            client = anthropic.Anthropic(api_key=self.config['api_key'])

            # Prepare messages for Claude API format
            api_messages = []
            for msg in messages:
                api_messages.append({
                    'role': msg.role,
                    'content': msg.content
                })

            # Prepare parameters
            params = {
                'model': self.config['model'],
                'messages': api_messages,
                'temperature': temperature if temperature is not None else self.get_default_temperature(),
                'max_tokens': max_tokens if max_tokens is not None else self.get_default_max_tokens()
            }

            # Add system prompt if provided
            if system_prompt:
                params['system'] = system_prompt

            AppLogger.info(f"Calling Claude API with {len(api_messages)} messages")

            # Make API call
            response = client.messages.create(**params)

            # Extract response content
            content = response.content[0].text if response.content else ""

            # Extract usage information
            usage = None
            if hasattr(response, 'usage'):
                usage = {
                    'input_tokens': response.usage.input_tokens,
                    'output_tokens': response.usage.output_tokens
                }

            AppLogger.info(f"Claude API response received. Tokens: {usage}")

            return AIResponse(
                content=content,
                success=True,
                error=None,
                usage=usage,
                metadata={
                    'model': self.config['model'],
                    'stop_reason': response.stop_reason if hasattr(response, 'stop_reason') else None
                }
            )

        except Exception as e:
            error_msg = f"Error calling Claude API: {str(e)}"
            AppLogger.error(error_msg)
            return AIResponse(
                content="",
                success=False,
                error=error_msg
            )

    def is_available(self) -> bool:
        """
        Check if Claude provider is available

        Returns:
            bool: True if API key is set and anthropic package is installed
        """
        try:
            import anthropic
            return bool(self.config.get('api_key'))
        except ImportError:
            return False

    def get_provider_name(self) -> str:
        """Get provider name"""
        return "Claude (Anthropic)"
