"""
Document reranker for improving retrieval relevance
"""

from typing import List, Dict, Any, Optional, Tuple
import logging
import re

logger = logging.getLogger(__name__)

class DocumentReranker:
    """Reranks retrieved documents based on query relevance"""
    
    def __init__(self):
        self.reranking_model = None  # Placeholder for reranking model
        
    async def rerank_documents(
        self,
        query: str,
        documents: List[Dict[str, Any]],
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Rerank documents based on query relevance
        
        Args:
            query: User's question
            documents: List of retrieved documents
            top_k: Number of top documents to return
            
        Returns:
            Reranked list of documents
        """
        try:
            if not documents:
                return []
            
            logger.info(f"Reranking {len(documents)} documents for query")
            
            # Calculate relevance scores
            scored_docs = []
            for doc in documents:
                relevance_score = await self._calculate_relevance(query, doc)
                
                # Update document with new score
                doc_copy = doc.copy()
                doc_copy["original_score"] = doc.get("score", 0.0)
                doc_copy["relevance_score"] = relevance_score
                doc_copy["score"] = self._combine_scores(
                    doc.get("score", 0.0),
                    relevance_score
                )
                
                scored_docs.append(doc_copy)
            
            # Sort by combined score
            reranked = sorted(
                scored_docs,
                key=lambda x: x["score"],
                reverse=True
            )
            
            result = reranked[:top_k]
            logger.info(f"Reranked documents, returning top {len(result)}")
            
            return result
            
        except Exception as e:
            logger.error(f"Reranking failed: {e}")
            return documents[:top_k]
    
    async def _calculate_relevance(
        self,
        query: str,
        document: Dict[str, Any]
    ) -> float:
        """Calculate relevance score between query and document"""
        try:
            content = document.get("content", "")
            
            # Multiple relevance signals
            scores = []
            
            # 1. Keyword overlap
            keyword_score = self._calculate_keyword_overlap(query, content)
            scores.append(keyword_score)
            
            # 2. Semantic similarity (placeholder)
            semantic_score = await self._calculate_semantic_similarity(query, content)
            scores.append(semantic_score)
            
            # 3. Document type relevance
            type_score = self._calculate_type_relevance(
                query, 
                document.get("type", "unknown")
            )
            scores.append(type_score)
            
            # 4. Freshness score
            freshness_score = self._calculate_freshness_score(document)
            scores.append(freshness_score)
            
            # Weighted combination
            weights = [0.3, 0.4, 0.2, 0.1]
            relevance = sum(score * weight for score, weight in zip(scores, weights))
            
            return min(1.0, max(0.0, relevance))
            
        except Exception as e:
            logger.error(f"Relevance calculation failed: {e}")
            return 0.5  # Default score
    
    def _calculate_keyword_overlap(self, query: str, content: str) -> float:
        """Calculate keyword overlap between query and content"""
        try:
            # Normalize text
            query_clean = re.sub(r'[^\w\s]', '', query.lower())
            content_clean = re.sub(r'[^\w\s]', '', content.lower())
            
            query_words = set(query_clean.split())
            content_words = set(content_clean.split())
            
            # Remove common stop words
            stop_words = {
                'the', 'is', 'at', 'which', 'on', 'a', 'an', 'and', 'or', 'but',
                'in', 'with', 'to', 'for', 'of', 'as', 'by', 'that', 'this',
                'what', 'when', 'where', 'how', 'why', 'can', 'could', 'would'
            }
            
            query_words = query_words - stop_words
            content_words = content_words - stop_words
            
            if not query_words:
                return 0.0
            
            # Calculate overlap
            overlap = len(query_words & content_words)
            overlap_ratio = overlap / len(query_words)
            
            return overlap_ratio
            
        except Exception as e:
            logger.error(f"Keyword overlap calculation failed: {e}")
            return 0.0
    
    async def _calculate_semantic_similarity(self, query: str, content: str) -> float:
        """Calculate semantic similarity (placeholder)"""
        try:
            # Placeholder for semantic similarity calculation
            # This would typically use embeddings and cosine similarity
            
            # Simple heuristic based on content length and keyword density
            content_length = len(content)
            query_length = len(query)
            
            # Prefer moderate length content (not too short, not too long)
            if content_length < 50:
                length_score = content_length / 50.0
            elif content_length > 1000:
                length_score = 1000.0 / content_length
            else:
                length_score = 1.0
            
            # Boost for educational keywords
            educational_keywords = [
                'learn', 'teach', 'explain', 'understand', 'concept',
                'theory', 'practice', 'example', 'definition', 'formula'
            ]
            
            keyword_boost = 0.0
            for keyword in educational_keywords:
                if keyword in content.lower():
                    keyword_boost += 0.1
            
            semantic_score = min(1.0, length_score + keyword_boost)
            return semantic_score
            
        except Exception as e:
            logger.error(f"Semantic similarity calculation failed: {e}")
            return 0.5
    
    def _calculate_type_relevance(self, query: str, doc_type: str) -> float:
        """Calculate relevance based on document type"""
        try:
            # Define type preferences for different query patterns
            type_preferences = {
                'educational_content': 0.9,
                'textbook': 0.8,
                'lecture_notes': 0.7,
                'research_paper': 0.6,
                'wiki_article': 0.5,
                'forum_post': 0.4,
                'unknown': 0.3
            }
            
            # Boost certain types for specific query patterns
            query_lower = query.lower()
            
            if any(word in query_lower for word in ['definition', 'what is', 'explain']):
                if doc_type in ['textbook', 'wiki_article']:
                    return min(1.0, type_preferences.get(doc_type, 0.5) + 0.2)
            
            elif any(word in query_lower for word in ['example', 'how to', 'tutorial']):
                if doc_type in ['lecture_notes', 'educational_content']:
                    return min(1.0, type_preferences.get(doc_type, 0.5) + 0.2)
            
            return type_preferences.get(doc_type, 0.5)
            
        except Exception as e:
            logger.error(f"Type relevance calculation failed: {e}")
            return 0.5
    
    def _calculate_freshness_score(self, document: Dict[str, Any]) -> float:
        """Calculate freshness score based on document age"""
        try:
            # Placeholder for freshness calculation
            # This would typically use document timestamps
            
            metadata = document.get("metadata", {})
            doc_type = document.get("type", "unknown")
            
            # Different freshness requirements for different types
            if doc_type in ['research_paper', 'news_article']:
                # Recent content preferred
                return 0.8
            elif doc_type in ['textbook', 'educational_content']:
                # Evergreen content, freshness less important
                return 0.9
            else:
                return 0.7
            
        except Exception as e:
            logger.error(f"Freshness calculation failed: {e}")
            return 0.7
    
    def _combine_scores(self, original_score: float, relevance_score: float) -> float:
        """Combine original retrieval score with relevance score"""
        try:
            # Weighted combination favoring relevance
            combined = (original_score * 0.4) + (relevance_score * 0.6)
            return min(1.0, max(0.0, combined))
            
        except Exception as e:
            logger.error(f"Score combination failed: {e}")
            return original_score