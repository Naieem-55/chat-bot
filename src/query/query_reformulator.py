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
    """Combine semantic (vector) and keyword (BM25) retrieval for better results."""

    def __init__(self, vector_retriever, bm25_retriever=None):
        """
        Initialize hybrid retrieval.

        Args:
            vector_retriever: Semantic vector search retriever
            bm25_retriever: Keyword BM25 retriever (optional)
        """
        self.vector_retriever = vector_retriever
        self.bm25_retriever = bm25_retriever

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
        original_results = self.vector_retriever.retrieve(original_query)
        reformulated_results = self.vector_retriever.retrieve(reformulated_query)

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

    def retrieve_hybrid(
        self,
        query: str,
        vector_weight: float = 0.6,
        bm25_weight: float = 0.4
    ) -> List[Dict]:
        """
        Retrieve documents using hybrid semantic + keyword search.

        Args:
            query: Search query
            vector_weight: Weight for semantic vector search
            bm25_weight: Weight for BM25 keyword search

        Returns:
            Combined and re-ranked documents
        """
        # Get vector search results
        vector_results = self.vector_retriever.retrieve(query)

        # If no BM25 retriever, return vector results only
        if not self.bm25_retriever:
            logger.info("No BM25 retriever available, using vector search only")
            return vector_results

        # Get BM25 keyword search results
        bm25_results = self.bm25_retriever.retrieve(query)

        # Combine both result sets
        combined = self._combine_results(
            vector_results,
            bm25_results,
            vector_weight,
            bm25_weight
        )

        logger.info(f"Hybrid retrieval: {len(combined)} documents (vector + BM25)")
        return combined

    def retrieve_full_hybrid(
        self,
        original_query: str,
        reformulated_query: str,
        vector_weight: float = 0.5,
        bm25_weight: float = 0.3,
        reformulation_weight: float = 0.2
    ) -> List[Dict]:
        """
        Full hybrid retrieval: semantic + keyword + query reformulation.

        Combines three retrieval strategies:
        1. Semantic vector search on original query
        2. BM25 keyword search on original query
        3. Semantic vector search on reformulated query

        Args:
            original_query: Original user query
            reformulated_query: Reformulated query with context
            vector_weight: Weight for semantic search
            bm25_weight: Weight for keyword search
            reformulation_weight: Weight for reformulated query

        Returns:
            Combined and re-ranked documents
        """
        results_list = []
        weights = []

        # 1. Vector search on original query
        vector_results = self.vector_retriever.retrieve(original_query)
        results_list.append(vector_results)
        weights.append(vector_weight)

        # 2. BM25 keyword search (if available)
        if self.bm25_retriever:
            bm25_results = self.bm25_retriever.retrieve(original_query)
            results_list.append(bm25_results)
            weights.append(bm25_weight)

        # 3. Vector search on reformulated query (if different)
        if reformulated_query != original_query:
            reformulated_results = self.vector_retriever.retrieve(reformulated_query)
            results_list.append(reformulated_results)
            weights.append(reformulation_weight)

        # Combine all result sets
        if len(results_list) == 1:
            return results_list[0]
        elif len(results_list) == 2:
            return self._combine_results(results_list[0], results_list[1], weights[0], weights[1])
        else:
            return self._combine_multiple_results(results_list, weights)

    def _combine_multiple_results(
        self,
        results_list: List[List],
        weights: List[float]
    ) -> List:
        """
        Combine multiple result sets with different weights.

        Args:
            results_list: List of result sets (can be tuples or dicts)
            weights: Corresponding weights for each result set

        Returns:
            Combined and re-ranked documents
        """
        scores = {}
        doc_map = {}

        for results, weight in zip(results_list, weights):
            for rank, item in enumerate(results):
                if isinstance(item, tuple):
                    doc, _ = item
                    doc_id = doc.page_content[:100]
                    doc_map[doc_id] = item
                else:
                    doc_id = item['content'][:100]
                    doc_map[doc_id] = item

                rrf_score = 1.0 / (rank + 60)
                scores[doc_id] = scores.get(doc_id, 0) + (rrf_score * weight)

                if doc_id not in doc_map:
                    doc_map[doc_id] = item

        # Sort by combined score
        sorted_docs = sorted(
            doc_map.items(),
            key=lambda x: scores.get(x[0], 0),
            reverse=True
        )

        # Return top documents
        top_k = getattr(self.vector_retriever, 'top_k', 5)
        return [doc for _, doc in sorted_docs[:top_k]]

    def _combine_results(
        self,
        results1: List,
        results2: List,
        weight1: float,
        weight2: float
    ) -> List:
        """
        Combine and re-rank results from two queries.

        Uses reciprocal rank fusion for combining results.
        Args can be either List[Tuple[Document, float]] or List[Dict]
        """
        # Create a scoring dictionary
        scores = {}
        doc_map = {}

        # Score results from first query
        for rank, item in enumerate(results1):
            if isinstance(item, tuple):
                doc, _ = item
                doc_id = doc.page_content[:100]  # Use content prefix as ID
                doc_map[doc_id] = item
            else:
                doc_id = item['content'][:100]
                doc_map[doc_id] = item

            rrf_score = 1.0 / (rank + 60)  # Reciprocal rank fusion
            scores[doc_id] = scores.get(doc_id, 0) + (rrf_score * weight1)

        # Score results from second query
        for rank, item in enumerate(results2):
            if isinstance(item, tuple):
                doc, _ = item
                doc_id = doc.page_content[:100]
                if doc_id not in doc_map:
                    doc_map[doc_id] = item
            else:
                doc_id = item['content'][:100]
                if doc_id not in doc_map:
                    doc_map[doc_id] = item

            rrf_score = 1.0 / (rank + 60)
            scores[doc_id] = scores.get(doc_id, 0) + (rrf_score * weight2)

        # Sort by combined score
        sorted_docs = sorted(
            doc_map.items(),
            key=lambda x: scores.get(x[0], 0),
            reverse=True
        )

        # Return top documents
        top_k = getattr(self.vector_retriever, 'top_k', 5)
        return [doc for _, doc in sorted_docs[:top_k]]
