"""
Security utilities for data anonymization and validation
"""

import re
import hashlib
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)

def anonymize_query(query: str) -> str:
    """
    Anonymize personally identifiable information in queries
    """
    try:
        # Remove email addresses
        query = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', query)
        
        # Remove phone numbers
        query = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[PHONE]', query)
        
        # Remove social security numbers
        query = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[SSN]', query)
        
        # Remove credit card numbers (basic pattern)
        query = re.sub(r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b', '[CREDIT_CARD]', query)
        
        # Remove names (common patterns with titles)
        query = re.sub(r'\b(Mr|Mrs|Ms|Dr|Prof)\.?\s+[A-Z][a-z]+\b', '[NAME]', query)
        
        return query
        
    except Exception as e:
        logger.error(f"Query anonymization failed: {e}")
        return query

def hash_sensitive_data(data: str, salt: str = "educational_qa_bot") -> str:
    """
    Hash sensitive data for secure storage
    """
    try:
        combined = f"{salt}{data}".encode('utf-8')
        return hashlib.sha256(combined).hexdigest()
    except Exception as e:
        logger.error(f"Data hashing failed: {e}")
        return data

def validate_file_type(filename: Optional[str]) -> bool:
    """
    Validate if file type is allowed
    """
    if not filename:
        return False
        
    try:
        from app.core.config import settings
        
        allowed_extensions = settings.ALLOWED_FILE_TYPES
        file_extension = '.' + filename.split('.')[-1].lower() if '.' in filename else ''
        
        return file_extension in allowed_extensions
        
    except Exception as e:
        logger.error(f"File type validation failed: {e}")
        return False

def scan_file_content(content: bytes) -> bool:
    """
    Basic security scan of file content
    """
    try:
        # Check file size
        if len(content) == 0:
            return False
            
        # Check for binary executable signatures
        dangerous_signatures = [
            b'\x4d\x5a',  # PE executable
            b'\x7f\x45\x4c\x46',  # ELF executable
            b'\xfe\xed\xfa',  # Mach-O executable
        ]
        
        for signature in dangerous_signatures:
            if content.startswith(signature):
                logger.warning("Potentially dangerous file detected")
                return False
        
        # Check for script injections in text files
        try:
            text_content = content.decode('utf-8', errors='ignore')
            
            # Check for common script injection patterns
            dangerous_patterns = [
                r'<script[^>]*>.*?</script>',
                r'javascript:',
                r'vbscript:',
                r'onload\s*=',
                r'onerror\s*=',
                r'eval\s*\(',
                r'exec\s*\(',
                r'system\s*\(',
                r'import\s+os',
                r'__import__',
            ]
            
            for pattern in dangerous_patterns:
                if re.search(pattern, text_content, re.IGNORECASE):
                    logger.warning(f"Potentially dangerous content pattern detected: {pattern}")
                    return False
                    
        except UnicodeDecodeError:
            # Binary file, basic checks already done
            pass
        
        return True
        
    except Exception as e:
        logger.error(f"File content scan failed: {e}")
        return False

def sanitize_input(text: str, max_length: int = 10000) -> str:
    """
    Sanitize user input to prevent injection attacks
    """
    try:
        if not text:
            return ""
            
        # Truncate to max length
        text = text[:max_length]
        
        # Remove null bytes
        text = text.replace('\x00', '')
        
        # Remove or escape potentially dangerous characters
        # Keep basic punctuation and Unicode characters for educational content
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x84\x86-\x9f]', '', text)
        
        return text.strip()
        
    except Exception as e:
        logger.error(f"Input sanitization failed: {e}")
        return ""

def validate_session_id(session_id: str) -> bool:
    """
    Validate session ID format
    """
    try:
        # Check if it's a valid UUID format
        import uuid
        uuid.UUID(session_id)
        return True
    except (ValueError, TypeError):
        # Check if it's alphanumeric with reasonable length
        if re.match(r'^[a-zA-Z0-9_-]{8,64}$', session_id):
            return True
        return False

def generate_secure_token(length: int = 32) -> str:
    """
    Generate a secure random token
    """
    try:
        import secrets
        import string
        
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(length))
        
    except Exception as e:
        logger.error(f"Token generation failed: {e}")
        import uuid
        return str(uuid.uuid4()).replace('-', '')

def mask_sensitive_info(text: str) -> str:
    """
    Mask sensitive information in logs and responses
    """
    try:
        # Mask API keys
        text = re.sub(r'(api[_-]?key|token|secret)["\']?\s*[:=]\s*["\']?([a-zA-Z0-9]{8,})["\']?', 
                     r'\1: [REDACTED]', text, flags=re.IGNORECASE)
        
        # Mask passwords
        text = re.sub(r'(password|passwd|pwd)["\']?\s*[:=]\s*["\']?([^"\'\s]{6,})["\']?', 
                     r'\1: [REDACTED]', text, flags=re.IGNORECASE)
        
        return text
        
    except Exception as e:
        logger.error(f"Sensitive info masking failed: {e}")
        return text