"""Main RAG pipeline orchestration."""

from typing import Dict, Any, List, Generator, Union
import logging
from .vector_store.vector_store_manager import VectorStoreManager
from .retrieval.retriever import DocumentRetriever
from .retrieval.bm25_retriever import BM25Retriever
from .llm.claude_client import ClaudeClient
from .llm.huggingface_client import HuggingFaceClient, PromptTemplate
from .session.session_manager import SessionManager
from .query.query_reformulator import QueryReformulator, HybridRetrieval

logger = logging.getLogger(__name__)


class RAGPipeline:
    """Orchestrate the full RAG pipeline."""

    def __init__(
        self,
        vector_store_manager: VectorStoreManager,
        claude_client: Union[ClaudeClient, HuggingFaceClient],
        session_manager: SessionManager,
        top_k_documents: int = 5,
        use_query_reformulation: bool = True,
        use_bm25: bool = True
    ):
        """
        Initialize RAG pipeline.

        Args:
            vector_store_manager: Vector store manager instance
            claude_client: LLM client instance (Claude or HuggingFace)
            session_manager: Session manager instance
            top_k_documents: Number of documents to retrieve
            use_query_reformulation: Whether to use query reformulation
            use_bm25: Whether to use BM25 keyword search in hybrid retrieval
        """
        self.vector_store = vector_store_manager
        self.retriever = DocumentRetriever(vector_store_manager, top_k=top_k_documents)
        self.claude_client = claude_client
        self.session_manager = session_manager
        self.prompt_template = PromptTemplate

        # BM25 keyword retrieval
        self.bm25_retriever = None
        if use_bm25:
            try:
                # Get all documents from vector store for BM25 indexing
                all_docs = self._get_all_documents()
                if all_docs:
                    self.bm25_retriever = BM25Retriever(all_docs, top_k=top_k_documents)
                    logger.info(f"✓ BM25 keyword search enabled ({len(all_docs)} documents)")
                else:
                    logger.warning("No documents available for BM25 indexing")
            except Exception as e:
                logger.error(f"Failed to initialize BM25: {e}")

        # Query reformulation with hybrid retrieval
        self.use_query_reformulation = use_query_reformulation
        if use_query_reformulation:
            self.query_reformulator = QueryReformulator(claude_client)
            self.hybrid_retrieval = HybridRetrieval(self.retriever, self.bm25_retriever)
            logger.info("✓ Query reformulation enabled")
            logger.info("✓ Hybrid retrieval: Vector (semantic) + BM25 (keyword) + Reformulation")

    def process_query(
        self,
        query: str,
        session_id: str,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Process user query through RAG pipeline.

        Args:
            query: User's question
            session_id: Session identifier
            stream: Whether to stream the response

        Returns:
            Dictionary with response and metadata
        """
        # Step 1: Get conversation history
        history = self.session_manager.get_history(session_id)

        # Step 2: Reformulate query if enabled
        original_query = query
        if self.use_query_reformulation and history:
            reformulated_query = self.query_reformulator.reformulate(query, history)
            logger.info(f"Query: '{query}' -> '{reformulated_query}'")
        else:
            reformulated_query = query

        # Step 3: Retrieve relevant documents with hybrid approach
        if self.use_query_reformulation and reformulated_query != original_query:
            # Full hybrid: Vector + BM25 + Reformulation
            retrieval_results = self.hybrid_retrieval.retrieve_full_hybrid(
                original_query,
                reformulated_query,
                vector_weight=0.5,      # Semantic search weight
                bm25_weight=0.3,        # Keyword search weight
                reformulation_weight=0.2  # Reformulated query weight
            )
        elif self.bm25_retriever:
            # Hybrid: Vector + BM25 only
            retrieval_results = self.hybrid_retrieval.retrieve_hybrid(
                query,
                vector_weight=0.6,
                bm25_weight=0.4
            )
        else:
            # Vector search only
            retrieval_results = self.retriever.retrieve(reformulated_query)

        # Step 4: Format context
        context = self.retriever.format_context(retrieval_results)

        # Step 5: Build messages for LLM (use original query for response)
        messages = self._build_messages(query, context, history)

        # Step 6: Generate response
        if stream:
            response_text = self._generate_streaming_response(messages)
        else:
            response_text = self.claude_client.generate_response(
                system_prompt=PromptTemplate.SYSTEM_PROMPT,
                messages=messages,
                stream=False
            )

        # Step 7: Save to session history
        self.session_manager.add_message(session_id, 'user', query)
        if not stream:  # For streaming, this happens after full response
            self.session_manager.add_message(session_id, 'assistant', response_text)

        # Step 8: Prepare response
        retrieval_metadata = self.retriever.get_retrieval_metadata(retrieval_results)

        response_data = {
            'response': response_text,
            'session_id': session_id,
            'sources': retrieval_metadata,
            'context_used': len(retrieval_results) > 0
        }

        # Add reformulation info if used
        if self.use_query_reformulation and reformulated_query != original_query:
            response_data['reformulated_query'] = reformulated_query

        return response_data

    def _build_messages(
        self,
        query: str,
        context: str,
        history: List[Dict[str, str]]
    ) -> List[Dict[str, str]]:
        """
        Build message list for Claude API.

        Args:
            query: Current user query
            context: Retrieved context
            history: Conversation history

        Returns:
            Formatted message list
        """
        messages = []

        # Add recent history (without timestamps)
        for msg in history:
            messages.append({
                'role': msg['role'],
                'content': msg['content']
            })

        # Add current query with context
        current_message = PromptTemplate.format_user_query(query, context)
        messages.append({
            'role': 'user',
            'content': current_message
        })

        return messages

    def _generate_streaming_response(
        self,
        messages: List[Dict[str, str]]
    ) -> Generator[str, None, None]:
        """Generate streaming response."""
        return self.claude_client.generate_response(
            system_prompt=PromptTemplate.SYSTEM_PROMPT,
            messages=messages,
            stream=True
        )

    def create_session(self) -> str:
        """Create a new conversation session."""
        return self.session_manager.create_session()

    def get_session_history(self, session_id: str) -> List[Dict[str, str]]:
        """Get conversation history for a session."""
        return self.session_manager.get_history(session_id)

    def clear_session(self, session_id: str) -> bool:
        """Clear a session's history."""
        return self.session_manager.delete_session(session_id)

    def _get_all_documents(self) -> List[Dict]:
        """
        Get all documents from vector store for BM25 indexing.

        Returns:
            List of all documents with metadata
        """
        try:
            # Get all documents from vector store
            all_docs = self.vector_store.get_all_documents()
            return all_docs
        except Exception as e:
            logger.error(f"Error getting documents for BM25: {e}")
            return []
