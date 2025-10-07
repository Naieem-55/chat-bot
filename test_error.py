"""Test to find the exact error."""
import sys
import traceback

# Add src to path
sys.path.insert(0, 'C:/projects/chatbot')

try:
    from src.config import settings
    from src.vector_store.vector_store_manager import VectorStoreManager
    from src.llm.huggingface_client import HuggingFaceClient
    from src.session.session_manager import SessionManager
    from src.rag_pipeline import RAGPipeline

    print("1. Initializing vector store...")
    vector_store = VectorStoreManager(
        embedding_model=settings.embedding_model,
        vector_db_type=settings.vector_db_type,
        vector_db_path=settings.vector_db_path
    )
    print("✓ Vector store initialized")

    print("\n2. Initializing LLM client...")
    llm_client = HuggingFaceClient(
        model=settings.huggingface_model,
        max_tokens=settings.max_tokens,
        temperature=settings.temperature,
        api_key=settings.huggingface_api_key
    )
    print(f"✓ LLM client initialized: {settings.huggingface_model}")

    print("\n3. Initializing session manager...")
    session_manager = SessionManager(
        max_history=settings.max_conversation_history
    )
    print("✓ Session manager initialized")

    print("\n4. Initializing RAG pipeline...")
    rag_pipeline = RAGPipeline(
        vector_store_manager=vector_store,
        claude_client=llm_client,
        session_manager=session_manager,
        top_k_documents=settings.top_k_documents
    )
    print("✓ RAG pipeline initialized")

    print("\n5. Creating session...")
    session_id = rag_pipeline.create_session()
    print(f"✓ Session created: {session_id}")

    print("\n6. Processing test query...")
    result = rag_pipeline.process_query(
        query="What is your return policy?",
        session_id=session_id,
        stream=False
    )
    print("✓ Query processed successfully!")
    print(f"\nResponse: {result['response'][:200]}...")

except Exception as e:
    print(f"\n❌ ERROR: {e}")
    print(f"\nFull traceback:")
    traceback.print_exc()
