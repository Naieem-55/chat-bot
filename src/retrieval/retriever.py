"""Document retrieval with ranking and filtering."""

from typing import List, Dict, Any, Tuple
from langchain.docstore.document import Document


class DocumentRetriever:
    """Retrieve and rank documents for RAG."""

    def __init__(self, vector_store_manager, top_k: int = 5):
        """
        Initialize retriever.

        Args:
            vector_store_manager: VectorStoreManager instance
            top_k: Number of documents to retrieve
        """
        self.vector_store_manager = vector_store_manager
        self.top_k = top_k

    def retrieve(
        self,
        query: str,
        k: int = None,
        filter_metadata: Dict[str, Any] = None
    ) -> List[Tuple[Document, float]]:
        """
        Retrieve relevant documents for a query.

        Args:
            query: User query
            k: Number of documents to retrieve (overrides default)
            filter_metadata: Optional metadata filters

        Returns:
            List of (Document, score) tuples
        """
        k = k or self.top_k

        # Get documents from vector store
        results = self.vector_store_manager.search(query, k=k * 2)  # Get more for filtering

        # Apply metadata filters if provided
        if filter_metadata:
            results = self._filter_by_metadata(results, filter_metadata)

        # Rank and return top k
        ranked_results = self._rank_results(results, query)
        return ranked_results[:k]

    def _filter_by_metadata(
        self,
        results: List[Tuple[Document, float]],
        filters: Dict[str, Any]
    ) -> List[Tuple[Document, float]]:
        """
        Filter documents by metadata.

        Args:
            results: List of (Document, score) tuples
            filters: Metadata key-value pairs to filter by

        Returns:
            Filtered results
        """
        filtered = []
        for doc, score in results:
            match = all(
                doc.metadata.get(key) == value
                for key, value in filters.items()
            )
            if match:
                filtered.append((doc, score))

        return filtered

    def _rank_results(
        self,
        results: List[Tuple[Document, float]],
        query: str
    ) -> List[Tuple[Document, float]]:
        """
        Rank results by relevance score.

        Args:
            results: List of (Document, score) tuples
            query: Original query

        Returns:
            Ranked results (lower distance = more relevant)
        """
        # FAISS returns L2 distances (lower is better)
        # Results are already sorted by FAISS
        return results

    def format_context(self, results: List[Tuple[Document, float]]) -> str:
        """
        Format retrieved documents into context string.

        Args:
            results: List of (Document, score) tuples

        Returns:
            Formatted context string
        """
        if not results:
            return "No relevant information found."

        context_parts = []
        for i, (doc, score) in enumerate(results, 1):
            source = doc.metadata.get('source', 'Unknown')
            category = doc.metadata.get('category', '')

            context_part = f"[Document {i}]"
            if category:
                context_part += f" Category: {category}"
            context_part += f"\n{doc.page_content}"

            context_parts.append(context_part)

        return "\n\n".join(context_parts)

    def get_retrieval_metadata(
        self,
        results: List[Tuple[Document, float]]
    ) -> List[Dict[str, Any]]:
        """
        Extract metadata from retrieval results.

        Args:
            results: List of (Document, score) tuples

        Returns:
            List of metadata dictionaries
        """
        metadata_list = []
        for doc, score in results:
            metadata = {
                'source': doc.metadata.get('source', 'Unknown'),
                'category': doc.metadata.get('category', ''),
                'relevance_score': round(1 / (1 + score), 3),  # Convert distance to similarity
                'chunk_id': doc.metadata.get('chunk_id', ''),
            }
            metadata_list.append(metadata)

        return metadata_list
