"""Script to ingest and index documents into the vector store."""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import settings
from src.data_ingestion.document_loader import DocumentLoader, load_faq_data
from src.data_ingestion.text_processor import TextProcessor
from src.vector_store.vector_store_manager import VectorStoreManager


def main():
    """Main ingestion pipeline."""
    print("=" * 60)
    print("RAG Chatbot - Data Ingestion Pipeline")
    print("=" * 60)

    # Step 1: Load documents
    print("\n[1/4] Loading documents...")

    # Option A: Load from FAQ data (default for demo)
    documents = load_faq_data()
    print(f"✓ Loaded {len(documents)} FAQ documents")

    # Option B: Load from directory
    docs_directory = "./data/documents"
    if os.path.exists(docs_directory):
        additional_docs = DocumentLoader.load_directory(docs_directory)
        documents.extend(additional_docs)
        print(f"✓ Loaded {len(additional_docs)} documents from {docs_directory}")

    if not documents:
        print("✗ No documents found! Add documents or use FAQ data.")
        return

    # Step 2: Process and chunk documents
    print("\n[2/4] Processing and chunking documents...")
    processor = TextProcessor(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap
    )

    processed_docs = processor.process_pipeline(documents)

    # Step 3: Initialize vector store
    print("\n[3/4] Initializing vector store...")
    vector_store = VectorStoreManager(
        embedding_model=settings.embedding_model,
        vector_db_type=settings.vector_db_type,
        vector_db_path=settings.vector_db_path
    )

    # Step 4: Index documents
    print("\n[4/4] Indexing documents into vector store...")
    vector_store.index_documents(processed_docs)

    # Save vector store
    print("\nSaving vector store...")
    vector_store.save()

    # Display stats
    print("\n" + "=" * 60)
    print("Ingestion Complete!")
    print("=" * 60)
    stats = vector_store.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    print("\n✓ Ready to use! Start the API server with: python -m src.api.main")


if __name__ == "__main__":
    main()
