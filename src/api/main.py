"""FastAPI application for the chatbot."""

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import logging
import tempfile
import os
from pathlib import Path

from ..config import settings
from ..vector_store.vector_store_manager import VectorStoreManager
from ..llm.claude_client import ClaudeClient
from ..llm.huggingface_client import HuggingFaceClient
from ..session.session_manager import SessionManager
from ..rag_pipeline import RAGPipeline
from ..feedback.feedback_manager import FeedbackManager
from ..feedback.hallucination_detector import HallucinationDetector
from ..suggestions.question_generator import QuestionGenerator, PeopleAlsoAsked
from ..data_ingestion.document_loader import DocumentLoader
from ..data_ingestion.text_processor import TextProcessor
from ..notifications.email_notifier import EmailNotifier
from ..notifications.webhook_manager import WebhookManager
import uuid
from datetime import datetime

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
email_notifier: Optional[Any] = None
webhook_manager: Optional[Any] = None


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
    reformulated_query: Optional[str] = None
    memory_used: Optional[bool] = None
    memory_stats: Optional[Dict[str, int]] = None


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
    global rag_pipeline, feedback_manager, hallucination_detector, question_generator, people_also_asked, email_notifier, webhook_manager

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

        # Initialize notifications
        webhook_manager = WebhookManager()
        email_notifier = EmailNotifier(enabled=False)  # Disabled by default, configured via API

        logger.info("✓ RAG pipeline initialized successfully")
        logger.info("✓ Feedback system initialized")
        logger.info("✓ Question suggestions initialized")
        logger.info("✓ Webhook notification system initialized")

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

    # Send email notifications for session_created event
    if webhook_manager and email_notifier:
        try:
            webhooks = webhook_manager.get_webhooks_for_event("session_created")
            for webhook in webhooks:
                email_notifier.send_email(
                    to_email=webhook['email'],
                    subject="🆕 New Chat Session Created",
                    body=f"A new chat session has been created.\n\nSession ID: {session_id}\nTimestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                )
        except Exception as notif_error:
            logger.warning(f"Failed to send session_created notification: {notif_error}")

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

        # Send email notifications for new_message event
        if webhook_manager and email_notifier:
            try:
                webhooks = webhook_manager.get_webhooks_for_event("new_message")
                for webhook in webhooks:
                    email_notifier.notify_new_message(
                        to_email=webhook['email'],
                        session_id=session_id,
                        user_message=request.message,
                        bot_response=result['response']
                    )
            except Exception as notif_error:
                logger.warning(f"Failed to send email notification: {notif_error}")

        return ChatResponse(
            message_id=message_id,
            hallucination_risk=hallucination_risk,
            **result
        )

    except Exception as e:
        import traceback
        error_details = str(e)
        logger.error(f"Error processing chat request: {error_details}")
        logger.error(f"Traceback: {traceback.format_exc()}")

        # Send error notifications
        if webhook_manager and email_notifier:
            try:
                webhooks = webhook_manager.get_webhooks_for_event("error")
                for webhook in webhooks:
                    email_notifier.notify_error(
                        to_email=webhook['email'],
                        error_type="Chat Processing Error",
                        error_message=error_details,
                        session_id=request.session_id
                    )
            except Exception as notif_error:
                logger.warning(f"Failed to send error notification: {notif_error}")

        raise HTTPException(status_code=500, detail=error_details)


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

    # Send email notifications for session_deleted event
    if webhook_manager and email_notifier:
        try:
            webhooks = webhook_manager.get_webhooks_for_event("session_deleted")
            for webhook in webhooks:
                email_notifier.send_email(
                    to_email=webhook['email'],
                    subject="🗑️ Chat Session Deleted",
                    body=f"A chat session has been deleted.\n\nSession ID: {session_id}\nTimestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                )
        except Exception as notif_error:
            logger.warning(f"Failed to send session_deleted notification: {notif_error}")

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

        # Send email notifications for feedback event
        if webhook_manager and email_notifier:
            try:
                webhooks = webhook_manager.get_webhooks_for_event("feedback")
                for webhook in webhooks:
                    email_notifier.notify_feedback(
                        to_email=webhook['email'],
                        session_id=request.session_id,
                        message_id=request.message_id,
                        feedback_type=request.feedback,
                        query=request.user_query
                    )
            except Exception as notif_error:
                logger.warning(f"Failed to send feedback notification: {notif_error}")

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


# Document Management endpoints
@app.get("/documents/list")
async def list_documents():
    """
    Get list of all documents in the vector store.

    Returns:
        List of documents with metadata
    """
    if not rag_pipeline:
        raise HTTPException(status_code=503, detail="Service not initialized")

    try:
        documents = rag_pipeline.vector_store.get_all_documents()

        # Format response
        formatted_docs = []
        for doc in documents:
            metadata = doc.get('metadata', {})
            formatted_docs.append({
                'id': doc['id'],
                'filename': metadata.get('filename', metadata.get('title', 'Unknown')),
                'source': metadata.get('source', 'Unknown'),
                'type': metadata.get('type', Path(metadata.get('source', '')).suffix.lstrip('.')),
                'category': metadata.get('category', 'General'),
                'content_preview': doc['content'][:200] + '...' if len(doc['content']) > 200 else doc['content'],
                'content_length': len(doc['content'])
            })

        return {
            "total": len(formatted_docs),
            "documents": formatted_docs
        }

    except Exception as e:
        logger.error(f"Error listing documents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/documents/upload")
async def upload_document(file: UploadFile = File(...)):
    """
    Upload and index a document.

    Args:
        file: Document file to upload

    Returns:
        Upload status and document info
    """
    if not rag_pipeline:
        raise HTTPException(status_code=503, detail="Service not initialized")

    try:
        # Check file extension
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in DocumentLoader.SUPPORTED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {file_ext}. Supported: {list(DocumentLoader.SUPPORTED_EXTENSIONS.keys())}"
            )

        # Save uploaded file to temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name

        try:
            # Load document
            logger.info(f"Loading document: {file.filename}")
            documents = DocumentLoader.load_document(tmp_file_path)

            # Process documents (chunk)
            text_processor = TextProcessor(
                chunk_size=settings.chunk_size,
                chunk_overlap=settings.chunk_overlap
            )
            processed_docs = text_processor.process_pipeline(documents)

            # Index into vector store
            rag_pipeline.vector_store.index_documents(processed_docs)
            rag_pipeline.vector_store.save()

            # Reinitialize BM25 if enabled
            if hasattr(rag_pipeline, 'bm25_retriever') and rag_pipeline.bm25_retriever:
                from ..retrieval.bm25_retriever import BM25Retriever
                all_docs = rag_pipeline.vector_store.get_all_documents()
                rag_pipeline.bm25_retriever = BM25Retriever(all_docs, top_k=settings.top_k_documents)
                logger.info("✓ Reinitialized BM25 retriever")

            return {
                "message": "Document uploaded and indexed successfully",
                "filename": file.filename,
                "chunks_created": len(processed_docs),
                "total_documents": len(rag_pipeline.vector_store.get_all_documents())
            }

        finally:
            # Clean up temporary file
            os.unlink(tmp_file_path)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/documents/{doc_id}")
async def delete_document(doc_id: int):
    """
    Delete a document from the vector store.

    Args:
        doc_id: ID of the document to delete

    Returns:
        Deletion status
    """
    if not rag_pipeline:
        raise HTTPException(status_code=503, detail="Service not initialized")

    try:
        success = rag_pipeline.vector_store.delete_document(doc_id)

        if not success:
            raise HTTPException(status_code=404, detail=f"Document {doc_id} not found")

        # Reinitialize BM25 if enabled
        if hasattr(rag_pipeline, 'bm25_retriever') and rag_pipeline.bm25_retriever:
            from ..retrieval.bm25_retriever import BM25Retriever
            all_docs = rag_pipeline.vector_store.get_all_documents()
            if all_docs:
                rag_pipeline.bm25_retriever = BM25Retriever(all_docs, top_k=settings.top_k_documents)
            else:
                rag_pipeline.bm25_retriever = None
            logger.info("✓ Reinitialized BM25 retriever")

        return {
            "message": "Document deleted successfully",
            "doc_id": doc_id,
            "remaining_documents": len(rag_pipeline.vector_store.get_all_documents())
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/documents/clear")
async def clear_all_documents():
    """
    Clear all documents from the vector store.

    Returns:
        Confirmation message
    """
    if not rag_pipeline:
        raise HTTPException(status_code=503, detail="Service not initialized")

    try:
        rag_pipeline.vector_store.clear_all_documents()

        # Clear BM25
        if hasattr(rag_pipeline, 'bm25_retriever'):
            rag_pipeline.bm25_retriever = None

        return {
            "message": "All documents cleared successfully",
            "remaining_documents": 0
        }

    except Exception as e:
        logger.error(f"Error clearing documents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/documents/upload-url")
async def upload_from_url(url: str):
    """
    Ingest content from a URL.

    Args:
        url: Website URL to scrape and index

    Returns:
        Upload status
    """
    if not rag_pipeline:
        raise HTTPException(status_code=503, detail="Service not initialized")

    try:
        # Load from URL
        logger.info(f"Loading content from URL: {url}")
        documents = DocumentLoader.load_from_url(url)

        if not documents:
            raise HTTPException(status_code=400, detail="No content extracted from URL")

        # Process documents
        text_processor = TextProcessor(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap
        )
        processed_docs = text_processor.process_pipeline(documents)

        # Index into vector store
        rag_pipeline.vector_store.index_documents(processed_docs)
        rag_pipeline.vector_store.save()

        # Reinitialize BM25 if enabled
        if hasattr(rag_pipeline, 'bm25_retriever') and rag_pipeline.bm25_retriever:
            from ..retrieval.bm25_retriever import BM25Retriever
            all_docs = rag_pipeline.vector_store.get_all_documents()
            rag_pipeline.bm25_retriever = BM25Retriever(all_docs, top_k=settings.top_k_documents)
            logger.info("✓ Reinitialized BM25 retriever")

        return {
            "message": "URL content indexed successfully",
            "url": url,
            "chunks_created": len(processed_docs),
            "total_documents": len(rag_pipeline.vector_store.get_all_documents())
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading from URL: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Memory Management endpoints
@app.get("/memory/{session_id}/facts")
async def get_user_facts(session_id: str, category: Optional[str] = None):
    """
    Get facts stored about the user.

    Args:
        session_id: User session ID
        category: Optional category filter

    Returns:
        List of user facts
    """
    if not rag_pipeline or not rag_pipeline.memory_manager:
        raise HTTPException(status_code=503, detail="Memory service not initialized")

    try:
        facts = rag_pipeline.memory_manager.get_user_facts(session_id, category)
        return {
            "session_id": session_id,
            "facts": facts,
            "count": len(facts)
        }
    except Exception as e:
        logger.error(f"Error retrieving user facts: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/memory/{session_id}/preferences")
async def get_user_preferences(session_id: str):
    """Get all user preferences."""
    if not rag_pipeline or not rag_pipeline.memory_manager:
        raise HTTPException(status_code=503, detail="Memory service not initialized")

    try:
        preferences = rag_pipeline.memory_manager.get_all_preferences(session_id)
        return {
            "session_id": session_id,
            "preferences": preferences,
            "count": len(preferences)
        }
    except Exception as e:
        logger.error(f"Error retrieving preferences: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


class PreferenceRequest(BaseModel):
    """Preference storage request."""
    key: str
    value: Any


@app.post("/memory/{session_id}/preference")
async def store_user_preference(session_id: str, request: PreferenceRequest):
    """Store a user preference."""
    if not rag_pipeline or not rag_pipeline.memory_manager:
        raise HTTPException(status_code=503, detail="Memory service not initialized")

    try:
        rag_pipeline.memory_manager.store_preference(
            session_id,
            request.key,
            request.value
        )
        return {
            "message": "Preference stored successfully",
            "session_id": session_id,
            "key": request.key
        }
    except Exception as e:
        logger.error(f"Error storing preference: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/memory/{session_id}/summaries")
async def get_conversation_summaries(session_id: str, limit: int = 10):
    """Get conversation summaries for a user."""
    if not rag_pipeline or not rag_pipeline.memory_manager:
        raise HTTPException(status_code=503, detail="Memory service not initialized")

    try:
        summaries = rag_pipeline.memory_manager.get_conversation_summaries(session_id, limit)
        return {
            "session_id": session_id,
            "summaries": summaries,
            "count": len(summaries)
        }
    except Exception as e:
        logger.error(f"Error retrieving summaries: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/memory/{session_id}/stats")
async def get_memory_stats(session_id: str):
    """Get memory statistics for a user."""
    if not rag_pipeline or not rag_pipeline.memory_manager:
        raise HTTPException(status_code=503, detail="Memory service not initialized")

    try:
        stats = rag_pipeline.memory_manager.get_memory_stats(session_id)
        return {
            "session_id": session_id,
            "stats": stats
        }
    except Exception as e:
        logger.error(f"Error retrieving memory stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/memory/{session_id}")
async def clear_user_memory(session_id: str):
    """Clear all memory for a specific user."""
    if not rag_pipeline or not rag_pipeline.memory_manager:
        raise HTTPException(status_code=503, detail="Memory service not initialized")

    try:
        rag_pipeline.memory_manager.clear_user_memory(session_id)
        return {
            "message": "User memory cleared successfully",
            "session_id": session_id
        }
    except Exception as e:
        logger.error(f"Error clearing user memory: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True
    )


@app.get("/sessions/list")
async def list_sessions():
    """List all conversation sessions with metadata."""
    if not rag_pipeline:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    sessions = rag_pipeline.session_manager.list_sessions()
    return {"sessions": sessions, "count": len(sessions)}


class UpdateTitleRequest(BaseModel):
    """Update session title request."""
    title: str


@app.put("/session/{session_id}/title")
async def update_session_title(session_id: str, request: UpdateTitleRequest):
    """Update the title of a session."""
    if not rag_pipeline:
        raise HTTPException(status_code=503, detail="Service not initialized")

    success = rag_pipeline.session_manager.update_session_title(session_id, request.title)

    if not success:
        raise HTTPException(status_code=404, detail="Session not found")

    return {"message": "Title updated successfully", "session_id": session_id, "title": request.title}


@app.put("/session/{session_id}/pin")
async def toggle_pin_session(session_id: str):
    """Toggle pin status of a session."""
    if not rag_pipeline:
        raise HTTPException(status_code=503, detail="Service not initialized")

    pinned_status = rag_pipeline.session_manager.toggle_pin_session(session_id)

    if pinned_status is None:
        raise HTTPException(status_code=404, detail="Session not found")

    return {
        "message": "Pin status updated successfully",
        "session_id": session_id,
        "pinned": pinned_status
    }


# Webhook/Notification endpoints
class EmailConfigRequest(BaseModel):
    """Email configuration request."""
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: str
    smtp_password: str
    from_email: Optional[str] = None


class WebhookRequest(BaseModel):
    """Webhook creation/update request."""
    webhook_id: str
    email: str
    events: List[str]
    enabled: bool = True


@app.post("/webhooks/email/configure")
async def configure_email_notifications(request: EmailConfigRequest):
    """
    Configure email notification settings.

    Args:
        request: Email configuration (SMTP settings)

    Returns:
        Configuration status
    """
    if not email_notifier:
        raise HTTPException(status_code=503, detail="Email notifier not initialized")

    try:
        # Update email notifier configuration
        email_notifier.smtp_server = request.smtp_server
        email_notifier.smtp_port = request.smtp_port
        email_notifier.smtp_username = request.smtp_username
        email_notifier.smtp_password = request.smtp_password
        email_notifier.from_email = request.from_email or request.smtp_username
        email_notifier.enabled = True

        logger.info("✓ Email notifications configured")

        return {
            "message": "Email notifications configured successfully",
            "smtp_server": request.smtp_server,
            "smtp_port": request.smtp_port,
            "from_email": email_notifier.from_email,
            "enabled": True
        }

    except Exception as e:
        logger.error(f"Error configuring email: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/webhooks/email/test")
async def test_email_notification(to_email: str):
    """
    Test email configuration by sending a test email.

    Args:
        to_email: Email address to send test to

    Returns:
        Test result
    """
    if not email_notifier:
        raise HTTPException(status_code=503, detail="Email notifier not initialized")

    try:
        result = email_notifier.test_connection(to_email)
        return result
    except Exception as e:
        logger.error(f"Error testing email: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/webhooks/create")
async def create_webhook(request: WebhookRequest):
    """
    Create or update a webhook subscription.

    Args:
        request: Webhook configuration

    Returns:
        Created webhook configuration
    """
    if not webhook_manager:
        raise HTTPException(status_code=503, detail="Webhook manager not initialized")

    try:
        webhook = webhook_manager.add_email_webhook(
            webhook_id=request.webhook_id,
            email=request.email,
            events=request.events,
            enabled=request.enabled
        )

        return {
            "message": "Webhook created successfully",
            "webhook": webhook
        }

    except Exception as e:
        logger.error(f"Error creating webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/webhooks/list")
async def list_webhooks():
    """
    List all configured webhooks.

    Returns:
        List of webhooks
    """
    if not webhook_manager:
        raise HTTPException(status_code=503, detail="Webhook manager not initialized")

    try:
        webhooks = webhook_manager.list_webhooks()
        stats = webhook_manager.get_stats()

        return {
            "webhooks": webhooks,
            "stats": stats
        }

    except Exception as e:
        logger.error(f"Error listing webhooks: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/webhooks/{webhook_id}")
async def get_webhook(webhook_id: str):
    """
    Get webhook configuration by ID.

    Args:
        webhook_id: Webhook identifier

    Returns:
        Webhook configuration
    """
    if not webhook_manager:
        raise HTTPException(status_code=503, detail="Webhook manager not initialized")

    try:
        webhook = webhook_manager.get_webhook(webhook_id)

        if not webhook:
            raise HTTPException(status_code=404, detail="Webhook not found")

        return webhook

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/webhooks/{webhook_id}")
async def delete_webhook(webhook_id: str):
    """
    Delete a webhook.

    Args:
        webhook_id: Webhook identifier

    Returns:
        Deletion status
    """
    if not webhook_manager:
        raise HTTPException(status_code=503, detail="Webhook manager not initialized")

    try:
        success = webhook_manager.remove_webhook(webhook_id)

        if not success:
            raise HTTPException(status_code=404, detail="Webhook not found")

        return {
            "message": "Webhook deleted successfully",
            "webhook_id": webhook_id
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/webhooks/{webhook_id}/enable")
async def enable_webhook(webhook_id: str):
    """
    Enable a webhook.

    Args:
        webhook_id: Webhook identifier

    Returns:
        Updated status
    """
    if not webhook_manager:
        raise HTTPException(status_code=503, detail="Webhook manager not initialized")

    try:
        success = webhook_manager.enable_webhook(webhook_id)

        if not success:
            raise HTTPException(status_code=404, detail="Webhook not found")

        return {
            "message": "Webhook enabled successfully",
            "webhook_id": webhook_id,
            "enabled": True
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error enabling webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/webhooks/{webhook_id}/disable")
async def disable_webhook(webhook_id: str):
    """
    Disable a webhook.

    Args:
        webhook_id: Webhook identifier

    Returns:
        Updated status
    """
    if not webhook_manager:
        raise HTTPException(status_code=503, detail="Webhook manager not initialized")

    try:
        success = webhook_manager.disable_webhook(webhook_id)

        if not success:
            raise HTTPException(status_code=404, detail="Webhook not found")

        return {
            "message": "Webhook disabled successfully",
            "webhook_id": webhook_id,
            "enabled": False
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error disabling webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/webhooks/events/available")
async def get_available_events():
    """
    Get list of available events that can be subscribed to.

    Returns:
        List of available events
    """
    if not webhook_manager:
        raise HTTPException(status_code=503, detail="Webhook manager not initialized")

    try:
        events = webhook_manager.get_available_events()
        return {
            "events": events,
            "count": len(events)
        }

    except Exception as e:
        logger.error(f"Error getting available events: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
