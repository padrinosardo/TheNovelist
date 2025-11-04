"""
OpenAI AI Provider (OpenAI API)
"""
from typing import List, Optional, Dict, Any
from .ai_provider import AIProvider, AIMessage, AIResponse
from utils.logger import AppLogger


class OpenAIProvider(AIProvider):
    """
    Provider for OpenAI API (GPT-4, GPT-3.5, etc.)

    Configuration:
        - api_key: OpenAI API key (required)
        - model: Model name (default: 'gpt-4-turbo-preview')
        - temperature: Creativity (default: 0.7)
        - max_tokens: Max response length (default: 2000)
    """

    DEFAULT_MODEL = 'gpt-4-turbo-preview'

    # Model pricing (per 1M tokens) - as of 2024
    PRICING = {
        'gpt-4-turbo-preview': {'input': 10.00, 'output': 30.00},
        'gpt-4': {'input': 30.00, 'output': 60.00},
        'gpt-3.5-turbo': {'input': 0.50, 'output': 1.50},
        'gpt-3.5-turbo-16k': {'input': 3.00, 'output': 4.00},
    }

    def _validate_config(self) -> None:
        """Validate OpenAI-specific configuration"""
        if 'api_key' not in self.config or not self.config['api_key']:
            raise ValueError("OpenAI provider requires 'api_key' in configuration")

        # Set defaults
        if 'model' not in self.config:
            self.config['model'] = self.DEFAULT_MODEL
        if 'temperature' not in self.config:
            self.config['temperature'] = 0.7
        if 'max_tokens' not in self.config:
            self.config['max_tokens'] = 2000

        AppLogger.info(f"OpenAI provider initialized with model: {self.config['model']}")

    def generate(
        self,
        messages: List[AIMessage],
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> AIResponse:
        """
        Generate response using OpenAI API

        Args:
            messages: Conversation history
            system_prompt: Optional system prompt
            temperature: Override temperature
            max_tokens: Override max tokens

        Returns:
            AIResponse: Generated response with metadata
        """
        try:
            # Import openai here to avoid requiring it if not using OpenAI
            from openai import OpenAI
        except ImportError:
            error_msg = "openai package not installed. Install with: pip install openai"
            AppLogger.error(error_msg)
            return AIResponse(
                content="",
                success=False,
                error=error_msg
            )

        try:
            # Initialize client
            client = OpenAI(api_key=self.config['api_key'])

            # Prepare messages for OpenAI API format
            api_messages = []

            # Add system prompt if provided
            if system_prompt:
                api_messages.append({
                    'role': 'system',
                    'content': system_prompt
                })

            # Add conversation messages
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

            AppLogger.info(f"Calling OpenAI API with {len(api_messages)} messages")

            # Make API call
            response = client.chat.completions.create(**params)

            # Extract response content
            content = response.choices[0].message.content if response.choices else ""

            # Extract usage information
            usage = None
            if hasattr(response, 'usage') and response.usage:
                usage = {
                    'input_tokens': response.usage.prompt_tokens,
                    'output_tokens': response.usage.completion_tokens,
                    'total_tokens': response.usage.total_tokens
                }

                # Calculate cost
                cost = self._calculate_cost(
                    response.usage.prompt_tokens,
                    response.usage.completion_tokens
                )
                usage['cost_usd'] = cost

            AppLogger.info(f"OpenAI API response received. Tokens: {usage}")

            return AIResponse(
                content=content,
                success=True,
                error=None,
                usage=usage,
                metadata={
                    'model': self.config['model'],
                    'finish_reason': response.choices[0].finish_reason if response.choices else None
                }
            )

        except Exception as e:
            error_msg = f"Error calling OpenAI API: {str(e)}"
            AppLogger.error(error_msg)
            return AIResponse(
                content="",
                success=False,
                error=error_msg
            )

    def _calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """
        Calculate cost in USD for the API call

        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens

        Returns:
            float: Cost in USD
        """
        model = self.config['model']
        pricing = self.PRICING.get(model, self.PRICING['gpt-4-turbo-preview'])

        input_cost = (input_tokens / 1_000_000) * pricing['input']
        output_cost = (output_tokens / 1_000_000) * pricing['output']

        return input_cost + output_cost

    def get_available_models(self) -> list:
        """
        Get list of available OpenAI models

        Returns:
            list: List of model identifiers
        """
        return [
            "gpt-4-turbo-preview",
            "gpt-4",
            "gpt-3.5-turbo",
            "gpt-3.5-turbo-16k"
        ]

    def is_available(self) -> bool:
        """
        Check if OpenAI provider is available

        Returns:
            bool: True if API key is set and openai package is installed
        """
        try:
            from openai import OpenAI
            return bool(self.config.get('api_key'))
        except ImportError:
            return False

    def get_provider_name(self) -> str:
        """Get provider name"""
        return "OpenAI (GPT)"
