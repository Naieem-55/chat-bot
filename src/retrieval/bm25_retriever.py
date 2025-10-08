"""BM25-based keyword retrieval for hybrid search."""

from typing import List, Dict, Tuple
from rank_bm25 import BM25Okapi
from langchain.docstore.document import Document
import logging

logger = logging.getLogger(__name__)


class BM25Retriever:
    """BM25-based keyword retrieval for exact term matching."""

    def __init__(self, documents: List[Dict] = None, top_k: int = 5):
        """
        Initialize BM25 retriever.

        Args:
            documents: List of document dictionaries with 'content' field
            top_k: Number of top documents to retrieve
        """
        self.top_k = top_k
        self.documents = []
        self.bm25 = None

        if documents:
            self.index_documents(documents)

    def index_documents(self, documents: List[Dict]):
        """
        Index documents for BM25 retrieval.

        Args:
            documents: List of document dictionaries
        """
        self.documents = documents

        # Tokenize documents (simple word splitting)
        tokenized_docs = [
            self._tokenize(doc.get('content', ''))
            for doc in documents
        ]

        # Create BM25 index
        self.bm25 = BM25Okapi(tokenized_docs)

        logger.info(f"Indexed {len(documents)} documents for BM25 retrieval")

    def retrieve(self, query: str) -> List[Tuple[Document, float]]:
        """
        Retrieve documents using BM25 keyword matching.

        Args:
            query: Search query

        Returns:
            List of (Document, score) tuples matching vector retriever format
        """
        if not self.bm25 or not self.documents:
            logger.warning("BM25 index is empty, returning empty results")
            return []

        # Tokenize query
        tokenized_query = self._tokenize(query)

        # Get BM25 scores
        scores = self.bm25.get_scores(tokenized_query)

        # Get top-k document indices
        top_indices = sorted(
            range(len(scores)),
            key=lambda i: scores[i],
            reverse=True
        )[:self.top_k]

        # Return documents as (Document, score) tuples to match vector retriever format
        results = []
        for idx in top_indices:
            doc_dict = self.documents[idx]

            # Create Document object
            doc = Document(
                page_content=doc_dict['content'],
                metadata=doc_dict.get('metadata', {})
            )

            # BM25 scores are similarity (higher is better), convert to distance-like
            # by inverting: lower distance = higher similarity
            distance = 1.0 / (1.0 + float(scores[idx]))

            results.append((doc, distance))

        logger.info(f"BM25 retrieved {len(results)} documents for query: '{query}'")
        return results

    def _tokenize(self, text: str) -> List[str]:
        """
        Simple tokenization by splitting on whitespace and lowercasing.

        Args:
            text: Text to tokenize

        Returns:
            List of tokens
        """
        # Simple word-based tokenization
        # You could enhance this with stemming, stopword removal, etc.
        return text.lower().split()
