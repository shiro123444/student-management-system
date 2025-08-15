"""
Document retriever for RAG pipeline
Handles similarity search and document retrieval
"""

from typing import List, Dict, Any, Optional
import logging
import numpy as np

from app.core.milvus_client import milvus_client
from app.core.neo4j_client import neo4j_client
from app.graph.graph_store import GraphStore
from app.utils.text_split import TextSplitter

logger = logging.getLogger(__name__)

class DocumentRetriever:
    """Retrieves relevant documents for query processing"""
    
    def __init__(self):
        self.milvus_client = milvus_client
        self.neo4j_client = neo4j_client
        self.graph_store = GraphStore()
        self.text_splitter = TextSplitter()
        self.embedding_model = None  # Placeholder for embedding model
    
    async def retrieve_documents(
        self,
        query: str,
        top_k: int = 5,
        session_context: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant documents for a query
        
        Args:
            query: User's question
            top_k: Number of documents to retrieve
            session_context: Optional conversation context
            filters: Optional metadata filters
            
        Returns:
            List of relevant documents with scores
        """
        try:
            logger.info(f"Retrieving documents for query: {query[:100]}...")
            
            # Generate query embedding
            query_embedding = await self._generate_embedding(query)
            
            if not query_embedding:
                logger.warning("Failed to generate query embedding")
                return []
            
            # Perform vector similarity search
            vector_results = await self._vector_search(
                query_embedding=query_embedding,
                top_k=top_k * 2,  # Get more candidates for reranking
                filters=filters
            )
            
            # Enhance with graph-based retrieval
            graph_results = await self._graph_search(
                query=query,
                top_k=top_k,
                context=session_context
            )
            
            # Combine and deduplicate results
            combined_results = self._combine_results(vector_results, graph_results)
            
            # Apply session context if available
            if session_context:
                combined_results = await self._apply_session_context(
                    results=combined_results,
                    context=session_context
                )
            
            # Sort by relevance and return top-k
            final_results = sorted(
                combined_results,
                key=lambda x: x["score"],
                reverse=True
            )[:top_k]
            
            logger.info(f"Retrieved {len(final_results)} documents")
            return final_results
            
        except Exception as e:
            logger.error(f"Document retrieval failed: {e}")
            return []
    
    async def _generate_embedding(self, text: str) -> Optional[List[float]]:
        """Generate embedding for text using embedding model"""
        try:
            # Placeholder for embedding generation
            # This would typically use sentence-transformers, OpenAI embeddings, etc.
            
            # Simulate embedding (replace with actual implementation)
            import hashlib
            text_hash = hashlib.md5(text.encode()).hexdigest()
            
            # Create a deterministic "embedding" for testing
            embedding = [
                float(int(char, 16) / 15.0) if char.isdigit() or char in 'abcdef' else 0.5
                for char in text_hash[:384]  # 384-dimensional vector
            ]
            
            # Pad or truncate to exactly 384 dimensions
            if len(embedding) < 384:
                embedding.extend([0.0] * (384 - len(embedding)))
            else:
                embedding = embedding[:384]
            
            return embedding
            
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            return None
    
    async def _vector_search(
        self,
        query_embedding: List[float],
        top_k: int,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Perform vector similarity search"""
        try:
            # Search in Milvus
            results = await self.milvus_client.search_similar(
                query_vector=query_embedding,
                top_k=top_k,
                score_threshold=0.3
            )
            
            # Convert to standard format
            formatted_results = []
            for result in results:
                formatted_results.append({
                    "id": result["content_id"],
                    "content": f"Vector search result for {result['content_id']}",
                    "score": result["score"],
                    "type": "vector_search",
                    "metadata": result.get("metadata", {})
                })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            return []
    
    async def _graph_search(
        self,
        query: str,
        top_k: int,
        context: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Perform graph-based retrieval"""
        try:
            # Extract concepts from query
            concepts = await self._extract_concepts(query)
            
            if not concepts:
                return []
            
            # Search for related concepts in knowledge graph
            graph_results = []
            for concept in concepts[:3]:  # Limit to top 3 concepts
                related_content = await self.neo4j_client.search_similar_concepts(
                    concept=concept,
                    similarity_threshold=0.7,
                    limit=top_k
                )
                
                for content in related_content:
                    graph_results.append({
                        "id": content.get("id", f"graph-{concept}"),
                        "content": content.get("content", f"Graph content related to {concept}"),
                        "score": content.get("similarity", 0.8),
                        "type": "graph_search",
                        "metadata": {
                            "concept": concept,
                            "graph_properties": content.get("properties", {})
                        }
                    })
            
            return graph_results
            
        except Exception as e:
            logger.error(f"Graph search failed: {e}")
            return []
    
    async def _extract_concepts(self, text: str) -> List[str]:
        """Extract key concepts from text"""
        try:
            # Placeholder for concept extraction
            # This would typically use NER, keyword extraction, etc.
            
            # Simple word-based extraction for placeholder
            words = text.lower().split()
            
            # Filter common educational concepts
            educational_keywords = {
                'math', 'mathematics', 'algebra', 'calculus', 'geometry',
                'science', 'physics', 'chemistry', 'biology',
                'history', 'literature', 'programming', 'computer',
                'algorithm', 'data', 'structure', 'function', 'equation'
            }
            
            concepts = [word for word in words if word in educational_keywords]
            
            # Add some generic concepts if none found
            if not concepts:
                concepts = ['education', 'learning', 'knowledge']
            
            return concepts[:5]  # Return top 5 concepts
            
        except Exception as e:
            logger.error(f"Concept extraction failed: {e}")
            return []
    
    def _combine_results(
        self,
        vector_results: List[Dict[str, Any]],
        graph_results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Combine and deduplicate results from different sources"""
        try:
            combined = {}
            
            # Add vector results
            for result in vector_results:
                result_id = result["id"]
                if result_id not in combined:
                    combined[result_id] = result
                    combined[result_id]["sources"] = ["vector"]
                else:
                    # Boost score if found in multiple sources
                    combined[result_id]["score"] = max(
                        combined[result_id]["score"],
                        result["score"]
                    )
                    combined[result_id]["sources"].append("vector")
            
            # Add graph results
            for result in graph_results:
                result_id = result["id"]
                if result_id not in combined:
                    combined[result_id] = result
                    combined[result_id]["sources"] = ["graph"]
                else:
                    # Boost score for multi-source results
                    combined[result_id]["score"] = min(1.0, combined[result_id]["score"] + 0.1)
                    combined[result_id]["sources"].append("graph")
            
            return list(combined.values())
            
        except Exception as e:
            logger.error(f"Result combination failed: {e}")
            return vector_results + graph_results
    
    async def _apply_session_context(
        self,
        results: List[Dict[str, Any]],
        context: str
    ) -> List[Dict[str, Any]]:
        """Apply session context to boost relevant results"""
        try:
            # Extract context concepts
            context_concepts = await self._extract_concepts(context)
            
            # Boost scores for results matching context
            for result in results:
                content_concepts = await self._extract_concepts(result["content"])
                
                # Calculate context overlap
                overlap = len(set(context_concepts) & set(content_concepts))
                if overlap > 0:
                    boost = min(0.3, overlap * 0.1)  # Max 30% boost
                    result["score"] = min(1.0, result["score"] + boost)
                    result["context_boost"] = boost
            
            return results
            
        except Exception as e:
            logger.error(f"Context application failed: {e}")
            return results