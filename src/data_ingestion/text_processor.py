"""Text processing and chunking utilities."""

from typing import List
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document


class TextProcessor:
    """Process and chunk documents for embedding."""

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        """
        Initialize text processor.

        Args:
            chunk_size: Maximum size of each text chunk
            chunk_overlap: Number of characters to overlap between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""],
        )

    def chunk_documents(self, documents: List[Document]) -> List[Document]:
        """
        Split documents into smaller chunks.

        Args:
            documents: List of Document objects to chunk

        Returns:
            List of chunked Document objects
        """
        chunked_docs = self.text_splitter.split_documents(documents)

        # Add chunk metadata
        for i, doc in enumerate(chunked_docs):
            doc.metadata['chunk_id'] = i
            doc.metadata['chunk_size'] = len(doc.page_content)

        return chunked_docs

    def preprocess_text(self, text: str) -> str:
        """
        Clean and preprocess text.

        Args:
            text: Raw text to preprocess

        Returns:
            Cleaned text
        """
        # Remove extra whitespace
        text = " ".join(text.split())

        # Remove special characters if needed (optional)
        # text = re.sub(r'[^\w\s\.,!?-]', '', text)

        return text.strip()

    def preprocess_documents(self, documents: List[Document]) -> List[Document]:
        """
        Preprocess all documents.

        Args:
            documents: List of Document objects

        Returns:
            List of preprocessed Document objects
        """
        for doc in documents:
            doc.page_content = self.preprocess_text(doc.page_content)

        return documents

    def process_pipeline(self, documents: List[Document]) -> List[Document]:
        """
        Full processing pipeline: preprocess → chunk.

        Args:
            documents: Raw Document objects

        Returns:
            Processed and chunked Document objects
        """
        print(f"Processing {len(documents)} documents...")

        # Step 1: Preprocess
        processed_docs = self.preprocess_documents(documents)
        print(f"✓ Preprocessed {len(processed_docs)} documents")

        # Step 2: Chunk
        chunked_docs = self.chunk_documents(processed_docs)
        print(f"✓ Created {len(chunked_docs)} chunks")

        return chunked_docs
