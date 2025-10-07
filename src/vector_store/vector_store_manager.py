"""Vector store manager for handling different vector database types."""

from typing import List, Tuple
from langchain.docstore.document import Document
from .embeddings import EmbeddingGenerator
from .faiss_store import FAISSVectorStore


class VectorStoreManager:
    """Manage vector store operations with embedding generation."""

    def __init__(
        self,
        embedding_model: str,
        vector_db_type: str = "faiss",
        vector_db_path: str = "./data/vector_store"
    ):
        """
        Initialize vector store manager.

        Args:
            embedding_model: Name of the embedding model
            vector_db_type: Type of vector database ("faiss" or "pinecone")
            vector_db_path: Path to store vector database
        """
        self.embedding_generator = EmbeddingGenerator(embedding_model)
        self.vector_db_type = vector_db_type
        self.vector_db_path = vector_db_path

        # Initialize vector store
        if vector_db_type == "faiss":
            self.vector_store = FAISSVectorStore(
                embedding_dimension=self.embedding_generator.get_dimension(),
                index_path=vector_db_path
            )
        elif vector_db_type == "pinecone":
            # Pinecone implementation would go here
            raise NotImplementedError("Pinecone support coming soon")
        else:
            raise ValueError(f"Unsupported vector database type: {vector_db_type}")

    def index_documents(self, documents: List[Document]):
        """
        Index documents into the vector store.

        Args:
            documents: List of Document objects to index
        """
        print(f"Generating embeddings for {len(documents)} documents...")

        # Extract text content
        texts = [doc.page_content for doc in documents]

        # Generate embeddings
        embeddings = self.embedding_generator.embed_batch(texts)

        # Add to vector store
        self.vector_store.add_documents(documents, embeddings)

    def search(
        self,
        query: str,
        k: int = 5
    ) -> List[Tuple[Document, float]]:
        """
        Search for similar documents.

        Args:
            query: Search query text
            k: Number of results to return

        Returns:
            List of (Document, similarity_score) tuples
        """
        # Generate query embedding
        query_embedding = self.embedding_generator.embed_text(query)

        # Search vector store
        results = self.vector_store.search(query_embedding, k)

        return results

    def save(self):
        """Save the vector store to disk."""
        if hasattr(self.vector_store, 'save'):
            self.vector_store.save()

    def load(self):
        """Load the vector store from disk."""
        if hasattr(self.vector_store, 'load'):
            self.vector_store.load()

    def get_stats(self):
        """Get vector store statistics."""
        if hasattr(self.vector_store, 'get_stats'):
            return self.vector_store.get_stats()
        return {}
