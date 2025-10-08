"""Query reformulation for better retrieval using conversation history."""

from typing import List, Dict, Union, Optional
import logging

logger = logging.getLogger(__name__)


class QueryReformulator:
    """Reformulate user queries using LLM and conversation history."""

    def __init__(self, llm_client):
        """
        Initialize query reformulator.

        Args:
            llm_client: LLM client instance (Claude or HuggingFace)
        """
        self.llm_client = llm_client

    def reformulate(
        self,
        query: str,
        conversation_history: List[Dict[str, str]] = None
    ) -> str:
        """
        Reformulate query using conversation context.

        Args:
            query: Original user query
            conversation_history: Recent conversation history

        Returns:
            Reformulated standalone query
        """
        # If no history or query is already complete, return as-is
        if not conversation_history or len(conversation_history) == 0:
            return query

        # Check if query needs reformulation (contains references like "it", "that", "this")
        if not self._needs_reformulation(query):
            return query

        # Build reformulation prompt
        reformulation_prompt = self._build_reformulation_prompt(query, conversation_history)

        try:
            # Get reformulated query from LLM
            messages = [{'role': 'user', 'content': reformulation_prompt}]

            reformulated = self.llm_client.generate_response(
                system_prompt=self.REFORMULATION_SYSTEM_PROMPT,
                messages=messages,
                stream=False
            )

            # Clean up the response
            reformulated = reformulated.strip().strip('"').strip("'")

            # Validate reformulated query
            if self._is_valid_reformulation(query, reformulated):
                logger.info(f"Reformulated query: '{query}' -> '{reformulated}'")
                return reformulated
            else:
                logger.warning(f"Invalid reformulation, using original: '{query}'")
                return query

        except Exception as e:
            logger.error(f"Error reformulating query: {e}")
            return query  # Fall back to original

    def _needs_reformulation(self, query: str) -> bool:
        """
        Check if query needs reformulation.

        Args:
            query: User query

        Returns:
            True if query contains pronouns or references that need context
        """
        query_lower = query.lower()

        # Pronouns and references that indicate need for context
        reference_words = [
            'it', 'this', 'that', 'these', 'those', 'them', 'they',
            'he', 'she', 'his', 'her', 'their',
            'same', 'also', 'too', 'either',
            'what about', 'how about', 'and the', 'or the'
        ]

        # Check if query is very short (likely a follow-up)
        if len(query.split()) <= 3:
            return True

        # Check for reference words
        for word in reference_words:
            if f' {word} ' in f' {query_lower} ' or query_lower.startswith(word + ' '):
                return True

        # Check for questions without subject
        question_words = ['what', 'how', 'when', 'where', 'why', 'can', 'does', 'is']
        for qword in question_words:
            if query_lower.startswith(qword + ' ') and len(query.split()) <= 5:
                return True

        return False

    def _build_reformulation_prompt(
        self,
        query: str,
        conversation_history: List[Dict[str, str]]
    ) -> str:
        """
        Build prompt for query reformulation.

        Args:
            query: Original query
            conversation_history: Conversation history

        Returns:
            Reformulation prompt
        """
        # Get last few turns (up to 3 exchanges)
        recent_history = conversation_history[-6:] if len(conversation_history) > 6 else conversation_history

        history_text = ""
        for msg in recent_history:
            role = "User" if msg['role'] == 'user' else "Assistant"
            history_text += f"{role}: {msg['content']}\n"

        prompt = f"""Given the following conversation history and a new user question, reformulate the question to be a standalone question that can be understood without the conversation context.

Conversation History:
{history_text}

New User Question: {query}

Reformulated Standalone Question:"""

        return prompt

    def _is_valid_reformulation(self, original: str, reformulated: str) -> bool:
        """
        Validate that reformulation is reasonable.

        Args:
            original: Original query
            reformulated: Reformulated query

        Returns:
            True if reformulation is valid
        """
        # Check length (reformulated shouldn't be too different in length)
        if len(reformulated) > len(original) * 3:
            return False

        # Check if reformulated is too short
        if len(reformulated.split()) < 3:
            return False

        # Check if reformulated is empty or just punctuation
        if not reformulated or reformulated.strip('?.! ') == '':
            return False

        # Check if it contains the reformulation prompt
        if 'reformulated' in reformulated.lower() or 'standalone' in reformulated.lower():
            return False

        return True

    # System prompt for reformulation
    REFORMULATION_SYSTEM_PROMPT = """You are a query reformulation assistant. Your task is to take a user's question that may contain pronouns or references to previous conversation, and reformulate it into a clear, standalone question that can be understood without context.

Rules:
1. Keep the intent and meaning of the original question
2. Replace pronouns (it, this, that, etc.) with specific nouns from the conversation
3. Make the question self-contained and clear
4. Keep it concise and natural
5. Output ONLY the reformulated question, nothing else
6. Do not add explanations or extra text
7. If the original question is already clear and standalone, you may return it as-is

Examples:
Original: "What about the warranty?"
Previous context: User asked about laptop specifications
Reformulated: "What is the warranty for the laptop?"

Original: "How do I return it?"
Previous context: User asked about a product
Reformulated: "How do I return the product?"

Original: "What is your return policy?"
Reformulated: "What is your return policy?"
"""


class HybridRetrieval:
    """Combine original and reformulated queries for better retrieval."""

    def __init__(self, retriever):
        """
        Initialize hybrid retrieval.

        Args:
            retriever: Document retriever instance
        """
        self.retriever = retriever

    def retrieve_with_reformulation(
        self,
        original_query: str,
        reformulated_query: str,
        original_weight: float = 0.3,
        reformulated_weight: float = 0.7
    ) -> List[Dict]:
        """
        Retrieve documents using both original and reformulated queries.

        Args:
            original_query: Original user query
            reformulated_query: Reformulated standalone query
            original_weight: Weight for original query results
            reformulated_weight: Weight for reformulated query results

        Returns:
            Combined and re-ranked documents
        """
        # Retrieve with both queries
        original_results = self.retriever.retrieve(original_query)
        reformulated_results = self.retriever.retrieve(reformulated_query)

        # If queries are the same, just return one set
        if original_query == reformulated_query:
            return reformulated_results

        # Combine and re-rank
        combined = self._combine_results(
            original_results,
            reformulated_results,
            original_weight,
            reformulated_weight
        )

        return combined

    def _combine_results(
        self,
        results1: List[Dict],
        results2: List[Dict],
        weight1: float,
        weight2: float
    ) -> List[Dict]:
        """
        Combine and re-rank results from two queries.

        Uses reciprocal rank fusion for combining results.
        """
        # Create a scoring dictionary
        scores = {}

        # Score results from first query
        for rank, doc in enumerate(results1):
            doc_id = doc['content'][:100]  # Use content prefix as ID
            rrf_score = 1.0 / (rank + 60)  # Reciprocal rank fusion
            scores[doc_id] = scores.get(doc_id, 0) + (rrf_score * weight1)

        # Score results from second query
        for rank, doc in enumerate(results2):
            doc_id = doc['content'][:100]
            rrf_score = 1.0 / (rank + 60)
            scores[doc_id] = scores.get(doc_id, 0) + (rrf_score * weight2)

        # Create document map
        doc_map = {}
        for doc in results1 + results2:
            doc_id = doc['content'][:100]
            if doc_id not in doc_map:
                doc_map[doc_id] = doc

        # Sort by combined score
        sorted_docs = sorted(
            doc_map.items(),
            key=lambda x: scores.get(x[0], 0),
            reverse=True
        )

        # Return top documents
        return [doc for _, doc in sorted_docs[:self.retriever.top_k]]
