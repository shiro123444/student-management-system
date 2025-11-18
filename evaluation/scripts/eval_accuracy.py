#!/usr/bin/env python3
"""
Educational QA Bot - Accuracy Evaluation Script

This script evaluates the accuracy and performance of the RAG pipeline
by running test queries and comparing responses against expected answers.
"""

import asyncio
import json
import sys
import time
from pathlib import Path
from typing import Dict, List, Any, Tuple
import logging

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent / "backend"))

from app.rag.pipeline import RAGPipeline
from app.utils.eval_helpers import calculate_confidence_score, calculate_retrieval_metrics
from app.core.config import settings

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EvaluationMetrics:
    """Container for evaluation metrics"""
    
    def __init__(self):
        self.total_queries = 0
        self.successful_responses = 0
        self.average_confidence = 0.0
        self.average_response_time = 0.0
        self.accuracy_scores = []
        self.retrieval_metrics = []
        self.error_count = 0
        
    def add_result(self, result: Dict[str, Any]):
        """Add a single evaluation result"""
        self.total_queries += 1
        
        if result.get("error"):
            self.error_count += 1
            return
            
        self.successful_responses += 1
        self.accuracy_scores.append(result.get("accuracy_score", 0.0))
        self.average_confidence += result.get("confidence_score", 0.0)
        self.average_response_time += result.get("response_time_ms", 0)
        
        if result.get("retrieval_metrics"):
            self.retrieval_metrics.append(result["retrieval_metrics"])
    
    def calculate_final_metrics(self) -> Dict[str, float]:
        """Calculate final aggregated metrics"""
        if self.successful_responses == 0:
            return {"error": "No successful responses"}
            
        return {
            "total_queries": self.total_queries,
            "success_rate": self.successful_responses / self.total_queries,
            "error_rate": self.error_count / self.total_queries,
            "average_accuracy": sum(self.accuracy_scores) / len(self.accuracy_scores),
            "average_confidence": self.average_confidence / self.successful_responses,
            "average_response_time_ms": self.average_response_time / self.successful_responses,
            "accuracy_std": self._calculate_std(self.accuracy_scores),
            "retrieval_precision": self._average_retrieval_metric("precision"),
            "retrieval_recall": self._average_retrieval_metric("recall"),
            "retrieval_f1": self._average_retrieval_metric("f1_score")
        }
    
    def _calculate_std(self, values: List[float]) -> float:
        """Calculate standard deviation"""
        if len(values) < 2:
            return 0.0
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / (len(values) - 1)
        return variance ** 0.5
    
    def _average_retrieval_metric(self, metric: str) -> float:
        """Calculate average of a retrieval metric"""
        if not self.retrieval_metrics:
            return 0.0
        values = [m.get(metric, 0.0) for m in self.retrieval_metrics]
        return sum(values) / len(values)

class AccuracyEvaluator:
    """Evaluates the accuracy of the RAG pipeline"""
    
    def __init__(self):
        self.rag_pipeline = RAGPipeline()
        self.test_cases = self._load_test_cases()
        
    def _load_test_cases(self) -> List[Dict[str, Any]]:
        """Load test cases from file or create default ones"""
        try:
            test_file = Path(__file__).parent / "test_cases.json"
            if test_file.exists():
                with open(test_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load test cases file: {e}")
        
        # Return default test cases
        return [
            {
                "query": "What is machine learning?",
                "expected_concepts": ["machine learning", "artificial intelligence", "algorithms"],
                "expected_answer_keywords": ["data", "pattern", "predict", "algorithm"],
                "difficulty": "beginner",
                "domain": "computer_science"
            },
            {
                "query": "Explain the difference between supervised and unsupervised learning",
                "expected_concepts": ["supervised learning", "unsupervised learning"],
                "expected_answer_keywords": ["labeled", "unlabeled", "training", "classification"],
                "difficulty": "intermediate",
                "domain": "computer_science"
            },
            {
                "query": "How does a neural network work?",
                "expected_concepts": ["neural network", "neurons", "weights", "activation"],
                "expected_answer_keywords": ["nodes", "layers", "weights", "activation", "backpropagation"],
                "difficulty": "intermediate",
                "domain": "computer_science"
            },
            {
                "query": "What is photosynthesis?",
                "expected_concepts": ["photosynthesis", "chlorophyll", "plants"],
                "expected_answer_keywords": ["sunlight", "carbon dioxide", "oxygen", "glucose"],
                "difficulty": "beginner",
                "domain": "biology"
            },
            {
                "query": "Explain Newton's second law of motion",
                "expected_concepts": ["newton's second law", "force", "acceleration", "mass"],
                "expected_answer_keywords": ["force", "mass", "acceleration", "F=ma"],
                "difficulty": "intermediate",
                "domain": "physics"
            }
        ]
    
    async def evaluate_single_query(
        self, 
        test_case: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Evaluate a single query"""
        query = test_case["query"]
        logger.info(f"Evaluating query: {query}")
        
        start_time = time.time()
        
        try:
            # Process query through RAG pipeline
            result = await self.rag_pipeline.process_query(
                query=query,
                session_id=f"eval_{int(time.time())}"
            )
            
            response_time = (time.time() - start_time) * 1000  # Convert to ms
            
            # Calculate accuracy metrics
            accuracy_score = self._calculate_accuracy(test_case, result)
            
            # Calculate retrieval metrics if expected concepts are provided
            retrieval_metrics = None
            if test_case.get("expected_concepts"):
                retrieval_metrics = self._calculate_retrieval_metrics(
                    test_case["expected_concepts"],
                    result.get("sources", [])
                )
            
            evaluation_result = {
                "query": query,
                "response": result.get("answer", ""),
                "confidence_score": result.get("confidence", 0.0),
                "response_time_ms": response_time,
                "accuracy_score": accuracy_score,
                "retrieval_metrics": retrieval_metrics,
                "sources_count": len(result.get("sources", [])),
                "processing_metadata": result.get("metadata", {}),
                "error": None
            }
            
            logger.info(f"Query evaluated - Accuracy: {accuracy_score:.2f}, Confidence: {result.get('confidence', 0):.2f}")
            return evaluation_result
            
        except Exception as e:
            logger.error(f"Error evaluating query '{query}': {e}")
            return {
                "query": query,
                "error": str(e),
                "response_time_ms": (time.time() - start_time) * 1000
            }
    
    def _calculate_accuracy(
        self, 
        test_case: Dict[str, Any], 
        result: Dict[str, Any]
    ) -> float:
        """Calculate accuracy score for a query result"""
        answer = result.get("answer", "").lower()
        expected_keywords = test_case.get("expected_answer_keywords", [])
        
        if not expected_keywords:
            return 0.5  # Default score when no expected keywords
        
        # Check keyword coverage
        keyword_matches = sum(
            1 for keyword in expected_keywords 
            if keyword.lower() in answer
        )
        keyword_coverage = keyword_matches / len(expected_keywords)
        
        # Check response completeness
        response_length_score = min(1.0, len(answer.split()) / 50)  # Expect ~50 words
        
        # Check if response addresses the question type
        query_type_score = self._assess_query_type_match(
            test_case["query"], 
            answer
        )
        
        # Weighted combination
        accuracy = (
            keyword_coverage * 0.5 + 
            response_length_score * 0.2 + 
            query_type_score * 0.3
        )
        
        return min(1.0, accuracy)
    
    def _assess_query_type_match(self, query: str, answer: str) -> float:
        """Assess if the answer matches the query type"""
        query_lower = query.lower()
        answer_lower = answer.lower()
        
        # Definition questions
        if any(word in query_lower for word in ["what is", "define", "definition"]):
            if any(phrase in answer_lower for phrase in ["is", "refers to", "means"]):
                return 1.0
            return 0.5
        
        # Explanation questions
        elif any(word in query_lower for word in ["explain", "how", "why"]):
            if any(phrase in answer_lower for phrase in ["because", "by", "through", "process"]):
                return 1.0
            return 0.5
        
        # Comparison questions
        elif any(word in query_lower for word in ["difference", "compare", "versus"]):
            if any(phrase in answer_lower for phrase in ["while", "whereas", "different", "contrast"]):
                return 1.0
            return 0.5
        
        return 0.7  # Default for other question types
    
    def _calculate_retrieval_metrics(
        self, 
        expected_concepts: List[str], 
        retrieved_sources: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """Calculate retrieval metrics"""
        # Extract concepts from source metadata or titles
        retrieved_concepts = []
        for source in retrieved_sources:
            title = source.get("title", "").lower()
            metadata = source.get("metadata", {})
            
            # Check if expected concepts appear in source
            for concept in expected_concepts:
                if concept.lower() in title or concept.lower() in str(metadata):
                    retrieved_concepts.append(concept)
        
        return calculate_retrieval_metrics(
            retrieved_docs=[{"id": i} for i in range(len(retrieved_concepts))],
            relevant_docs=expected_concepts,
            top_k=len(retrieved_sources)
        )
    
    async def run_evaluation(self) -> Dict[str, Any]:
        """Run full evaluation on all test cases"""
        logger.info(f"Starting evaluation with {len(self.test_cases)} test cases")
        
        metrics = EvaluationMetrics()
        detailed_results = []
        
        for i, test_case in enumerate(self.test_cases, 1):
            logger.info(f"Running test case {i}/{len(self.test_cases)}")
            
            result = await self.evaluate_single_query(test_case)
            metrics.add_result(result)
            detailed_results.append(result)
            
            # Add delay between queries to avoid overwhelming the system
            await asyncio.sleep(1)
        
        final_metrics = metrics.calculate_final_metrics()
        
        return {
            "evaluation_summary": final_metrics,
            "detailed_results": detailed_results,
            "test_cases_count": len(self.test_cases),
            "timestamp": time.time()
        }
    
    def save_results(self, results: Dict[str, Any], output_file: str = None):
        """Save evaluation results to file"""
        if not output_file:
            timestamp = int(time.time())
            output_file = f"evaluation_results_{timestamp}.json"
        
        output_path = Path(__file__).parent / output_file
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Results saved to: {output_path}")

async def main():
    """Main evaluation function"""
    evaluator = AccuracyEvaluator()
    
    try:
        # Run evaluation
        results = await evaluator.run_evaluation()
        
        # Display summary
        summary = results["evaluation_summary"]
        print("\n" + "="*50)
        print("EVALUATION SUMMARY")
        print("="*50)
        print(f"Total Queries: {summary['total_queries']}")
        print(f"Success Rate: {summary['success_rate']:.2%}")
        print(f"Average Accuracy: {summary['average_accuracy']:.2f}")
        print(f"Average Confidence: {summary['average_confidence']:.2f}")
        print(f"Average Response Time: {summary['average_response_time_ms']:.0f}ms")
        print(f"Retrieval Precision: {summary['retrieval_precision']:.2f}")
        print(f"Retrieval Recall: {summary['retrieval_recall']:.2f}")
        print("="*50)
        
        # Save detailed results
        evaluator.save_results(results)
        
        # Print individual results
        print("\nDETAILED RESULTS:")
        for i, result in enumerate(results["detailed_results"], 1):
            print(f"\n{i}. Query: {result['query']}")
            if result.get("error"):
                print(f"   Error: {result['error']}")
            else:
                print(f"   Accuracy: {result['accuracy_score']:.2f}")
                print(f"   Confidence: {result['confidence_score']:.2f}")
                print(f"   Response Time: {result['response_time_ms']:.0f}ms")
                print(f"   Sources: {result['sources_count']}")
        
    except Exception as e:
        logger.error(f"Evaluation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())