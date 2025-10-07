"""FastAPI application for the chatbot."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import logging

from ..config import settings
from ..vector_store.vector_store_manager import VectorStoreManager
from ..llm.claude_client import ClaudeClient
from ..llm.huggingface_client import HuggingFaceClient
from ..session.session_manager import SessionManager
from ..rag_pipeline import RAGPipeline

# Setup logging
logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="RAG Customer Support Chatbot API",
    description="API for RAG-powered customer support chatbot",
    version="1.0.0"
)

# CORS middleware - Allow all origins for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins including file://
    allow_credentials=False,  # Must be False when allow_origins is "*"
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances (initialized on startup)
rag_pipeline: Optional[RAGPipeline] = None


# Pydantic models
class ChatRequest(BaseModel):
    """Chat request model."""
    message: str
    session_id: Optional[str] = None
    stream: bool = False


class ChatResponse(BaseModel):
    """Chat response model."""
    response: str
    session_id: str
    sources: List[Dict[str, Any]]
    context_used: bool


class SessionCreateResponse(BaseModel):
    """Session creation response."""
    session_id: str


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    vector_store_stats: Dict[str, Any]


@app.on_event("startup")
async def startup_event():
    """Initialize components on startup."""
    global rag_pipeline

    logger.info("Initializing RAG pipeline...")

    try:
        # Initialize vector store
        vector_store = VectorStoreManager(
            embedding_model=settings.embedding_model,
            vector_db_type=settings.vector_db_type,
            vector_db_path=settings.vector_db_path
        )

        # Initialize LLM client based on provider
        if settings.llm_provider == "huggingface":
            api_key = settings.huggingface_api_key if settings.huggingface_api_key else None
            llm_client = HuggingFaceClient(
                model=settings.huggingface_model,
                max_tokens=settings.max_tokens,
                temperature=settings.temperature,
                api_key=api_key
            )
            logger.info(f"Using Hugging Face model: {settings.huggingface_model}")
            logger.info(f"API key configured: {'Yes' if api_key else 'No'}")
        else:
            llm_client = ClaudeClient(
                api_key=settings.anthropic_api_key,
                model=settings.claude_model,
                max_tokens=settings.max_tokens,
                temperature=settings.temperature
            )
            logger.info(f"Using Claude model: {settings.claude_model}")

        # Initialize session manager
        session_manager = SessionManager(
            max_history=settings.max_conversation_history
        )

        # Initialize RAG pipeline
        rag_pipeline = RAGPipeline(
            vector_store_manager=vector_store,
            claude_client=llm_client,
            session_manager=session_manager,
            top_k_documents=settings.top_k_documents
        )

        logger.info("✓ RAG pipeline initialized successfully")

    except Exception as e:
        logger.error(f"Failed to initialize RAG pipeline: {str(e)}")
        raise


@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint."""
    return {
        "message": "RAG Customer Support Chatbot API",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    if not rag_pipeline:
        raise HTTPException(status_code=503, detail="Service not initialized")

    stats = rag_pipeline.vector_store.get_stats()

    return {
        "status": "healthy",
        "vector_store_stats": stats
    }


@app.post("/session/create", response_model=SessionCreateResponse)
async def create_session():
    """Create a new conversation session."""
    if not rag_pipeline:
        raise HTTPException(status_code=503, detail="Service not initialized")

    session_id = rag_pipeline.create_session()
    return {"session_id": session_id}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Process chat message.

    Args:
        request: Chat request with message and optional session_id

    Returns:
        Chat response with answer and sources
    """
    if not rag_pipeline:
        raise HTTPException(status_code=503, detail="Service not initialized")

    try:
        # Create session if not provided
        session_id = request.session_id
        if not session_id:
            session_id = rag_pipeline.create_session()

        # Process query
        if request.stream:
            # For streaming, we'd need to use StreamingResponse
            raise HTTPException(
                status_code=501,
                detail="Streaming not implemented in this endpoint. Use /chat/stream"
            )

        result = rag_pipeline.process_query(
            query=request.message,
            session_id=session_id,
            stream=False
        )

        return ChatResponse(**result)

    except Exception as e:
        import traceback
        logger.error(f"Error processing chat request: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/session/{session_id}/history")
async def get_session_history(session_id: str):
    """Get conversation history for a session."""
    if not rag_pipeline:
        raise HTTPException(status_code=503, detail="Service not initialized")

    history = rag_pipeline.get_session_history(session_id)

    if history is None:
        raise HTTPException(status_code=404, detail="Session not found")

    return {"session_id": session_id, "history": history}


@app.delete("/session/{session_id}")
async def delete_session(session_id: str):
    """Delete a session and its history."""
    if not rag_pipeline:
        raise HTTPException(status_code=503, detail="Service not initialized")

    success = rag_pipeline.clear_session(session_id)

    if not success:
        raise HTTPException(status_code=404, detail="Session not found")

    return {"message": "Session deleted successfully"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True
    )
