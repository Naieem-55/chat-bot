"""FAISS vector store implementation."""

import os
import pickle
from typing import List, Tuple, Dict, Any
import faiss
import numpy as np
from langchain.docstore.document import Document


class FAISSVectorStore:
    """Vector store using FAISS for similarity search."""

    def __init__(self, embedding_dimension: int, index_path: str = None):
        """
        Initialize FAISS vector store.

        Args:
            embedding_dimension: Dimension of embeddings
            index_path: Path to save/load the index
        """
        self.embedding_dimension = embedding_dimension
        self.index_path = index_path
        self.index = None
        self.documents: List[Document] = []
        self.document_embeddings: np.ndarray = None

        # Initialize or load index
        if index_path and os.path.exists(index_path):
            self.load()
        else:
            self.index = faiss.IndexFlatL2(embedding_dimension)
            print(f"✓ Created new FAISS index with dimension {embedding_dimension}")

    def add_documents(self, documents: List[Document], embeddings: np.ndarray):
        """
        Add documents and their embeddings to the vector store.

        Args:
            documents: List of Document objects
            embeddings: Numpy array of embeddings
        """
        if len(documents) != len(embeddings):
            raise ValueError("Number of documents must match number of embeddings")

        # Add embeddings to FAISS index
        self.index.add(embeddings.astype('float32'))

        # Store documents
        self.documents.extend(documents)

        # Store embeddings for reference
        if self.document_embeddings is None:
            self.document_embeddings = embeddings
        else:
            self.document_embeddings = np.vstack([self.document_embeddings, embeddings])

        print(f"✓ Added {len(documents)} documents to vector store")
        print(f"  Total documents: {len(self.documents)}")

    def search(
        self,
        query_embedding: np.ndarray,
        k: int = 5
    ) -> List[Tuple[Document, float]]:
        """
        Search for similar documents.

        Args:
            query_embedding: Query embedding vector
            k: Number of results to return

        Returns:
            List of (Document, distance) tuples
        """
        if self.index.ntotal == 0:
            return []

        # Ensure query is 2D array
        if query_embedding.ndim == 1:
            query_embedding = query_embedding.reshape(1, -1)

        # Search
        k = min(k, self.index.ntotal)  # Don't request more than available
        distances, indices = self.index.search(query_embedding.astype('float32'), k)

        # Return documents with distances
        results = []
        for idx, distance in zip(indices[0], distances[0]):
            if idx < len(self.documents):  # Safety check
                results.append((self.documents[idx], float(distance)))

        return results

    def save(self, path: str = None):
        """
        Save the vector store to disk.

        Args:
            path: Directory path to save the store
        """
        save_path = path or self.index_path

        if not save_path:
            raise ValueError("No save path specified")

        os.makedirs(save_path, exist_ok=True)

        # Save FAISS index
        index_file = os.path.join(save_path, "index.faiss")
        faiss.write_index(self.index, index_file)

        # Save documents and metadata
        docs_file = os.path.join(save_path, "documents.pkl")
        with open(docs_file, 'wb') as f:
            pickle.dump({
                'documents': self.documents,
                'embeddings': self.document_embeddings,
                'dimension': self.embedding_dimension
            }, f)

        print(f"✓ Saved vector store to {save_path}")

    def load(self, path: str = None):
        """
        Load the vector store from disk.

        Args:
            path: Directory path to load the store from
        """
        load_path = path or self.index_path

        if not load_path or not os.path.exists(load_path):
            raise ValueError(f"Invalid load path: {load_path}")

        # Load FAISS index
        index_file = os.path.join(load_path, "index.faiss")
        self.index = faiss.read_index(index_file)

        # Load documents and metadata
        docs_file = os.path.join(load_path, "documents.pkl")
        with open(docs_file, 'rb') as f:
            data = pickle.load(f)
            self.documents = data['documents']
            self.document_embeddings = data['embeddings']
            self.embedding_dimension = data['dimension']

        print(f"✓ Loaded vector store from {load_path}")
        print(f"  Total documents: {len(self.documents)}")

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store."""
        return {
            "total_documents": len(self.documents),
            "total_vectors": self.index.ntotal,
            "embedding_dimension": self.embedding_dimension,
            "index_type": type(self.index).__name__
        }
