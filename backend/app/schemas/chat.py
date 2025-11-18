"""
Chat-related Pydantic schemas
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class MessageSender(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class ChatMessage(BaseModel):
    id: str = Field(..., description="Unique message identifier")
    session_id: str = Field(..., description="Session identifier")
    message: str = Field(..., description="Message content")
    sender: MessageSender = Field(..., description="Message sender")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class SourceDocument(BaseModel):
    id: str = Field(..., description="Document identifier")
    title: str = Field(..., description="Document title")
    content_preview: str = Field(..., description="Content preview")
    relevance_score: float = Field(..., ge=0.0, le=1.0, description="Relevance score")
    document_type: str = Field(..., description="Type of document")
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000, description="User's question")
    session_id: Optional[str] = Field(None, description="Session identifier for context")
    context: Optional[str] = Field(None, description="Additional context")
    include_sources: bool = Field(default=True, description="Include source documents")
    max_sources: int = Field(default=3, ge=1, le=10, description="Maximum number of sources")
    
    class Config:
        schema_extra = {
            "example": {
                "query": "What is machine learning?",
                "session_id": "abc123",
                "context": "Previous discussion about AI",
                "include_sources": True,
                "max_sources": 3
            }
        }

class ChatResponse(BaseModel):
    session_id: str = Field(..., description="Session identifier")
    response: str = Field(..., description="AI response to the query")
    sources: List[SourceDocument] = Field(default_factory=list, description="Source documents")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Response confidence")
    processing_time_ms: int = Field(..., description="Processing time in milliseconds")
    suggested_followups: List[str] = Field(default_factory=list, description="Suggested follow-up questions")
    
    class Config:
        schema_extra = {
            "example": {
                "session_id": "abc123",
                "response": "Machine learning is a subset of artificial intelligence...",
                "sources": [
                    {
                        "id": "doc1",
                        "title": "Introduction to ML",
                        "content_preview": "Machine learning involves...",
                        "relevance_score": 0.95,
                        "document_type": "textbook",
                        "metadata": {}
                    }
                ],
                "confidence_score": 0.87,
                "processing_time_ms": 1250,
                "suggested_followups": [
                    "What are the types of machine learning?",
                    "How does machine learning differ from traditional programming?"
                ]
            }
        }