"""
Context manager for RAG pipeline
Handles context building and management
"""

from typing import Dict, List, Any, Optional
import logging
from datetime import datetime

from app.core.config import settings

logger = logging.getLogger(__name__)

class ContextManager:
    """Manages context building for RAG pipeline"""
    
    def __init__(self):
        self.max_context_length = settings.MAX_CONTEXT_LENGTH
        self.session_contexts = {}  # In-memory session storage
    
    async def build_context(
        self,
        query: str,
        documents: List[Dict[str, Any]],
        max_length: Optional[int] = None,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Build context from retrieved documents
        
        Args:
            query: User's question
            documents: Retrieved and reranked documents
            max_length: Maximum context length
            session_id: Session identifier for context tracking
            
        Returns:
            Dict containing formatted context and metadata
        """
        try:
            max_len = max_length or self.max_context_length
            logger.info(f"Building context from {len(documents)} documents")
            
            # Get session context if available
            session_context = ""
            if session_id:
                session_context = self._get_session_context(session_id)
            
            # Build context components
            context_parts = []
            total_length = 0
            sources_used = []
            
            # Add session context if available and relevant
            if session_context and len(session_context) < max_len // 4:
                context_parts.append(f"Previous conversation context:\n{session_context}\n")
                total_length += len(session_context)
            
            # Add document content
            for i, doc in enumerate(documents):
                content = doc.get("content", "")
                title = doc.get("title", f"Document {i+1}")
                
                # Format document content
                doc_text = f"Source {i+1} - {title}:\n{content}\n"
                
                # Check if adding this document exceeds limit
                if total_length + len(doc_text) > max_len:
                    # Try to fit partial content
                    remaining_space = max_len - total_length - 100  # Leave buffer
                    if remaining_space > 200:  # Only if meaningful space left
                        truncated_content = content[:remaining_space] + "..."
                        doc_text = f"Source {i+1} - {title}:\n{truncated_content}\n"
                        context_parts.append(doc_text)
                        total_length += len(doc_text)
                        sources_used.append(doc)
                    break
                else:
                    context_parts.append(doc_text)
                    total_length += len(doc_text)
                    sources_used.append(doc)
            
            # Format final context
            formatted_context = "\n".join(context_parts)
            
            # Calculate quality score
            quality_score = self._calculate_context_quality(
                query=query,
                context=formatted_context,
                sources=sources_used
            )
            
            # Update session context
            if session_id:
                self._update_session_context(session_id, query, formatted_context)
            
            result = {
                "formatted_context": formatted_context,
                "quality_score": quality_score,
                "sources_count": len(sources_used),
                "total_length": total_length,
                "metadata": {
                    "context_building_timestamp": datetime.utcnow().isoformat(),
                    "session_id": session_id,
                    "truncated": total_length >= max_len * 0.9
                }
            }
            
            logger.info(f"Context built: {total_length} chars, {len(sources_used)} sources")
            return result
            
        except Exception as e:
            logger.error(f"Context building failed: {e}")
            return {
                "formatted_context": "",
                "quality_score": 0.0,
                "sources_count": 0,
                "total_length": 0,
                "metadata": {"error": str(e)}
            }
    
    def _get_session_context(self, session_id: str) -> str:
        """Retrieve session context"""
        try:
            session_data = self.session_contexts.get(session_id, {})
            recent_interactions = session_data.get("recent_interactions", [])
            
            # Build context from recent interactions
            context_parts = []
            for interaction in recent_interactions[-3:]:  # Last 3 interactions
                query = interaction.get("query", "")
                answer = interaction.get("answer", "")
                if query and answer:
                    context_parts.append(f"Q: {query}\nA: {answer[:200]}...")
            
            return "\n\n".join(context_parts)
            
        except Exception as e:
            logger.error(f"Session context retrieval failed: {e}")
            return ""
    
    def _update_session_context(
        self,
        session_id: str,
        query: str,
        context: str
    ):
        """Update session context with new interaction"""
        try:
            if session_id not in self.session_contexts:
                self.session_contexts[session_id] = {
                    "created_at": datetime.utcnow(),
                    "recent_interactions": []
                }
            
            session_data = self.session_contexts[session_id]
            
            # Add new interaction
            interaction = {
                "query": query,
                "context_used": context[:500],  # Store truncated context
                "timestamp": datetime.utcnow()
            }
            
            session_data["recent_interactions"].append(interaction)
            
            # Keep only recent interactions (max 10)
            if len(session_data["recent_interactions"]) > 10:
                session_data["recent_interactions"] = session_data["recent_interactions"][-10:]
            
            session_data["last_updated"] = datetime.utcnow()
            
        except Exception as e:
            logger.error(f"Session context update failed: {e}")
    
    def _calculate_context_quality(
        self,
        query: str,
        context: str,
        sources: List[Dict[str, Any]]
    ) -> float:
        """Calculate quality score for built context"""
        try:
            quality_factors = []
            
            # 1. Context length appropriateness
            context_length = len(context)
            if context_length == 0:
                length_score = 0.0
            elif context_length < 200:
                length_score = context_length / 200.0
            elif context_length > self.max_context_length * 0.9:
                length_score = 0.8  # Penalize overly long context
            else:
                length_score = 1.0
            
            quality_factors.append(length_score)
            
            # 2. Source diversity
            if sources:
                source_types = set(source.get("type", "unknown") for source in sources)
                diversity_score = min(1.0, len(source_types) / 3.0)  # Up to 3 types ideal
                quality_factors.append(diversity_score)
            else:
                quality_factors.append(0.0)
            
            # 3. Source relevance scores
            if sources:
                avg_relevance = sum(source.get("score", 0.0) for source in sources) / len(sources)
                quality_factors.append(avg_relevance)
            else:
                quality_factors.append(0.0)
            
            # 4. Query-context alignment
            alignment_score = self._calculate_query_alignment(query, context)
            quality_factors.append(alignment_score)
            
            # Calculate weighted average
            weights = [0.2, 0.2, 0.3, 0.3]
            quality = sum(factor * weight for factor, weight in zip(quality_factors, weights))
            
            return min(1.0, max(0.0, quality))
            
        except Exception as e:
            logger.error(f"Context quality calculation failed: {e}")
            return 0.5
    
    def _calculate_query_alignment(self, query: str, context: str) -> float:
        """Calculate how well context aligns with query"""
        try:
            if not context:
                return 0.0
            
            # Extract key terms from query
            query_terms = set(query.lower().split())
            context_lower = context.lower()
            
            # Remove common words
            stop_words = {
                'the', 'is', 'at', 'which', 'on', 'a', 'an', 'and', 'or', 'but',
                'in', 'with', 'to', 'for', 'of', 'as', 'by', 'that', 'this'
            }
            query_terms = query_terms - stop_words
            
            if not query_terms:
                return 0.5
            
            # Count how many query terms appear in context
            terms_found = sum(1 for term in query_terms if term in context_lower)
            alignment = terms_found / len(query_terms)
            
            return alignment
            
        except Exception as e:
            logger.error(f"Query alignment calculation failed: {e}")
            return 0.5
    
    def clear_session_context(self, session_id: str):
        """Clear context for a specific session"""
        try:
            if session_id in self.session_contexts:
                del self.session_contexts[session_id]
                logger.info(f"Cleared context for session: {session_id}")
        except Exception as e:
            logger.error(f"Failed to clear session context: {e}")
    
    def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """Get summary of session interactions"""
        try:
            session_data = self.session_contexts.get(session_id, {})
            
            if not session_data:
                return {"exists": False}
            
            interactions = session_data.get("recent_interactions", [])
            
            return {
                "exists": True,
                "created_at": session_data.get("created_at"),
                "last_updated": session_data.get("last_updated"),
                "interaction_count": len(interactions),
                "recent_queries": [
                    interaction.get("query", "")
                    for interaction in interactions[-5:]
                ]
            }
            
        except Exception as e:
            logger.error(f"Session summary failed: {e}")
            return {"exists": False, "error": str(e)}