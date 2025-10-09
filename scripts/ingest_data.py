"""Script to ingest and index documents into the vector store."""

import sys
import os
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import settings
from src.data_ingestion.document_loader import DocumentLoader, load_faq_data
from src.data_ingestion.text_processor import TextProcessor
from src.vector_store.vector_store_manager import VectorStoreManager


def main():
    """Main ingestion pipeline."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Ingest documents into RAG chatbot')
    parser.add_argument('--url', type=str, help='Website URL to ingest')
    parser.add_argument('--urls', type=str, nargs='+', help='Multiple website URLs to ingest (space-separated)')
    parser.add_argument('--skip-faq', action='store_true', help='Skip loading FAQ data')
    parser.add_argument('--skip-files', action='store_true', help='Skip loading files from data/documents')
    args = parser.parse_args()

    print("=" * 60)
    print("RAG Chatbot - Data Ingestion Pipeline")
    print("=" * 60)

    # Step 1: Load documents
    print("\n[1/4] Loading documents...")

    documents = []

    # Option A: Load from FAQ data (default for demo)
    if not args.skip_faq:
        faq_docs = load_faq_data()
        documents.extend(faq_docs)
        print(f"✓ Loaded {len(faq_docs)} FAQ documents")

    # Option B: Load from directory
    if not args.skip_files:
        docs_directory = "./data/documents"
        if os.path.exists(docs_directory):
            additional_docs = DocumentLoader.load_directory(docs_directory)
            documents.extend(additional_docs)
            print(f"✓ Loaded {len(additional_docs)} documents from {docs_directory}")

    # Option C: Load from URL(s)
    if args.url:
        print(f"\n🌐 Loading from URL: {args.url}")
        url_docs = DocumentLoader.load_from_url(args.url)
        documents.extend(url_docs)
        print(f"✓ Loaded {len(url_docs)} documents from URL")

    if args.urls:
        print(f"\n🌐 Loading from {len(args.urls)} URLs...")
        url_docs = DocumentLoader.load_from_urls(args.urls)
        documents.extend(url_docs)
        print(f"✓ Loaded {len(url_docs)} documents from URLs")

    if not documents:
        print("\n✗ No documents found!")
        print("Please provide at least one of:")
        print("  - FAQ data (enabled by default)")
        print("  - Files in ./data/documents/")
        print("  - Website URL with --url flag")
        return

    # Step 2: Process and chunk documents
    print(f"\n[2/4] Processing and chunking documents...")
    print(f"Total documents to process: {len(documents)}")
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
    print("\n✓ Ready to use! Start the API server with: python run_server.py")


if __name__ == "__main__":
    main()
