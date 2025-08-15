"""
Ingestion service for processing uploaded files
"""

import asyncio
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
import uuid
import json

from app.core.config import settings
from app.utils.text_split import DocumentSplitter
from app.core.milvus_client import milvus_client
from app.core.neo4j_client import neo4j_client
from app.services.progress_service import ProgressService

logger = logging.getLogger(__name__)

class IngestService:
    """Service for ingesting and processing educational content"""
    
    def __init__(self):
        self.progress_service = ProgressService()
        self.text_splitter = DocumentSplitter()
        
    async def process_file(
        self,
        file_path: Path,
        file_id: str,
        document_type: str,
        metadata: str,
        progress_id: str
    ):
        """Process an uploaded file asynchronously"""
        try:
            logger.info(f"Starting file processing: {file_id}")
            
            # Update progress
            await self.progress_service.update_task_progress(
                progress_id, 
                progress=10, 
                message="Extracting text content"
            )
            
            # Extract text content
            content = await self._extract_text(file_path)
            
            if not content:
                raise ValueError("No text content extracted from file")
            
            # Parse metadata
            try:
                metadata_dict = json.loads(metadata) if metadata else {}
            except json.JSONDecodeError:
                metadata_dict = {}
            
            # Update progress
            await self.progress_service.update_task_progress(
                progress_id,
                progress=30,
                message="Splitting text into chunks"
            )
            
            # Split text into chunks
            chunks = self.text_splitter.split_text(content)
            
            # Update progress
            await self.progress_service.update_task_progress(
                progress_id,
                progress=50,
                message="Generating embeddings"
            )
            
            # Generate embeddings for chunks
            embeddings = await self._generate_embeddings(chunks)
            
            # Update progress
            await self.progress_service.update_task_progress(
                progress_id,
                progress=70,
                message="Storing in vector database"
            )
            
            # Store in vector database
            await self._store_vectors(file_id, chunks, embeddings, metadata_dict)
            
            # Update progress
            await self.progress_service.update_task_progress(
                progress_id,
                progress=85,
                message="Creating knowledge graph entries"
            )
            
            # Extract concepts and store in knowledge graph
            await self._process_knowledge_graph(file_id, content, metadata_dict)
            
            # Update progress
            await self.progress_service.update_task_progress(
                progress_id,
                progress=95,
                message="Finalizing processing"
            )
            
            # Store processing metadata
            processing_result = {
                "file_id": file_id,
                "document_type": document_type,
                "chunk_count": len(chunks),
                "total_characters": len(content),
                "metadata": metadata_dict,
                "processing_status": "completed"
            }
            
            # Complete processing
            await self.progress_service.complete_task(
                progress_id,
                result=processing_result
            )
            
            logger.info(f"File processing completed: {file_id}")
            
        except Exception as e:
            logger.error(f"File processing failed for {file_id}: {e}")
            await self.progress_service.fail_task(
                progress_id,
                error=str(e)
            )
            
            # Clean up on failure
            try:
                await self.delete_file(file_id)
            except Exception as cleanup_error:
                logger.error(f"Cleanup failed for {file_id}: {cleanup_error}")
    
    async def _extract_text(self, file_path: Path) -> str:
        """Extract text content from file"""
        try:
            file_extension = file_path.suffix.lower()
            
            if file_extension == '.txt':
                return await self._extract_text_from_txt(file_path)
            elif file_extension == '.md':
                return await self._extract_text_from_markdown(file_path)
            elif file_extension == '.pdf':
                return await self._extract_text_from_pdf(file_path)
            elif file_extension in ['.docx', '.doc']:
                return await self._extract_text_from_docx(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_extension}")
                
        except Exception as e:
            logger.error(f"Text extraction failed: {e}")
            raise
    
    async def _extract_text_from_txt(self, file_path: Path) -> str:
        """Extract text from .txt file"""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    
    async def _extract_text_from_markdown(self, file_path: Path) -> str:
        """Extract text from .md file"""
        # For now, treat as plain text
        # In production, could parse markdown structure
        return await self._extract_text_from_txt(file_path)
    
    async def _extract_text_from_pdf(self, file_path: Path) -> str:
        """Extract text from .pdf file"""
        # Placeholder - would use PyPDF2, pdfplumber, or similar
        logger.warning("PDF extraction not implemented - using placeholder")
        return f"PDF content from {file_path.name} (extraction not implemented)"
    
    async def _extract_text_from_docx(self, file_path: Path) -> str:
        """Extract text from .docx file"""
        # Placeholder - would use python-docx or similar
        logger.warning("DOCX extraction not implemented - using placeholder")
        return f"DOCX content from {file_path.name} (extraction not implemented)"
    
    async def _generate_embeddings(self, chunks: List[Dict[str, Any]]) -> List[List[float]]:
        """Generate embeddings for text chunks"""
        embeddings = []
        
        for chunk in chunks:
            # Placeholder embedding generation
            # In production, would use sentence-transformers or OpenAI embeddings
            content = chunk.get('content', '')
            
            # Simple hash-based embedding for testing
            import hashlib
            text_hash = hashlib.md5(content.encode()).hexdigest()
            
            # Create deterministic "embedding"
            embedding = [
                float(int(char, 16) / 15.0) if char.isdigit() or char in 'abcdef' else 0.5
                for char in text_hash[:384]
            ]
            
            # Pad to 384 dimensions
            if len(embedding) < 384:
                embedding.extend([0.0] * (384 - len(embedding)))
            else:
                embedding = embedding[:384]
            
            embeddings.append(embedding)
        
        return embeddings
    
    async def _store_vectors(
        self,
        file_id: str,
        chunks: List[Dict[str, Any]],
        embeddings: List[List[float]],
        metadata: Dict[str, Any]
    ):
        """Store vectors in Milvus database"""
        try:
            # Prepare data for insertion
            content_ids = [f"{file_id}_chunk_{i}" for i in range(len(chunks))]
            
            # Add chunk metadata
            chunk_metadata = []
            for i, chunk in enumerate(chunks):
                chunk_meta = {
                    **metadata,
                    "file_id": file_id,
                    "chunk_id": chunk.get('chunk_id', i),
                    "start_index": chunk.get('start_index', 0),
                    "end_index": chunk.get('end_index', len(chunk.get('content', ''))),
                    "length": chunk.get('length', len(chunk.get('content', '')))
                }
                chunk_metadata.append(chunk_meta)
            
            # Insert into Milvus
            success = await milvus_client.insert_vectors(
                embeddings=embeddings,
                content_ids=content_ids,
                metadata=chunk_metadata
            )
            
            if not success:
                raise Exception("Failed to insert vectors into Milvus")
                
            logger.info(f"Stored {len(embeddings)} vectors for file {file_id}")
            
        except Exception as e:
            logger.error(f"Vector storage failed: {e}")
            raise
    
    async def _process_knowledge_graph(
        self,
        file_id: str,
        content: str,
        metadata: Dict[str, Any]
    ):
        """Process content for knowledge graph"""
        try:
            # Extract concepts from content
            concepts = await self._extract_concepts(content)
            
            # Create document node
            doc_properties = {
                "file_id": file_id,
                "title": metadata.get("title", f"Document {file_id}"),
                "content_type": metadata.get("document_type", "educational_content"),
                "word_count": len(content.split()),
                "domain": metadata.get("domain", "general"),
                **metadata
            }
            
            doc_node_id = await neo4j_client.create_node(
                labels=["Document"],
                properties=doc_properties
            )
            
            # Create concept nodes and relationships
            for concept in concepts:
                concept_properties = {
                    "name": concept,
                    "domain": metadata.get("domain", "general"),
                    "difficulty_level": metadata.get("difficulty", "unknown")
                }
                
                concept_node_id = await neo4j_client.create_node(
                    labels=["Concept"],
                    properties=concept_properties
                )
                
                # Create EXPLAINS relationship
                if doc_node_id and concept_node_id:
                    await neo4j_client.create_relationship(
                        source_id=doc_node_id,
                        target_id=concept_node_id,
                        relationship_type="EXPLAINS",
                        properties={"confidence": 0.8}
                    )
            
            logger.info(f"Created knowledge graph entries for file {file_id}")
            
        except Exception as e:
            logger.error(f"Knowledge graph processing failed: {e}")
            # Don't raise - this is not critical for basic functionality
    
    async def _extract_concepts(self, content: str) -> List[str]:
        """Extract concepts from content"""
        # Simple keyword-based concept extraction
        # In production, would use NLP libraries like spaCy or NLTK
        
        educational_keywords = {
            # Computer Science
            'algorithm', 'programming', 'software', 'database', 'network',
            'machine learning', 'artificial intelligence', 'data structure',
            'computer', 'coding', 'development', 'system', 'application',
            
            # Mathematics
            'equation', 'formula', 'calculus', 'algebra', 'geometry',
            'statistics', 'probability', 'function', 'derivative', 'integral',
            'matrix', 'vector', 'theorem', 'proof', 'mathematics',
            
            # Science
            'experiment', 'hypothesis', 'theory', 'research', 'analysis',
            'molecule', 'atom', 'cell', 'energy', 'force', 'chemical',
            'physics', 'chemistry', 'biology', 'science', 'scientific',
            
            # General Education
            'learning', 'education', 'knowledge', 'study', 'concept',
            'principle', 'method', 'technique', 'process', 'procedure'
        }
        
        content_lower = content.lower()
        found_concepts = []
        
        for keyword in educational_keywords:
            if keyword in content_lower:
                found_concepts.append(keyword)
        
        # Add some content-specific concepts based on frequency
        words = content_lower.split()
        word_freq = {}
        for word in words:
            if len(word) > 4 and word.isalpha():  # Filter meaningful words
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Add high-frequency words as potential concepts
        frequent_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        for word, freq in frequent_words:
            if freq > 3 and word not in found_concepts:  # Appears multiple times
                found_concepts.append(word)
        
        return found_concepts[:20]  # Limit to top 20 concepts
    
    async def delete_file(self, file_id: str) -> bool:
        """Delete a file and all its processed data"""
        try:
            # Delete from vector database
            await milvus_client.delete_by_content_id(file_id)
            
            # Delete from knowledge graph
            # This would delete the document node and its relationships
            
            # Delete physical file if it exists
            # Implementation depends on storage strategy
            
            logger.info(f"Deleted file {file_id}")
            return True
            
        except Exception as e:
            logger.error(f"File deletion failed for {file_id}: {e}")
            return False
    
    async def get_file_status(self, file_id: str) -> Optional[Dict[str, Any]]:
        """Get processing status of a file"""
        # This would query the database for file status
        # Placeholder implementation
        return {
            "file_id": file_id,
            "status": "unknown",
            "message": "Status tracking not implemented"
        }