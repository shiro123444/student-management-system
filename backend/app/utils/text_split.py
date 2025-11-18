"""
Text splitting utilities for document processing
"""

from typing import List, Dict, Any, Optional
import re
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

class TextSplitter:
    """Splits text into chunks for processing"""
    
    def __init__(
        self,
        chunk_size: int = None,
        chunk_overlap: int = None,
        separators: Optional[List[str]] = None
    ):
        self.chunk_size = chunk_size or settings.CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or settings.CHUNK_OVERLAP
        self.separators = separators or ["\n\n", "\n", ". ", " ", ""]
    
    def split_text(self, text: str) -> List[Dict[str, Any]]:
        """Split text into chunks with metadata"""
        try:
            chunks = []
            
            # Clean the text
            text = self._clean_text(text)
            
            if len(text) <= self.chunk_size:
                return [{
                    'content': text,
                    'start_index': 0,
                    'end_index': len(text),
                    'chunk_id': 0
                }]
            
            # Split using hierarchical separators
            text_chunks = self._split_by_separators(text)
            
            # Create chunks with metadata
            for i, chunk in enumerate(text_chunks):
                if chunk.strip():  # Skip empty chunks
                    chunks.append({
                        'content': chunk.strip(),
                        'start_index': text.find(chunk),
                        'end_index': text.find(chunk) + len(chunk),
                        'chunk_id': i,
                        'length': len(chunk.strip())
                    })
            
            logger.info(f"Split text into {len(chunks)} chunks")
            return chunks
            
        except Exception as e:
            logger.error(f"Text splitting failed: {e}")
            return [{'content': text, 'start_index': 0, 'end_index': len(text), 'chunk_id': 0}]
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        try:
            # Remove excessive whitespace
            text = re.sub(r'\s+', ' ', text)
            
            # Remove control characters
            text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x84\x86-\x9f]', '', text)
            
            # Normalize quotes
            text = text.replace('"', '"').replace('"', '"')
            text = text.replace(''', "'").replace(''', "'")
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"Text cleaning failed: {e}")
            return text
    
    def _split_by_separators(self, text: str) -> List[str]:
        """Split text using hierarchical separators"""
        try:
            chunks = [text]
            
            for separator in self.separators:
                new_chunks = []
                
                for chunk in chunks:
                    if len(chunk) <= self.chunk_size:
                        new_chunks.append(chunk)
                    else:
                        # Split by current separator
                        split_chunks = self._split_with_overlap(chunk, separator)
                        new_chunks.extend(split_chunks)
                
                chunks = new_chunks
                
                # Check if all chunks are small enough
                if all(len(chunk) <= self.chunk_size for chunk in chunks):
                    break
            
            return chunks
            
        except Exception as e:
            logger.error(f"Separator splitting failed: {e}")
            return [text]
    
    def _split_with_overlap(self, text: str, separator: str) -> List[str]:
        """Split text with overlap to maintain context"""
        try:
            if not separator:
                # Character-level splitting for final fallback
                return self._split_by_characters(text)
            
            parts = text.split(separator)
            chunks = []
            current_chunk = ""
            
            for part in parts:
                test_chunk = current_chunk + separator + part if current_chunk else part
                
                if len(test_chunk) <= self.chunk_size:
                    current_chunk = test_chunk
                else:
                    if current_chunk:
                        chunks.append(current_chunk)
                        
                        # Create overlap
                        overlap_text = self._get_overlap_text(current_chunk)
                        current_chunk = overlap_text + separator + part if overlap_text else part
                    else:
                        current_chunk = part
            
            if current_chunk:
                chunks.append(current_chunk)
            
            return chunks
            
        except Exception as e:
            logger.error(f"Overlap splitting failed: {e}")
            return [text]
    
    def _split_by_characters(self, text: str) -> List[str]:
        """Split by characters as final fallback"""
        try:
            chunks = []
            start = 0
            
            while start < len(text):
                end = start + self.chunk_size
                
                # Try to find a good break point near the end
                if end < len(text):
                    # Look for whitespace near the end
                    for i in range(end, max(start + self.chunk_size - 50, start), -1):
                        if text[i].isspace():
                            end = i
                            break
                
                chunk = text[start:end]
                chunks.append(chunk)
                
                # Move start with overlap
                start = max(end - self.chunk_overlap, start + 1)
            
            return chunks
            
        except Exception as e:
            logger.error(f"Character splitting failed: {e}")
            return [text]
    
    def _get_overlap_text(self, text: str) -> str:
        """Get overlap text from the end of a chunk"""
        try:
            if len(text) <= self.chunk_overlap:
                return text
            
            overlap = text[-self.chunk_overlap:]
            
            # Try to start from a word boundary
            space_index = overlap.find(' ')
            if space_index > 0:
                overlap = overlap[space_index + 1:]
            
            return overlap
            
        except Exception as e:
            logger.error(f"Overlap text extraction failed: {e}")
            return ""

# Document-specific splitters
class DocumentSplitter(TextSplitter):
    """Splitter for structured documents"""
    
    def __init__(self, document_type: str = "general", **kwargs):
        super().__init__(**kwargs)
        self.document_type = document_type
        self._set_document_specific_separators()
    
    def _set_document_specific_separators(self):
        """Set separators based on document type"""
        if self.document_type == "academic":
            self.separators = [
                "\n\n## ", "\n\n# ", "\n\n### ",  # Headers
                "\n\n", "\n",  # Paragraphs
                ". ", "! ", "? ",  # Sentences
                ", ", " ", ""  # Phrases and characters
            ]
        elif self.document_type == "code":
            self.separators = [
                "\n\nclass ", "\n\ndef ", "\n\nfunction ",  # Code blocks
                "\n\n", "\n",  # Lines
                "; ", " ", ""  # Statements
            ]
        elif self.document_type == "markdown":
            self.separators = [
                "\n\n## ", "\n\n# ", "\n\n### ", "\n\n#### ",  # Headers
                "\n\n```", "\n```",  # Code blocks
                "\n\n", "\n",  # Paragraphs
                ". ", " ", ""  # Default
            ]