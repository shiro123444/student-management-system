"""
Chat endpoint for educational QA
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import List, Optional
import logging
import uuid
from datetime import datetime

from app.schemas.chat import ChatRequest, ChatResponse, ChatMessage
from app.rag.pipeline import RAGPipeline
from app.services.progress_service import ProgressService
from app.utils.security import anonymize_query

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize services
rag_pipeline = RAGPipeline()
progress_service = ProgressService()

@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    background_tasks: BackgroundTasks
):
    """
    Process educational questions using RAG pipeline
    """
    try:
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        
        # Anonymize query for privacy
        anonymized_query = anonymize_query(request.query)
        
        logger.info(f"Processing chat request - Session: {session_id}")
        
        # Track progress
        progress_id = await progress_service.start_task(
            task_type="chat",
            session_id=session_id
        )
        
        # Process through RAG pipeline
        rag_result = await rag_pipeline.process_query(
            query=request.query,
            context=request.context,
            session_id=session_id
        )
        
        # Create response
        response = ChatResponse(
            session_id=session_id,
            response=rag_result["answer"],
            sources=rag_result["sources"],
            confidence_score=rag_result["confidence"],
            processing_time_ms=rag_result["processing_time"],
            suggested_followups=rag_result.get("followups", [])
        )
        
        # Update progress in background
        background_tasks.add_task(
            progress_service.complete_task,
            progress_id,
            {"response_length": len(response.response)}
        )
        
        logger.info(f"Chat response generated - Session: {session_id}")
        return response
        
    except Exception as e:
        logger.error(f"Chat processing failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process chat request: {str(e)}"
        )

@router.get("/chat/history/{session_id}")
async def get_chat_history(
    session_id: str,
    limit: Optional[int] = 50
) -> List[ChatMessage]:
    """
    Retrieve chat history for a session
    """
    try:
        # Placeholder implementation
        logger.info(f"Retrieving chat history for session: {session_id}")
        
        # This would typically fetch from a database
        return [
            ChatMessage(
                id=str(uuid.uuid4()),
                session_id=session_id,
                message="Sample historical message",
                sender="user",
                timestamp=datetime.utcnow(),
                metadata={}
            )
        ]
        
    except Exception as e:
        logger.error(f"Failed to retrieve chat history: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve chat history: {str(e)}"
        )

@router.delete("/chat/history/{session_id}")
async def clear_chat_history(session_id: str):
    """
    Clear chat history for a session
    """
    try:
        logger.info(f"Clearing chat history for session: {session_id}")
        
        # Placeholder implementation
        # This would typically delete from database
        
        return {"message": f"Chat history cleared for session {session_id}"}
        
    except Exception as e:
        logger.error(f"Failed to clear chat history: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to clear chat history: {str(e)}"
        )