"""Free LLM API client for response generation."""

from typing import List, Dict, Generator
import requests
import json


class HuggingFaceClient:
    """Client for free LLM APIs."""

    # Using Groq's free API (70k tokens/day free tier)
    # Other options: Together AI, Fireworks AI
    FREE_API_URL = "https://api.groq.com/openai/v1/chat/completions"

    # Free models available (updated for 2025)
    FREE_MODELS = {
        "mistral": "llama-3.1-8b-instant",    # Groq - Fast and free
        "llama": "llama-3.3-70b-versatile",   # Groq - Best quality
        "gemma": "gemma2-9b-it",              # Groq - Fast
    }

    def __init__(
        self,
        model: str = "mistral",
        max_tokens: int = 2048,
        temperature: float = 0.7,
        api_key: str = None
    ):
        """
        Initialize free LLM client.

        Args:
            model: Model name or key from FREE_MODELS
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            api_key: Optional API key (Groq offers free tier)
        """
        self.model = self.FREE_MODELS.get(model, self.FREE_MODELS["mistral"])
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.api_key = api_key or "gsk_demo_key_for_testing"  # Demo key for testing

    def generate_response(
        self,
        system_prompt: str,
        messages: List[Dict[str, str]],
        stream: bool = False
    ) -> str:
        """
        Generate response using free API.

        Args:
            system_prompt: System instructions
            messages: List of message dictionaries with 'role' and 'content'
            stream: Whether to stream the response (not implemented)

        Returns:
            Generated response text
        """
        # Format messages in OpenAI-compatible format
        formatted_messages = [{"role": "system", "content": system_prompt}]
        formatted_messages.extend(messages)

        payload = {
            "model": self.model,
            "messages": formatted_messages,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        try:
            response = requests.post(
                self.FREE_API_URL,
                headers=headers,
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"].strip()
            elif response.status_code == 401:
                return "API authentication required. Please get a free API key from console.groq.com and add it to your .env file as HUGGINGFACE_API_KEY"
            elif response.status_code == 429:
                return "Rate limit reached. Please wait a moment and try again."
            else:
                return f"Error: Unable to generate response (Status: {response.status_code}). Response: {response.text}"

        except Exception as e:
            return f"Error generating response: {str(e)}"


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
        Format conversation history for the API.

        Args:
            messages: List of message dictionaries

        Returns:
            Formatted messages for API
        """
        formatted = []
        for msg in messages:
            role = msg['role']
            content = msg['content']

            if role in ['user', 'assistant']:
                formatted.append({'role': role, 'content': content})

        return formatted


# For backwards compatibility
def get_free_api_key_instructions():
    """Instructions for getting a free API key."""
    return """
To get a FREE API key (takes 2 minutes):

1. Go to: https://console.groq.com/
2. Sign up (free, no credit card required)
3. Go to "API Keys" section
4. Create a new API key
5. Add to your .env file:
   HUGGINGFACE_API_KEY=your_groq_api_key_here

Groq offers 70,000 free tokens per day - plenty for development!
"""
