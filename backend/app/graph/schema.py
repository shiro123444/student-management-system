"""
Knowledge graph schema definitions
"""

from typing import Dict, List, Any, Optional
from enum import Enum
from datetime import datetime

class NodeType(str, Enum):
    """Supported node types in the knowledge graph"""
    CONCEPT = "Concept"
    DOCUMENT = "Document"
    QUESTION = "Question"
    ANSWER = "Answer"
    LEARNING_PATH = "LearningPath"
    SESSION = "Session"

class RelationshipType(str, Enum):
    """Supported relationship types"""
    # Content relationships
    EXPLAINS = "EXPLAINS"
    CONTAINS = "CONTAINS"
    CITES = "CITES"
    REFERENCES = "REFERENCES"
    
    # Conceptual relationships
    PREREQUISITE = "PREREQUISITE"
    RELATES_TO = "RELATES_TO"
    PART_OF = "PART_OF"
    INSTANCE_OF = "INSTANCE_OF"
    
    # Learning relationships
    FOLLOWS = "FOLLOWS"
    INCLUDED_IN = "INCLUDED_IN"
    
    # Question-Answer relationships
    ASKS_ABOUT = "ASKS_ABOUT"
    ANSWERED_BY = "ANSWERED_BY"
    
    # Usage relationships
    QUERIED_ABOUT = "QUERIED_ABOUT"

class DifficultyLevel(str, Enum):
    """Learning difficulty levels"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class ContentType(str, Enum):
    """Types of educational content"""
    TEXTBOOK = "textbook"
    RESEARCH_PAPER = "research_paper"
    LECTURE_NOTES = "lecture_notes"
    VIDEO = "video"
    WIKI_ARTICLE = "wiki_article"
    TUTORIAL = "tutorial"
    EXERCISE = "exercise"

class QuestionType(str, Enum):
    """Types of questions"""
    DEFINITION = "definition"
    EXPLANATION = "explanation"
    COMPARISON = "comparison"
    PROCEDURE = "procedure"
    EXAMPLE = "example"
    APPLICATION = "application"

class GraphSchema:
    """Knowledge graph schema definitions and validation"""
    
    @staticmethod
    def get_node_schema(node_type: NodeType) -> Dict[str, Any]:
        """Get schema for a specific node type"""
        
        if node_type == NodeType.CONCEPT:
            return {
                "required_properties": ["name", "domain"],
                "optional_properties": [
                    "description", "difficulty_level", "prerequisites",
                    "learning_objectives", "synonyms", "importance_score"
                ],
                "property_types": {
                    "name": str,
                    "description": str,
                    "domain": str,
                    "difficulty_level": DifficultyLevel,
                    "prerequisites": list,
                    "learning_objectives": list,
                    "synonyms": list,
                    "importance_score": float
                }
            }
        
        elif node_type == NodeType.DOCUMENT:
            return {
                "required_properties": ["title", "content_type"],
                "optional_properties": [
                    "source_url", "authors", "publication_date", "language",
                    "quality_score", "word_count", "reading_level", "verified"
                ],
                "property_types": {
                    "title": str,
                    "content_type": ContentType,
                    "source_url": str,
                    "authors": list,
                    "publication_date": datetime,
                    "language": str,
                    "quality_score": float,
                    "word_count": int,
                    "reading_level": str,
                    "verified": bool
                }
            }
        
        elif node_type == NodeType.QUESTION:
            return {
                "required_properties": ["text", "question_type"],
                "optional_properties": [
                    "difficulty", "answer_quality_score", "frequency_asked", "language"
                ],
                "property_types": {
                    "text": str,
                    "question_type": QuestionType,
                    "difficulty": DifficultyLevel,
                    "answer_quality_score": float,
                    "frequency_asked": int,
                    "language": str
                }
            }
        
        elif node_type == NodeType.ANSWER:
            return {
                "required_properties": ["content"],
                "optional_properties": [
                    "confidence_score", "generated_by", "verified", "upvotes", "downvotes"
                ],
                "property_types": {
                    "content": str,
                    "confidence_score": float,
                    "generated_by": str,
                    "verified": bool,
                    "upvotes": int,
                    "downvotes": int
                }
            }
        
        elif node_type == NodeType.LEARNING_PATH:
            return {
                "required_properties": ["name", "description"],
                "optional_properties": [
                    "estimated_duration", "difficulty_progression", "completion_rate"
                ],
                "property_types": {
                    "name": str,
                    "description": str,
                    "estimated_duration": str,
                    "difficulty_progression": str,
                    "completion_rate": float
                }
            }
        
        elif node_type == NodeType.SESSION:
            return {
                "required_properties": ["user_id", "start_time"],
                "optional_properties": [
                    "last_activity", "query_count", "topics_explored"
                ],
                "property_types": {
                    "user_id": str,
                    "start_time": datetime,
                    "last_activity": datetime,
                    "query_count": int,
                    "topics_explored": list
                }
            }
        
        else:
            raise ValueError(f"Unknown node type: {node_type}")
    
    @staticmethod
    def get_relationship_schema(relationship_type: RelationshipType) -> Dict[str, Any]:
        """Get schema for a specific relationship type"""
        
        # Common properties for all relationships
        base_schema = {
            "optional_properties": ["created_at", "confidence", "weight"],
            "property_types": {
                "created_at": datetime,
                "confidence": float,
                "weight": float
            }
        }
        
        # Relationship-specific properties
        if relationship_type == RelationshipType.EXPLAINS:
            base_schema["optional_properties"].extend([
                "coverage_depth", "quality_score", "page_range"
            ])
            base_schema["property_types"].update({
                "coverage_depth": str,
                "quality_score": float,
                "page_range": str
            })
        
        elif relationship_type == RelationshipType.PREREQUISITE:
            base_schema["optional_properties"].extend([
                "importance", "estimated_study_time"
            ])
            base_schema["property_types"].update({
                "importance": float,
                "estimated_study_time": str
            })
        
        elif relationship_type == RelationshipType.RELATES_TO:
            base_schema["optional_properties"].extend([
                "relationship_nature", "strength"
            ])
            base_schema["property_types"].update({
                "relationship_nature": str,
                "strength": float
            })
        
        elif relationship_type == RelationshipType.FOLLOWS:
            base_schema["optional_properties"].extend([
                "sequence_order", "transition_difficulty"
            ])
            base_schema["property_types"].update({
                "sequence_order": int,
                "transition_difficulty": float
            })
        
        elif relationship_type == RelationshipType.REFERENCES:
            base_schema["optional_properties"].extend([
                "relevance", "quote_start", "quote_end"
            ])
            base_schema["property_types"].update({
                "relevance": float,
                "quote_start": int,
                "quote_end": int
            })
        
        return base_schema
    
    @staticmethod
    def validate_node(node_type: NodeType, properties: Dict[str, Any]) -> List[str]:
        """Validate node properties against schema"""
        errors = []
        schema = GraphSchema.get_node_schema(node_type)
        
        # Check required properties
        for prop in schema["required_properties"]:
            if prop not in properties:
                errors.append(f"Missing required property: {prop}")
        
        # Check property types
        for prop, value in properties.items():
            if prop in schema["property_types"]:
                expected_type = schema["property_types"][prop]
                
                # Handle enum types
                if isinstance(expected_type, type) and issubclass(expected_type, Enum):
                    if value not in [e.value for e in expected_type]:
                        errors.append(f"Invalid value for {prop}: {value}")
                
                # Handle basic types
                elif not isinstance(value, expected_type):
                    if expected_type == datetime and isinstance(value, str):
                        # Allow string datetime representations
                        try:
                            datetime.fromisoformat(value.replace('Z', '+00:00'))
                        except ValueError:
                            errors.append(f"Invalid datetime format for {prop}: {value}")
                    else:
                        errors.append(f"Invalid type for {prop}: expected {expected_type.__name__}, got {type(value).__name__}")
        
        return errors
    
    @staticmethod
    def validate_relationship(
        relationship_type: RelationshipType,
        source_type: NodeType,
        target_type: NodeType,
        properties: Dict[str, Any]
    ) -> List[str]:
        """Validate relationship properties and node type compatibility"""
        errors = []
        
        # Check relationship property schema
        schema = GraphSchema.get_relationship_schema(relationship_type)
        for prop, value in properties.items():
            if prop in schema["property_types"]:
                expected_type = schema["property_types"][prop]
                if not isinstance(value, expected_type):
                    errors.append(f"Invalid type for {prop}: expected {expected_type.__name__}")
        
        # Check node type compatibility
        valid_combinations = GraphSchema.get_valid_relationship_combinations()
        if relationship_type in valid_combinations:
            valid_pairs = valid_combinations[relationship_type]
            if (source_type, target_type) not in valid_pairs:
                errors.append(
                    f"Invalid node type combination for {relationship_type}: "
                    f"{source_type} -> {target_type}"
                )
        
        return errors
    
    @staticmethod
    def get_valid_relationship_combinations() -> Dict[RelationshipType, List[tuple]]:
        """Get valid source-target node type combinations for each relationship"""
        return {
            RelationshipType.EXPLAINS: [
                (NodeType.DOCUMENT, NodeType.CONCEPT)
            ],
            RelationshipType.CONTAINS: [
                (NodeType.DOCUMENT, NodeType.CONCEPT),
                (NodeType.LEARNING_PATH, NodeType.CONCEPT)
            ],
            RelationshipType.PREREQUISITE: [
                (NodeType.CONCEPT, NodeType.CONCEPT)
            ],
            RelationshipType.RELATES_TO: [
                (NodeType.CONCEPT, NodeType.CONCEPT)
            ],
            RelationshipType.PART_OF: [
                (NodeType.CONCEPT, NodeType.CONCEPT)
            ],
            RelationshipType.ASKS_ABOUT: [
                (NodeType.QUESTION, NodeType.CONCEPT)
            ],
            RelationshipType.ANSWERED_BY: [
                (NodeType.QUESTION, NodeType.ANSWER)
            ],
            RelationshipType.REFERENCES: [
                (NodeType.ANSWER, NodeType.DOCUMENT),
                (NodeType.QUESTION, NodeType.DOCUMENT)
            ],
            RelationshipType.FOLLOWS: [
                (NodeType.CONCEPT, NodeType.CONCEPT)
            ],
            RelationshipType.INCLUDED_IN: [
                (NodeType.CONCEPT, NodeType.LEARNING_PATH)
            ],
            RelationshipType.QUERIED_ABOUT: [
                (NodeType.SESSION, NodeType.CONCEPT)
            ]
        }
    
    @staticmethod
    def get_default_properties(node_type: NodeType) -> Dict[str, Any]:
        """Get default property values for a node type"""
        defaults = {
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        if node_type == NodeType.CONCEPT:
            defaults.update({
                "importance_score": 0.5,
                "difficulty_level": DifficultyLevel.INTERMEDIATE
            })
        
        elif node_type == NodeType.DOCUMENT:
            defaults.update({
                "quality_score": 0.5,
                "verified": False,
                "language": "en"
            })
        
        elif node_type == NodeType.QUESTION:
            defaults.update({
                "frequency_asked": 1,
                "language": "en"
            })
        
        elif node_type == NodeType.ANSWER:
            defaults.update({
                "confidence_score": 0.5,
                "verified": False,
                "upvotes": 0,
                "downvotes": 0
            })
        
        return defaults