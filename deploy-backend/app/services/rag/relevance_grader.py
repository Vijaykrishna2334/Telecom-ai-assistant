"""
CRAG Relevance Grader - Core component for Corrective RAG.
Grades the relevance of retrieved documents to prevent hallucination.
"""
from enum import Enum
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass

from app.core.logging import get_logger
from app.services.rag.embeddings import embedding_service

logger = get_logger(__name__)


class RelevanceGrade(Enum):
    """Relevance grades for CRAG decision making."""
    CORRECT = "correct"      # Document is relevant (score >= 0.6)
    AMBIGUOUS = "ambiguous"  # Document may be relevant (0.3 <= score < 0.6)
    INCORRECT = "incorrect"  # Document is not relevant (score < 0.3)


@dataclass
class GradedDocument:
    """A document with its relevance grade and score."""
    text: str
    metadata: Dict[str, Any]
    retrieval_score: float
    relevance_score: float
    grade: RelevanceGrade


class RelevanceGrader:
    """
    Grades the relevance of retrieved documents using embedding similarity.
    
    This is the core CRAG component that prevents hallucination by
    filtering out irrelevant documents before they reach the LLM.
    """

    def __init__(
        self,
        relevance_threshold: float = 0.6,
        ambiguous_threshold: float = 0.3,
    ):
        """
        Initialize the relevance grader.

        Args:
            relevance_threshold: Score >= this = CORRECT
            ambiguous_threshold: Score >= this but < relevance = AMBIGUOUS
        """
        self.relevance_threshold = relevance_threshold
        self.ambiguous_threshold = ambiguous_threshold
        logger.info(
            "Initializing relevance grader",
            relevance_threshold=relevance_threshold,
            ambiguous_threshold=ambiguous_threshold
        )

    async def grade_document(
        self,
        query: str,
        document: Dict[str, Any],
    ) -> GradedDocument:
        """
        Grade a single document's relevance to the query.

        Args:
            query: The user's query
            document: Retrieved document with text, metadata, score

        Returns:
            GradedDocument with relevance score and grade
        """
        text = document.get("text", "")
        retrieval_score = document.get("score", 0.0)
        
        try:
            # Compute semantic similarity between query and document
            relevance_score = await embedding_service.compute_similarity(query, text)
        except Exception as e:
            logger.warning("Similarity computation failed, using retrieval score", error=str(e))
            relevance_score = retrieval_score
        
        # Determine grade based on thresholds
        if relevance_score >= self.relevance_threshold:
            grade = RelevanceGrade.CORRECT
        elif relevance_score >= self.ambiguous_threshold:
            grade = RelevanceGrade.AMBIGUOUS
        else:
            grade = RelevanceGrade.INCORRECT
        
        return GradedDocument(
            text=text,
            metadata=document.get("metadata", {}),
            retrieval_score=retrieval_score,
            relevance_score=relevance_score,
            grade=grade,
        )

    async def grade_documents(
        self,
        query: str,
        documents: List[Dict[str, Any]],
    ) -> List[GradedDocument]:
        """
        Grade multiple documents for relevance.

        Args:
            query: The user's query
            documents: List of retrieved documents

        Returns:
            List of GradedDocuments sorted by relevance score
        """
        graded = []
        for doc in documents:
            graded_doc = await self.grade_document(query, doc)
            graded.append(graded_doc)
        
        # Sort by relevance score (highest first)
        graded.sort(key=lambda x: x.relevance_score, reverse=True)
        
        # Log grading results
        correct = sum(1 for g in graded if g.grade == RelevanceGrade.CORRECT)
        ambiguous = sum(1 for g in graded if g.grade == RelevanceGrade.AMBIGUOUS)
        incorrect = sum(1 for g in graded if g.grade == RelevanceGrade.INCORRECT)
        
        logger.info(
            "Graded documents",
            total=len(graded),
            correct=correct,
            ambiguous=ambiguous,
            incorrect=incorrect
        )
        
        return graded

    def decision(
        self,
        graded_documents: List[GradedDocument],
    ) -> Tuple[str, List[GradedDocument]]:
        """
        Make a CRAG decision based on graded documents.

        Returns:
            Tuple of (action, filtered_documents)
            - action: "USE_CONTEXT" | "REFINE_QUERY" | "FALLBACK"
            - filtered_documents: Only CORRECT and AMBIGUOUS documents
        """
        if not graded_documents:
            return "FALLBACK", []
        
        correct_docs = [d for d in graded_documents if d.grade == RelevanceGrade.CORRECT]
        ambiguous_docs = [d for d in graded_documents if d.grade == RelevanceGrade.AMBIGUOUS]
        
        if correct_docs:
            # We have relevant documents - use them
            return "USE_CONTEXT", correct_docs + ambiguous_docs
        elif ambiguous_docs:
            # Only ambiguous - try to refine query or use with caution
            return "REFINE_QUERY", ambiguous_docs
        else:
            # No relevant documents - fallback to helpline
            return "FALLBACK", []


# Global relevance grader instance
relevance_grader = RelevanceGrader()
