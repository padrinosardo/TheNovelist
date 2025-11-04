"""
Ollama AI Provider (Local AI)
"""
from typing import List, Optional, Dict, Any
from .ai_provider import AIProvider, AIMessage, AIResponse
from utils.logger import AppLogger
import requests


class OllamaProvider(AIProvider):
    """
    Provider for Ollama (Local AI)

    Configuration:
        - base_url: Ollama server URL (default: 'http://localhost:11434')
        - model: Model name (default: 'llama3')
        - temperature: Creativity (default: 0.7)
        - max_tokens: Max response length (default: 2000)
    """

    DEFAULT_BASE_URL = 'http://localhost:11434'
    DEFAULT_MODEL = 'llama3'

    def _validate_config(self) -> None:
        """Validate Ollama-specific configuration"""
        # Set defaults
        if 'base_url' not in self.config:
            self.config['base_url'] = self.DEFAULT_BASE_URL
        if 'model' not in self.config:
            self.config['model'] = self.DEFAULT_MODEL
        if 'temperature' not in self.config:
            self.config['temperature'] = 0.7
        if 'max_tokens' not in self.config:
            self.config['max_tokens'] = 2000

        AppLogger.info(f"Ollama provider initialized with model: {self.config['model']}")

    def generate(
        self,
        messages: List[AIMessage],
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> AIResponse:
        """
        Generate response using Ollama API

        Args:
            messages: Conversation history
            system_prompt: Optional system prompt
            temperature: Override temperature
            max_tokens: Override max tokens

        Returns:
            AIResponse: Generated response with metadata
        """
        try:
            # Build prompt from messages
            prompt_parts = []

            if system_prompt:
                prompt_parts.append(f"System: {system_prompt}")

            for msg in messages:
                role = msg.role.capitalize()
                prompt_parts.append(f"{role}: {msg.content}")

            # Add final "Assistant:" to prompt response
            prompt_parts.append("Assistant:")
            prompt = "\n\n".join(prompt_parts)

            # Prepare request parameters
            params = {
                'model': self.config['model'],
                'prompt': prompt,
                'stream': False,
                'options': {
                    'temperature': temperature if temperature is not None else self.get_default_temperature(),
                    'num_predict': max_tokens if max_tokens is not None else self.get_default_max_tokens()
                }
            }

            AppLogger.info(f"Calling Ollama API at {self.config['base_url']}")

            # Make API call
            response = requests.post(
                f"{self.config['base_url']}/api/generate",
                json=params,
                timeout=120  # 2 minutes timeout for local processing
            )

            response.raise_for_status()
            data = response.json()

            # Extract response content
            content = data.get('response', '')

            # Extract usage information
            usage = None
            if 'eval_count' in data or 'prompt_eval_count' in data:
                usage = {
                    'input_tokens': data.get('prompt_eval_count', 0),
                    'output_tokens': data.get('eval_count', 0),
                    'total_tokens': data.get('prompt_eval_count', 0) + data.get('eval_count', 0),
                    'cost_usd': 0.0  # Local models are free!
                }

            AppLogger.info(f"Ollama API response received. Tokens: {usage}")

            return AIResponse(
                content=content,
                success=True,
                error=None,
                usage=usage,
                metadata={
                    'model': self.config['model'],
                    'done': data.get('done', False),
                    'total_duration': data.get('total_duration'),
                    'load_duration': data.get('load_duration'),
                    'prompt_eval_duration': data.get('prompt_eval_duration'),
                    'eval_duration': data.get('eval_duration')
                }
            )

        except requests.exceptions.ConnectionError as e:
            error_msg = (
                f"Cannot connect to Ollama at {self.config['base_url']}. "
                "Make sure Ollama is running. Install from https://ollama.ai/"
            )
            AppLogger.error(error_msg)
            return AIResponse(
                content="",
                success=False,
                error=error_msg
            )
        except requests.exceptions.Timeout:
            error_msg = "Ollama request timed out. The model might be too large or your system is slow."
            AppLogger.error(error_msg)
            return AIResponse(
                content="",
                success=False,
                error=error_msg
            )
        except Exception as e:
            error_msg = f"Error calling Ollama API: {str(e)}"
            AppLogger.error(error_msg)
            return AIResponse(
                content="",
                success=False,
                error=error_msg
            )

    def get_available_models(self) -> list:
        """
        Get list of locally installed Ollama models

        Returns:
            list: List of model identifiers
        """
        try:
            response = requests.get(
                f"{self.config['base_url']}/api/tags",
                timeout=5
            )
            response.raise_for_status()
            data = response.json()

            models = [model['name'] for model in data.get('models', [])]

            if models:
                AppLogger.info(f"Found {len(models)} Ollama models installed")
                return models
            else:
                # Return default models if none installed
                AppLogger.warning("No Ollama models found, returning defaults")
                return ['llama3', 'llama2', 'mistral', 'codellama', 'phi']

        except Exception as e:
            AppLogger.warning(f"Could not fetch Ollama models: {e}")
            # Return common models as fallback
            return ['llama3', 'llama2', 'mistral', 'codellama', 'phi']

    def is_available(self) -> bool:
        """
        Check if Ollama provider is available

        Returns:
            bool: True if Ollama server is running and reachable
        """
        try:
            response = requests.get(
                f"{self.config['base_url']}/api/tags",
                timeout=3
            )
            return response.status_code == 200
        except:
            return False

    def get_provider_name(self) -> str:
        """Get provider name"""
        return "Ollama (Local AI)"
