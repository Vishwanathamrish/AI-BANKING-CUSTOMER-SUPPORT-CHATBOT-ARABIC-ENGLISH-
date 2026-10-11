"""
FastAPI Main Application - AI Customer Support Chatbot API

This is the main entry point for the backend API server.
"""

import os
import logging
from typing import List, Optional, Dict
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from .embeddings import EmbeddingService
from .vector_store import VectorStoreManager
from .rag_pipeline import RAGPipeline
from .language_detection import LanguageDetector
from .memory import ConversationMemoryManager
from .intent_detection import IntentDetector, BankingIntent, get_intent_detector
from .analytics import ConversationAnalytics, get_analytics_tracker

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI Customer Support Chatbot API",
    description="Bilingual (Arabic + English) AI chatbot using RAG",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global services
embeddings_service = None
vector_store_manager = None
rag_pipeline = None
memory_manager = None
intent_detector = None
analytics_tracker = None


def initialize_services():
    """Initialize all backend services."""
    global embeddings_service, vector_store_manager, rag_pipeline, memory_manager, intent_detector, analytics_tracker
    
    try:
        logger.info("Initializing backend services...")
        
        # Initialize embedding service
        embeddings_service = EmbeddingService(
            model_name="all-MiniLM-L6-v2",
            chunk_size=16
        )
        
        # Initialize vector store manager
        vector_db_path = os.getenv("VECTOR_DB_PATH", "./vector_db")
        vector_store_manager = VectorStoreManager(
            embeddings_service=embeddings_service,
            vector_db_path=vector_db_path
        )
        
        # Initialize RAG pipeline
        rag_pipeline = RAGPipeline(
            embeddings_service=embeddings_service,
            vector_store_manager=vector_store_manager,
            model_name=os.getenv("LLM_MODEL", "openai/gpt-oss-20b"),
            chunk_size=int(os.getenv("CHUNK_SIZE", "1000")),
            chunk_overlap=int(os.getenv("CHUNK_OVERLAP", "200")),
            similarity_threshold=float(os.getenv("SIMILARITY_THRESHOLD", "0.5"))
        )
        
        # Initialize conversation memory
        memory_manager = ConversationMemoryManager(max_history_length=10)
        
        # Initialize intent detector
        intent_detector = get_intent_detector()
        
        # Initialize analytics tracker
        analytics_tracker = get_analytics_tracker()
        
        # Try to load existing vector index
        if vector_store_manager.index_exists():
            if vector_store_manager.load_index():
                logger.info("Loaded existing vector index")
            else:
                logger.error("Vector index exists but could not be loaded")
        else:
            logger.warning("No vector index found. Please initialize with documents.")
        
        logger.info("All services initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        raise


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str = Field(..., description="User's message")
    conversation_id: Optional[str] = Field(None, description="Conversation session ID")


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    answer: str
    language: str
    confidence: float
    conversation_id: str
    fallback: bool = False
    response_type: str = "text"  # text | loan | account | card | balance
    data: Optional[Dict] = None  # Structured data for UI rendering


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    initialize_services()


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "AI Customer Support Chatbot",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Detailed health check."""
    return {
        "status": "ok",
        "services": {
            "embeddings": embeddings_service is not None,
            "vector_store": vector_store_manager is not None,
            "rag_pipeline": rag_pipeline is not None,
            "memory": memory_manager is not None
        }
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint for customer support.
    
    Args:
        request: ChatRequest with message and optional conversation_id
        
    Returns:
        ChatResponse with answer, language, and metadata
    """
    import time
    import traceback
    start_time = time.time()
    
    try:
        # Validate input
        if not request.message or not request.message.strip():
            logger.warning("Empty message received")
            return ChatResponse(
                answer="I'm here to help! Please ask me a question about our banking services.",
                language="English",
                confidence=1.0,
                conversation_id=request.conversation_id or "unknown",
                fallback=True
            )
        
        # Detect user language
        detected_language = LanguageDetector.detect(request.message)
        language_name = LanguageDetector.get_language_name(detected_language)
        
        logger.info(f"Detected language: {language_name} ({detected_language})")
        
        # Get or create conversation
        conversation_id = request.conversation_id
        if not conversation_id:
            conversation_id = memory_manager.create_conversation()
        
        # Get conversation history
        chat_history = memory_manager.get_history(conversation_id)
        
        # Generate response using RAG
        result = rag_pipeline.generate_response(
            query=request.message,
            chat_history=chat_history,
            language=language_name
        )
        
        # Extract response
        answer = result.get("answer", "")
        confidence = result.get("confidence", 0.0)
        is_fallback = result.get("fallback", False)
        intent = result.get("intent", "unknown")
        response_time_ms = result.get("response_time_ms", 0.0)
        response_type = result.get("response_type", "text")
        data = result.get("data")
        
        # CRITICAL FIX: Log what we got from RAG pipeline
        logger.info(f"📊 Got response from RAG: {len(answer)} chars, fallback={is_fallback}, confidence={confidence:.2f}")
        
        # Validate response - but DON'T replace with generic fallback!
        if not answer or not answer.strip():
            logger.error(f"❌ EMPTY response from RAG for query: {request.message[:50]}")
            # Instead of generic fallback, log error and return domain-appropriate message
            if language_name.lower() == "arabic":
                answer = "عذراً، حدث خطأ في معالجة طلبك. يرجى المحاولة مرة أخرى أو الاتصال بخدمة العملاء."
            else:
                answer = "I apologize, but there was an error processing your request. Please try again or contact customer service."
            is_fallback = True
            confidence = 0.0
            logger.error(f"✅ Set error message instead of generic fallback")
        
        # Check if answer contains fallback phrases (indicates LLM failure)
        fallback_phrases = ["i apologize", "trouble finding", "rephrase", "cannot find"]
        if any(phrase in answer.lower() for phrase in fallback_phrases):
            logger.warning(f"⚠️ Response contains fallback phrases - may need regeneration")
        
        # Store in memory
        memory_manager.add_message(
            conversation_id=conversation_id,
            user_message=request.message,
            ai_response=answer
        )
        
        # Track analytics
        if analytics_tracker:
            analytics_tracker.track_conversation(
                question=request.message,
                answer=answer,
                language=language_name,
                intent=intent,
                confidence=confidence,
                response_time_ms=response_time_ms,
                is_fallback=is_fallback,
                user_id=conversation_id
            )
        
        total_time = (time.time() - start_time) * 1000
        logger.info(f"Generated response (confidence: {confidence:.3f}, fallback: {is_fallback}, intent: {intent}, time: {total_time:.1f}ms)")
        
        return ChatResponse(
            answer=answer,
            language=language_name,
            confidence=confidence,
            conversation_id=conversation_id,
            fallback=is_fallback,
            response_type=response_type,
            data=data
        )
        
    except Exception as e:
        # Log full error details
        error_traceback = traceback.format_exc()
        logger.error(f"Error processing chat: {e}\n{error_traceback}")
        
        # Return safe fallback response instead of crashing
        safe_response = (
            "I apologize, but I'm experiencing technical difficulties at the moment. "
            "Please try again in a few moments, or contact our support team for immediate assistance."
        )
        
        return ChatResponse(
            answer=safe_response,
            language="English",
            confidence=0.0,
            conversation_id=request.conversation_id or "error-session",
            fallback=True
        )


@app.post("/chat/reset/{conversation_id}")
async def reset_conversation(conversation_id: str):
    """
    Reset conversation history.
    
    Args:
        conversation_id: ID of conversation to reset
    """
    success = memory_manager.clear_conversation(conversation_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return {"status": "success", "message": "Conversation reset"}


@app.delete("/chat/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """
    Delete a conversation entirely.
    
    Args:
        conversation_id: ID of conversation to delete
    """
    success = memory_manager.delete_conversation(conversation_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return {"status": "success", "message": "Conversation deleted"}


@app.get("/conversations/count")
async def get_conversation_count():
    """Get number of active conversations."""
    return {"count": memory_manager.get_conversation_count()}


@app.get("/analytics/summary")
async def get_analytics_summary():
    """Get analytics summary statistics."""
    if not analytics_tracker:
        raise HTTPException(status_code=503, detail="Analytics not initialized")
    
    return analytics_tracker.get_summary_statistics()


@app.get("/analytics/questions/top")
async def get_top_questions(limit: int = 10):
    """Get most asked questions."""
    if not analytics_tracker:
        raise HTTPException(status_code=503, detail="Analytics not initialized")
    
    return {"questions": analytics_tracker.get_most_asked_questions(limit)}


@app.get("/analytics/intents")
async def get_intent_distribution():
    """Get intent distribution."""
    if not analytics_tracker:
        raise HTTPException(status_code=503, detail="Analytics not initialized")
    
    return {"intents": analytics_tracker.get_intent_distribution()}


@app.get("/analytics/languages")
async def get_language_distribution():
    """Get language distribution."""
    if not analytics_tracker:
        raise HTTPException(status_code=503, detail="Analytics not initialized")
    
    return {"languages": analytics_tracker.get_language_distribution()}


@app.get("/analytics/failed")
async def get_failed_queries(limit: int = 20):
    """Get recent failed queries."""
    if not analytics_tracker:
        raise HTTPException(status_code=503, detail="Analytics not initialized")
    
    return {"failed_queries": analytics_tracker.get_failed_queries(limit)}


@app.post("/intent/detect")
async def detect_intent(message: str):
    """
    Detect intent from message.
    
    Args:
        message: User message to analyze
        
    Returns:
        Detected intent with confidence score
    """
    if not intent_detector:
        raise HTTPException(status_code=503, detail="Intent detector not initialized")
    
    intent, confidence, keywords = intent_detector.detect_intent(message)
    
    return {
        "intent": intent.value,
        "intent_description": intent_detector.get_intent_description(intent),
        "confidence": confidence,
        "matched_keywords": keywords,
        "needs_escalation": intent_detector.needs_escalation(message)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
