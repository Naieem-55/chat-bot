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
from ..feedback.feedback_manager import FeedbackManager
from ..feedback.hallucination_detector import HallucinationDetector
from ..suggestions.question_generator import QuestionGenerator, PeopleAlsoAsked
import uuid

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
feedback_manager: Optional[FeedbackManager] = None
hallucination_detector: Optional[HallucinationDetector] = None
question_generator: Optional[QuestionGenerator] = None
people_also_asked: Optional[PeopleAlsoAsked] = None


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
    message_id: str
    sources: List[Dict[str, Any]]
    context_used: bool
    hallucination_risk: Optional[Dict[str, Any]] = None


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
    global rag_pipeline, feedback_manager, hallucination_detector, question_generator, people_also_asked

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

        # Initialize feedback manager
        feedback_manager = FeedbackManager()

        # Initialize hallucination detector
        hallucination_detector = HallucinationDetector()

        # Initialize suggestions
        question_generator = QuestionGenerator()
        people_also_asked = PeopleAlsoAsked()

        logger.info("✓ RAG pipeline initialized successfully")
        logger.info("✓ Feedback system initialized")
        logger.info("✓ Question suggestions initialized")

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

        # Generate unique message ID
        message_id = str(uuid.uuid4())

        # Detect hallucinations
        is_hallucination, reasons, score = hallucination_detector.detect(
            response=result['response'],
            query=request.message,
            sources=result['sources'],
            context_used=result['context_used']
        )

        # Add hallucination risk to response
        hallucination_risk = {
            'detected': is_hallucination,
            'confidence_score': round(score, 3),
            'risk_level': hallucination_detector.get_confidence_label(score),
            'reasons': reasons
        } if score > 0.3 else None  # Only show if medium risk or higher

        return ChatResponse(
            message_id=message_id,
            hallucination_risk=hallucination_risk,
            **result
        )

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


# Feedback endpoints
class FeedbackRequest(BaseModel):
    """Feedback request model."""
    message_id: str
    session_id: str
    user_query: str
    bot_response: str
    feedback: str  # 'positive' or 'negative'
    sources: List[Dict[str, Any]]
    context_used: bool


@app.post("/feedback")
async def submit_feedback(request: FeedbackRequest):
    """
    Submit feedback for a chatbot response.

    Args:
        request: Feedback data

    Returns:
        Confirmation with feedback stats
    """
    if not feedback_manager or not hallucination_detector:
        raise HTTPException(status_code=503, detail="Feedback system not initialized")

    try:
        # Re-run hallucination detection
        is_hallucination, reasons, score = hallucination_detector.detect(
            response=request.bot_response,
            query=request.user_query,
            sources=request.sources,
            context_used=request.context_used
        )

        # Store feedback
        feedback_entry = feedback_manager.add_feedback(
            message_id=request.message_id,
            session_id=request.session_id,
            user_query=request.user_query,
            bot_response=request.bot_response,
            feedback=request.feedback,
            sources=request.sources,
            context_used=request.context_used,
            hallucination_detected=is_hallucination,
            hallucination_reasons=reasons
        )

        return {
            "message": "Feedback recorded successfully",
            "feedback_id": request.message_id,
            "stats": feedback_manager.get_stats()
        }

    except Exception as e:
        logger.error(f"Error recording feedback: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/feedback/stats")
async def get_feedback_stats():
    """Get feedback statistics."""
    if not feedback_manager:
        raise HTTPException(status_code=503, detail="Feedback system not initialized")

    return feedback_manager.get_stats()


@app.get("/feedback/problematic-queries")
async def get_problematic_queries(min_negative_rate: float = 0.5):
    """
    Get queries that frequently receive negative feedback.

    Args:
        min_negative_rate: Minimum negative feedback rate (0.0-1.0)

    Returns:
        List of problematic queries
    """
    if not feedback_manager:
        raise HTTPException(status_code=503, detail="Feedback system not initialized")

    return {
        "problematic_queries": feedback_manager.get_problematic_queries(min_negative_rate)
    }


@app.get("/feedback/hallucinations")
async def get_hallucinations():
    """Get all responses marked as potential hallucinations."""
    if not feedback_manager:
        raise HTTPException(status_code=503, detail="Feedback system not initialized")

    hallucinations = feedback_manager.get_hallucinations()

    return {
        "total_hallucinations": len(hallucinations),
        "hallucinations": [
            {
                "message_id": h.message_id,
                "user_query": h.user_query,
                "bot_response": h.bot_response[:200] + "..." if len(h.bot_response) > 200 else h.bot_response,
                "feedback": h.feedback,
                "reasons": h.hallucination_reasons,
                "timestamp": h.timestamp.isoformat()
            }
            for h in hallucinations[-50:]  # Last 50
        ]
    }


@app.get("/feedback/export")
async def export_feedback():
    """Export all feedback data."""
    if not feedback_manager:
        raise HTTPException(status_code=503, detail="Feedback system not initialized")

    try:
        export_path = feedback_manager.export_feedback()
        return {
            "message": "Feedback exported successfully",
            "export_path": export_path
        }
    except Exception as e:
        logger.error(f"Error exporting feedback: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Suggestions endpoints
class AutocompleteRequest(BaseModel):
    """Autocomplete request model."""
    partial_query: str


class FollowUpRequest(BaseModel):
    """Follow-up request model."""
    user_query: str
    bot_response: str
    sources: List[Dict[str, Any]]


@app.get("/suggestions/common-questions")
async def get_common_questions(max_questions: int = 10):
    """
    Get common suggested questions based on document content.

    Args:
        max_questions: Maximum number of questions to return

    Returns:
        List of suggested questions
    """
    if not question_generator or not rag_pipeline:
        raise HTTPException(status_code=503, detail="Service not initialized")

    try:
        # Get all documents for analysis
        all_docs = rag_pipeline.vector_store.get_all_documents()

        # Generate suggestions
        questions = question_generator.generate_from_documents(
            documents=all_docs,
            max_questions=max_questions
        )

        return {
            "questions": questions,
            "count": len(questions)
        }

    except Exception as e:
        logger.error(f"Error generating common questions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/suggestions/autocomplete")
async def autocomplete_query(request: AutocompleteRequest):
    """
    Get autocomplete suggestions for partial query.

    Args:
        request: Partial query text

    Returns:
        List of suggested completions
    """
    if not question_generator or not rag_pipeline:
        raise HTTPException(status_code=503, detail="Service not initialized")

    try:
        # Get all documents
        all_docs = rag_pipeline.vector_store.get_all_documents()

        # Generate autocomplete suggestions
        suggestions = question_generator.generate_autocomplete(
            partial_query=request.partial_query,
            documents=all_docs,
            max_suggestions=5
        )

        return {
            "suggestions": suggestions,
            "count": len(suggestions)
        }

    except Exception as e:
        logger.error(f"Error generating autocomplete: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/suggestions/follow-ups")
async def get_follow_up_suggestions(request: FollowUpRequest):
    """
    Get follow-up question suggestions based on conversation context.

    Args:
        request: User query, bot response, and sources

    Returns:
        List of follow-up questions
    """
    if not question_generator:
        raise HTTPException(status_code=503, detail="Service not initialized")

    try:
        # Generate follow-up questions
        follow_ups = question_generator.generate_follow_ups(
            user_query=request.user_query,
            bot_response=request.bot_response,
            context_docs=request.sources
        )

        return {
            "follow_ups": follow_ups,
            "count": len(follow_ups)
        }

    except Exception as e:
        logger.error(f"Error generating follow-ups: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/suggestions/people-also-asked")
async def get_people_also_asked(request: FollowUpRequest):
    """
    Get 'People Also Asked' suggestions based on query.

    Args:
        request: User query and bot response

    Returns:
        List of related questions
    """
    if not people_also_asked:
        raise HTTPException(status_code=503, detail="Service not initialized")

    try:
        # Generate PAA questions
        paa_questions = people_also_asked.generate(
            user_query=request.user_query,
            response=request.bot_response,
            max_questions=4
        )

        return {
            "questions": paa_questions,
            "count": len(paa_questions)
        }

    except Exception as e:
        logger.error(f"Error generating PAA: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True
    )
