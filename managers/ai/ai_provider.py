"""
Base abstract class for AI providers
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime


@dataclass
class AIMessage:
    """
    Represents a single message in a conversation

    Attributes:
        role: Message role ('user', 'assistant', 'system')
        content: Message content text
        timestamp: ISO format timestamp
        metadata: Optional metadata dictionary
    """
    role: str  # 'user', 'assistant', 'system'
    content: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'role': self.role,
            'content': self.content,
            'timestamp': self.timestamp,
            'metadata': self.metadata
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'AIMessage':
        """Create AIMessage from dictionary"""
        return cls(
            role=data.get('role', 'user'),
            content=data.get('content', ''),
            timestamp=data.get('timestamp', datetime.now().isoformat()),
            metadata=data.get('metadata', {})
        )


@dataclass
class AIResponse:
    """
    Response from AI provider

    Attributes:
        content: Generated text content
        success: Whether the request was successful
        error: Error message if success is False
        usage: Token usage information (if available)
        metadata: Additional provider-specific metadata
    """
    content: str
    success: bool = True
    error: Optional[str] = None
    usage: Optional[Dict[str, int]] = None  # e.g., {'input_tokens': 100, 'output_tokens': 50}
    metadata: Dict[str, Any] = field(default_factory=dict)


class AIProvider(ABC):
    """
    Abstract base class for AI providers

    All AI providers (Claude, OpenAI, Ollama) must implement this interface
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the provider with configuration

        Args:
            config: Configuration dictionary containing provider-specific settings
                    (e.g., api_key, model, temperature, max_tokens)
        """
        self.config = config
        self._validate_config()

    @abstractmethod
    def _validate_config(self) -> None:
        """
        Validate the configuration

        Raises:
            ValueError: If configuration is invalid or missing required fields
        """
        pass

    @abstractmethod
    def generate(
        self,
        messages: List[AIMessage],
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> AIResponse:
        """
        Generate a response from the AI

        Args:
            messages: Conversation history (list of AIMessage objects)
            system_prompt: Optional system prompt to guide behavior
            temperature: Override default temperature (0.0-1.0, higher = more creative)
            max_tokens: Override default max tokens for response

        Returns:
            AIResponse: The AI response with content and metadata
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if the provider is available and properly configured

        Returns:
            bool: True if provider can be used, False otherwise
        """
        pass

    @abstractmethod
    def get_provider_name(self) -> str:
        """
        Get the provider name for display

        Returns:
            str: Provider name (e.g., 'Claude', 'OpenAI', 'Ollama')
        """
        pass

    def get_default_temperature(self) -> float:
        """
        Get default temperature for this provider

        Returns:
            float: Default temperature value
        """
        return self.config.get('temperature', 0.7)

    def get_default_max_tokens(self) -> int:
        """
        Get default max tokens for this provider

        Returns:
            int: Default max tokens value
        """
        return self.config.get('max_tokens', 2000)

    def generate_with_rag(
        self,
        messages: List[AIMessage],
        project_manager: Any,  # Avoid circular import
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        use_rag: bool = True,
        rag_top_k: int = 5
    ) -> AIResponse:
        """
        Generate a response with optional RAG (Retrieval Augmented Generation) context

        This method enhances the AI generation with relevant project context from
        the RAG knowledge base. It automatically retrieves relevant information
        based on the user's query and injects it into the system prompt.

        Args:
            messages: Conversation history (list of AIMessage objects)
            project_manager: ProjectManager instance to access RAG knowledge base
            system_prompt: Optional system prompt to guide behavior
            temperature: Override default temperature (0.0-1.0, higher = more creative)
            max_tokens: Override default max tokens for response
            use_rag: Whether to use RAG context (default: True)
            rag_top_k: Number of RAG results to retrieve (default: 5)

        Returns:
            AIResponse: The AI response with content and metadata
        """
        # If RAG is disabled or no project manager, use standard generation
        if not use_rag or not project_manager:
            return self.generate(messages, system_prompt, temperature, max_tokens)

        # Extract query from last user message
        user_messages = [msg for msg in messages if msg.role == 'user']
        if not user_messages:
            # No user messages, use standard generation
            return self.generate(messages, system_prompt, temperature, max_tokens)

        query = user_messages[-1].content

        # Retrieve RAG context
        try:
            rag_context = project_manager.get_project_context(query, rag_top_k)

            if rag_context:
                # Inject RAG context into system prompt
                rag_instruction = f"""
# PROJECT CONTEXT

You have access to relevant information from the current project's knowledge base.
Use this context to provide more accurate, consistent, and contextually relevant responses.

{rag_context}

---

Remember to use this project context when answering questions or generating content.
"""
                # Prepend RAG context to system prompt
                if system_prompt:
                    enhanced_system_prompt = rag_instruction + "\n\n" + system_prompt
                else:
                    enhanced_system_prompt = rag_instruction

                # Call standard generate with enhanced prompt
                return self.generate(messages, enhanced_system_prompt, temperature, max_tokens)
            else:
                # No RAG context available, use standard generation
                return self.generate(messages, system_prompt, temperature, max_tokens)

        except Exception as e:
            # RAG failed, fall back to standard generation
            print(f"Warning: RAG context retrieval failed: {e}")
            return self.generate(messages, system_prompt, temperature, max_tokens)
