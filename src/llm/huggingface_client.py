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

    def _format_response(self, text: str) -> str:
        """
        Post-process response to ensure proper paragraph formatting.
        Automatically inserts paragraph breaks where needed.
        """
        import re

        # If already has proper paragraph breaks, return as-is
        if '\n\n' in text and text.count('\n\n') >= 2:
            return text

        # Check if text has NO newlines at all (single block)
        if '\n' not in text:
            # Split into sentences and add paragraph breaks
            sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', text)

            formatted = []
            current_para = []

            for i, sentence in enumerate(sentences):
                sentence = sentence.strip()
                if not sentence:
                    continue

                # Check if sentence is a bullet point indicator
                if '**' in sentence and ':' in sentence:
                    # Heading detected - flush current paragraph
                    if current_para:
                        formatted.append(' '.join(current_para))
                        formatted.append('')  # Blank line
                        current_para = []
                    formatted.append(sentence)
                    formatted.append('')  # Blank line after heading
                elif sentence.startswith('*') or re.match(r'^\d+\.', sentence):
                    # Bullet point - add blank line before first bullet
                    if current_para:
                        formatted.append(' '.join(current_para))
                        formatted.append('')
                        current_para = []
                    formatted.append(sentence)
                else:
                    # Regular sentence - add to current paragraph
                    current_para.append(sentence)

                    # Create paragraph break after 2-3 sentences
                    if len(current_para) >= 2:
                        formatted.append(' '.join(current_para))
                        formatted.append('')  # Blank line
                        current_para = []

            # Add any remaining sentences
            if current_para:
                formatted.append(' '.join(current_para))

            return '\n'.join(formatted)

        # Has single newlines - convert to paragraph breaks
        lines = text.split('\n')
        formatted_lines = []

        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue

            formatted_lines.append(line)

            # Check next line
            next_line = lines[i + 1].strip() if i + 1 < len(lines) else ''

            if next_line:
                # Add blank line before headings or lists
                if next_line.startswith('##') or next_line.startswith('**') or \
                   next_line.startswith('*') or next_line.startswith('-') or \
                   re.match(r'^\d+\.', next_line):
                    if not (line.startswith('*') or line.startswith('-') or re.match(r'^\d+\.', line)):
                        formatted_lines.append('')
                # Add blank line after sentences if next is new thought
                elif (line.endswith('.') or line.endswith('!') or line.endswith('?')) and \
                     next_line and next_line[0].isupper():
                    if len(line.split('. ')) >= 2:
                        formatted_lines.append('')

        return '\n'.join(formatted_lines)

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
                response_text = result["choices"][0]["message"]["content"].strip()
                # Post-process to ensure proper paragraph formatting
                return self._format_response(response_text)
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

    SYSTEM_PROMPT = """You are a professional assistant. You MUST format responses with proper structure.

⚠️ CRITICAL: You will be penalized for writing single-paragraph responses. ALWAYS use multiple paragraphs.

MANDATORY FORMATTING RULES:
1. First paragraph: Direct answer (1-2 sentences ONLY)
2. Second paragraph onwards: Detailed explanation
3. ALWAYS add blank lines between paragraphs (use TWO newlines: \\n\\n)
4. NEVER add extra spaces or empty lines
5. Use bullet points for lists (start with "* ")
6. Maximum 3 sentences per paragraph

EXAMPLE (Good Response):
---
HTML is the standard markup language for creating web pages.

HTML stands for HyperText Markup Language. It describes the structure of web pages using elements and tags.

**Basic Syntax:**
* Elements have opening and closing tags
* Tags are enclosed in angle brackets
* Content goes between the tags

**Example:**
* Heading: `<h1>Title</h1>`
* Paragraph: `<p>Text here</p>`

You can learn more from HTML tutorials and documentation.
---

EXAMPLE (Bad Response - NEVER DO THIS):
---
HTML is the standard markup language for creating web pages and it stands for HyperText Markup Language which describes the structure of web pages using elements and tags where elements have opening and closing tags that are enclosed in angle brackets with content going between the tags like headings which use h1 tags and paragraphs which use p tags and you can learn more from HTML tutorials.
---

STRICT RULES:
✓ ALWAYS start with a short opening paragraph (1-2 sentences)
✓ ALWAYS add blank line after opening
✓ ALWAYS break information into multiple paragraphs
✓ ALWAYS use bullet points for lists of items
✓ NEVER write more than 3 sentences in one paragraph
✓ NEVER write everything in a single block of text

If you have multiple points to make, use bullet points with "* " prefix.
If you have explanations, use separate short paragraphs with blank lines."""

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
