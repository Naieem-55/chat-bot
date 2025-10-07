"""Claude API client for response generation."""

from typing import List, Dict, Any, Generator
from anthropic import Anthropic
from anthropic.types import Message


class ClaudeClient:
    """Client for Claude API interaction."""

    def __init__(
        self,
        api_key: str,
        model: str = "claude-3-5-sonnet-20241022",
        max_tokens: int = 2048,
        temperature: float = 0.7
    ):
        """
        Initialize Claude client.

        Args:
            api_key: Anthropic API key
            model: Claude model name
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
        """
        self.client = Anthropic(api_key=api_key)
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature

    def generate_response(
        self,
        system_prompt: str,
        messages: List[Dict[str, str]],
        stream: bool = False
    ) -> str:
        """
        Generate response from Claude.

        Args:
            system_prompt: System instructions
            messages: List of message dictionaries with 'role' and 'content'
            stream: Whether to stream the response

        Returns:
            Generated response text
        """
        if stream:
            return self._generate_streaming(system_prompt, messages)
        else:
            return self._generate_non_streaming(system_prompt, messages)

    def _generate_non_streaming(
        self,
        system_prompt: str,
        messages: List[Dict[str, str]]
    ) -> str:
        """Generate non-streaming response."""
        response = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            system=system_prompt,
            messages=messages
        )

        return response.content[0].text

    def _generate_streaming(
        self,
        system_prompt: str,
        messages: List[Dict[str, str]]
    ) -> Generator[str, None, None]:
        """Generate streaming response."""
        with self.client.messages.stream(
            model=self.model,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            system=system_prompt,
            messages=messages
        ) as stream:
            for text in stream.text_stream:
                yield text


class PromptTemplate:
    """Prompt templates for the chatbot."""

    SYSTEM_PROMPT = """You are a helpful customer support assistant for our company. Your role is to:

1. Answer customer questions accurately and professionally
2. Use the provided context from our documentation to inform your responses
3. If the context doesn't contain relevant information, politely say so and offer to help in other ways
4. Be concise but thorough in your answers
5. Maintain a friendly and empathetic tone
6. If you're unsure about something, acknowledge it rather than guessing

Guidelines:
- Always prioritize information from the provided context
- If the question is unclear, ask for clarification
- For account-specific issues, guide users to contact support directly
- Never make up information not present in the context
- Format your responses clearly with bullet points or paragraphs as appropriate"""

    @staticmethod
    def format_user_query(query: str, context: str) -> str:
        """
        Format user query with retrieved context.

        Args:
            query: User's question
            context: Retrieved context from documents

        Returns:
            Formatted prompt
        """
        return f"""Context from our documentation:

{context}

---

Customer Question: {query}

Please provide a helpful and accurate response based on the context above. If the context doesn't contain relevant information for this question, politely let the customer know and suggest alternative ways to get help."""

    @staticmethod
    def format_conversation_history(
        messages: List[Dict[str, str]]
    ) -> List[Dict[str, str]]:
        """
        Format conversation history for Claude API.

        Args:
            messages: List of message dictionaries

        Returns:
            Formatted messages for API
        """
        formatted = []
        for msg in messages:
            role = msg['role']
            content = msg['content']

            # Claude API expects 'user' and 'assistant' roles
            if role in ['user', 'assistant']:
                formatted.append({'role': role, 'content': content})

        return formatted
