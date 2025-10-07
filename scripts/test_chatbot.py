"""Script to test the chatbot locally without running the server."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import settings
from src.vector_store.vector_store_manager import VectorStoreManager
from src.llm.claude_client import ClaudeClient
from src.session.session_manager import SessionManager
from src.rag_pipeline import RAGPipeline


def main():
    """Test the chatbot with example queries."""
    print("=" * 60)
    print("RAG Chatbot - Interactive Test")
    print("=" * 60)

    # Initialize components
    print("\nInitializing components...")

    vector_store = VectorStoreManager(
        embedding_model=settings.embedding_model,
        vector_db_type=settings.vector_db_type,
        vector_db_path=settings.vector_db_path
    )

    claude_client = ClaudeClient(
        api_key=settings.anthropic_api_key,
        model=settings.claude_model,
        max_tokens=settings.max_tokens,
        temperature=settings.temperature
    )

    session_manager = SessionManager(
        max_history=settings.max_conversation_history
    )

    rag_pipeline = RAGPipeline(
        vector_store_manager=vector_store,
        claude_client=claude_client,
        session_manager=session_manager,
        top_k_documents=settings.top_k_documents
    )

    print("✓ Components initialized\n")

    # Create session
    session_id = rag_pipeline.create_session()
    print(f"Session ID: {session_id}\n")

    # Test queries
    test_queries = [
        "How do I track my order?",
        "What is your return policy?",
        "Do you ship internationally?",
    ]

    print("Running test queries...\n")
    print("=" * 60)

    for query in test_queries:
        print(f"\n👤 User: {query}")
        print("-" * 60)

        result = rag_pipeline.process_query(
            query=query,
            session_id=session_id,
            stream=False
        )

        print(f"🤖 Bot: {result['response']}")

        if result['sources']:
            print(f"\n📚 Sources used:")
            for source in result['sources']:
                print(f"   - {source['category']} (relevance: {source['relevance_score']})")

        print("=" * 60)

    # Interactive mode
    print("\n\nEntering interactive mode (type 'quit' to exit)...\n")

    while True:
        try:
            user_input = input("👤 You: ").strip()

            if user_input.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break

            if not user_input:
                continue

            result = rag_pipeline.process_query(
                query=user_input,
                session_id=session_id,
                stream=False
            )

            print(f"🤖 Bot: {result['response']}\n")

        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {str(e)}\n")


if __name__ == "__main__":
    main()
