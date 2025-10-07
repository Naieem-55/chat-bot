"""Embedding generation using sentence transformers."""

from typing import List
from sentence_transformers import SentenceTransformer
import numpy as np


class EmbeddingGenerator:
    """Generate embeddings for text using sentence transformers."""

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        Initialize embedding generator.

        Args:
            model_name: Name of the sentence transformer model
        """
        self.model_name = model_name
        print(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.embedding_dimension = self.model.get_sentence_embedding_dimension()
        print(f"✓ Model loaded. Embedding dimension: {self.embedding_dimension}")

    def embed_text(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text.

        Args:
            text: Input text

        Returns:
            Embedding vector as numpy array
        """
        return self.model.encode(text, convert_to_numpy=True)

    def embed_batch(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """
        Generate embeddings for a batch of texts.

        Args:
            texts: List of input texts
            batch_size: Batch size for processing

        Returns:
            Array of embedding vectors
        """
        return self.model.encode(
            texts,
            batch_size=batch_size,
            convert_to_numpy=True,
            show_progress_bar=len(texts) > 100
        )

    def get_dimension(self) -> int:
        """Get the embedding dimension."""
        return self.embedding_dimension
