"""
Message model for chat functionality
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from enum import Enum

class MessageSender(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class MessageStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class Message(BaseModel):
    """Chat message model"""
    
    id: str = Field(..., description="Unique message identifier")
    session_id: str = Field(..., description="Session identifier")
    content: str = Field(..., description="Message content")
    sender: MessageSender = Field(..., description="Message sender")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Message timestamp")
    status: MessageStatus = Field(default=MessageStatus.COMPLETED, description="Message status")
    
    # Optional fields for AI responses
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="AI confidence score")
    processing_time_ms: Optional[int] = Field(None, ge=0, description="Processing time in milliseconds")
    
    # Source information for answers
    sources: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="Source documents")
    suggested_followups: Optional[List[str]] = Field(default_factory=list, description="Suggested follow-up questions")
    
    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    # Error information
    error: Optional[str] = Field(None, description="Error message if processing failed")
    
    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        schema_extra = {
            "example": {
                "id": "msg_123",
                "session_id": "session_456",
                "content": "What is machine learning?",
                "sender": "user",
                "timestamp": "2024-01-15T10:30:00Z",
                "status": "completed",
                "metadata": {"query_type": "definition"}
            }
        }

class ChatSession(BaseModel):
    """Chat session model"""
    
    id: str = Field(..., description="Unique session identifier")
    user_id: Optional[str] = Field(None, description="User identifier (if authenticated)")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Session creation time")
    last_activity: datetime = Field(default_factory=datetime.utcnow, description="Last activity time")
    
    # Session statistics
    message_count: int = Field(default=0, ge=0, description="Total messages in session")
    topics_discussed: List[str] = Field(default_factory=list, description="Topics discussed in session")
    
    # Session settings
    settings: Dict[str, Any] = Field(default_factory=dict, description="Session-specific settings")
    
    # Session status
    is_active: bool = Field(default=True, description="Whether session is active")
    
    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class MessageThread(BaseModel):
    """Thread of related messages"""
    
    id: str = Field(..., description="Thread identifier")
    session_id: str = Field(..., description="Parent session ID")
    messages: List[Message] = Field(default_factory=list, description="Messages in thread")
    topic: Optional[str] = Field(None, description="Thread topic")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Thread creation time")
    
    def add_message(self, message: Message):
        """Add a message to the thread"""
        self.messages.append(message)
    
    def get_last_message(self) -> Optional[Message]:
        """Get the last message in the thread"""
        return self.messages[-1] if self.messages else None
    
    def get_messages_by_sender(self, sender: MessageSender) -> List[Message]:
        """Get messages from a specific sender"""
        return [msg for msg in self.messages if msg.sender == sender]