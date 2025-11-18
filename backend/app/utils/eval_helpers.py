"""
Evaluation helpers for RAG pipeline performance
"""

from typing import Dict, List, Any, Optional, Tuple
import logging
import re
from datetime import datetime

logger = logging.getLogger(__name__)

def calculate_confidence_score(
    query: str,
    answer: str,
    sources: List[Dict[str, Any]],
    context_quality: float
) -> float:
    """
    Calculate confidence score for RAG response
    
    Args:
        query: User's question
        answer: Generated answer
        sources: Retrieved source documents
        context_quality: Quality score of context used
        
    Returns:
        Confidence score between 0.0 and 1.0
    """
    try:
        scores = []
        
        # 1. Source quality score
        if sources:
            avg_source_score = sum(source.get('score', 0.0) for source in sources) / len(sources)
            scores.append(avg_source_score)
        else:
            scores.append(0.0)
        
        # 2. Context quality score
        scores.append(context_quality)
        
        # 3. Answer completeness score
        completeness_score = calculate_answer_completeness(query, answer)
        scores.append(completeness_score)
        
        # 4. Query-answer alignment score
        alignment_score = calculate_query_answer_alignment(query, answer)
        scores.append(alignment_score)
        
        # 5. Answer length appropriateness
        length_score = calculate_answer_length_score(answer)
        scores.append(length_score)
        
        # Weighted average
        weights = [0.25, 0.2, 0.25, 0.2, 0.1]
        confidence = sum(score * weight for score, weight in zip(scores, weights))
        
        return min(1.0, max(0.0, confidence))
        
    except Exception as e:
        logger.error(f"Confidence calculation failed: {e}")
        return 0.5

def calculate_answer_completeness(query: str, answer: str) -> float:
    """Calculate how complete the answer is relative to the query"""
    try:
        # Extract question words and key terms
        question_words = extract_question_indicators(query)
        key_terms = extract_key_terms(query)
        
        completeness_indicators = []
        
        # Check if answer addresses question type
        if question_words:
            answer_addresses_type = any(
                check_question_type_addressed(qword, answer) 
                for qword in question_words
            )
            completeness_indicators.append(1.0 if answer_addresses_type else 0.5)
        
        # Check key term coverage
        if key_terms:
            covered_terms = sum(
                1 for term in key_terms 
                if term.lower() in answer.lower()
            )
            term_coverage = covered_terms / len(key_terms)
            completeness_indicators.append(term_coverage)
        
        # Answer length relative to query complexity
        query_complexity = estimate_query_complexity(query)
        length_appropriateness = min(1.0, len(answer.split()) / (query_complexity * 20))
        completeness_indicators.append(length_appropriateness)
        
        return sum(completeness_indicators) / len(completeness_indicators) if completeness_indicators else 0.5
        
    except Exception as e:
        logger.error(f"Answer completeness calculation failed: {e}")
        return 0.5

def calculate_query_answer_alignment(query: str, answer: str) -> float:
    """Calculate how well the answer aligns with the query"""
    try:
        # Normalize texts
        query_clean = clean_text_for_comparison(query)
        answer_clean = clean_text_for_comparison(answer)
        
        query_words = set(query_clean.split())
        answer_words = set(answer_clean.split())
        
        # Remove stop words
        stop_words = {
            'the', 'is', 'at', 'which', 'on', 'a', 'an', 'and', 'or', 'but',
            'in', 'with', 'to', 'for', 'of', 'as', 'by', 'that', 'this',
            'what', 'when', 'where', 'how', 'why', 'can', 'could', 'would'
        }
        
        query_words = query_words - stop_words
        answer_words = answer_words - stop_words
        
        if not query_words:
            return 0.5
        
        # Calculate overlap
        overlap = len(query_words & answer_words)
        alignment = overlap / len(query_words)
        
        # Bonus for semantic indicators
        semantic_bonus = 0.0
        if any(word in answer.lower() for word in ['therefore', 'because', 'since', 'due to']):
            semantic_bonus += 0.1
        
        return min(1.0, alignment + semantic_bonus)
        
    except Exception as e:
        logger.error(f"Query-answer alignment calculation failed: {e}")
        return 0.5

def calculate_answer_length_score(answer: str) -> float:
    """Calculate appropriateness of answer length"""
    try:
        word_count = len(answer.split())
        
        # Optimal range: 50-300 words
        if 50 <= word_count <= 300:
            return 1.0
        elif word_count < 50:
            # Too short
            return word_count / 50.0
        else:
            # Too long - gradual penalty
            return max(0.3, 300.0 / word_count)
            
    except Exception as e:
        logger.error(f"Answer length score calculation failed: {e}")
        return 0.5

def extract_question_indicators(query: str) -> List[str]:
    """Extract question words and indicators"""
    try:
        question_words = []
        query_lower = query.lower()
        
        # Direct question words
        direct_questions = ['what', 'why', 'how', 'when', 'where', 'who', 'which']
        for word in direct_questions:
            if word in query_lower:
                question_words.append(word)
        
        # Question patterns
        if re.search(r'\bexplain\b', query_lower):
            question_words.append('explain')
        if re.search(r'\bdefine\b', query_lower):
            question_words.append('define')
        if re.search(r'\bdescribe\b', query_lower):
            question_words.append('describe')
        if re.search(r'\bcompare\b', query_lower):
            question_words.append('compare')
        
        return question_words
        
    except Exception as e:
        logger.error(f"Question indicator extraction failed: {e}")
        return []

def extract_key_terms(query: str) -> List[str]:
    """Extract key terms from query"""
    try:
        # Simple keyword extraction
        # In a real implementation, this could use NLP libraries
        
        words = query.lower().split()
        
        # Remove common words and keep important terms
        stop_words = {
            'the', 'is', 'at', 'which', 'on', 'a', 'an', 'and', 'or', 'but',
            'in', 'with', 'to', 'for', 'of', 'as', 'by', 'that', 'this',
            'what', 'when', 'where', 'how', 'why', 'can', 'could', 'would',
            'please', 'tell', 'me', 'about'
        }
        
        # Keep words that are likely to be important
        key_terms = []
        for word in words:
            word_clean = re.sub(r'[^\w]', '', word)
            if (len(word_clean) > 3 and 
                word_clean not in stop_words and
                not word_clean.isdigit()):
                key_terms.append(word_clean)
        
        return key_terms
        
    except Exception as e:
        logger.error(f"Key term extraction failed: {e}")
        return []

def check_question_type_addressed(question_word: str, answer: str) -> bool:
    """Check if the answer addresses the type of question asked"""
    try:
        answer_lower = answer.lower()
        
        if question_word == 'what':
            # Look for definitions, descriptions
            return any(phrase in answer_lower for phrase in [
                'is', 'are', 'refers to', 'means', 'definition', 'type of'
            ])
        
        elif question_word == 'why':
            # Look for causal explanations
            return any(phrase in answer_lower for phrase in [
                'because', 'due to', 'since', 'reason', 'cause', 'result'
            ])
        
        elif question_word == 'how':
            # Look for process or method descriptions
            return any(phrase in answer_lower for phrase in [
                'by', 'through', 'process', 'method', 'way', 'step', 'procedure'
            ])
        
        elif question_word == 'when':
            # Look for temporal information
            return any(phrase in answer_lower for phrase in [
                'during', 'after', 'before', 'time', 'period', 'year', 'century'
            ])
        
        elif question_word == 'where':
            # Look for location information
            return any(phrase in answer_lower for phrase in [
                'in', 'at', 'location', 'place', 'region', 'area', 'country'
            ])
        
        else:
            return True  # Default case
            
    except Exception as e:
        logger.error(f"Question type check failed: {e}")
        return False

def estimate_query_complexity(query: str) -> int:
    """Estimate the complexity of a query (1-5 scale)"""
    try:
        factors = []
        
        # Length factor
        word_count = len(query.split())
        if word_count > 20:
            factors.append(3)
        elif word_count > 10:
            factors.append(2)
        else:
            factors.append(1)
        
        # Question type factor
        query_lower = query.lower()
        if any(word in query_lower for word in ['compare', 'analyze', 'evaluate']):
            factors.append(4)
        elif any(word in query_lower for word in ['explain', 'describe', 'discuss']):
            factors.append(3)
        elif any(word in query_lower for word in ['what', 'define']):
            factors.append(2)
        else:
            factors.append(1)
        
        # Multiple concepts factor
        concept_indicators = ['and', 'or', 'versus', 'vs', 'between']
        if any(indicator in query_lower for indicator in concept_indicators):
            factors.append(3)
        else:
            factors.append(1)
        
        # Return average, capped at 5
        return min(5, int(sum(factors) / len(factors)))
        
    except Exception as e:
        logger.error(f"Query complexity estimation failed: {e}")
        return 2

def clean_text_for_comparison(text: str) -> str:
    """Clean text for comparison purposes"""
    try:
        # Remove punctuation and normalize
        text = re.sub(r'[^\w\s]', '', text.lower())
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
        
    except Exception as e:
        logger.error(f"Text cleaning failed: {e}")
        return text.lower()

def calculate_retrieval_metrics(
    retrieved_docs: List[Dict[str, Any]],
    relevant_docs: List[str],
    top_k: int = 5
) -> Dict[str, float]:
    """Calculate retrieval evaluation metrics"""
    try:
        retrieved_ids = [doc.get('id', '') for doc in retrieved_docs[:top_k]]
        relevant_set = set(relevant_docs)
        retrieved_set = set(retrieved_ids)
        
        # Precision
        if retrieved_set:
            precision = len(relevant_set & retrieved_set) / len(retrieved_set)
        else:
            precision = 0.0
        
        # Recall
        if relevant_set:
            recall = len(relevant_set & retrieved_set) / len(relevant_set)
        else:
            recall = 0.0
        
        # F1 Score
        if precision + recall > 0:
            f1 = 2 * (precision * recall) / (precision + recall)
        else:
            f1 = 0.0
        
        return {
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'retrieved_count': len(retrieved_set),
            'relevant_count': len(relevant_set)
        }
        
    except Exception as e:
        logger.error(f"Retrieval metrics calculation failed: {e}")
        return {
            'precision': 0.0,
            'recall': 0.0,
            'f1_score': 0.0,
            'retrieved_count': 0,
            'relevant_count': 0
        }