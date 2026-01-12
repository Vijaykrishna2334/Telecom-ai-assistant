"""
CRAG Chain - Corrective Retrieval-Augmented Generation.

This is the main RAG orchestrator implementing the 2024 CRAG paper methodology:
1. Retrieve documents (using HYBRID search - vector + BM25 with RRF fusion)
2. Grade relevance (CRAG-specific)
3. Decision gate:
   - CORRECT → Use documents for generation
   - AMBIGUOUS → Refine and re-retrieve
   - INCORRECT → Fallback response (escalate)

Reference: "Corrective Retrieval Augmented Generation" (2024)
https://arxiv.org/abs/2401.15884
"""
from typing import List, Optional, Dict, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import re

from app.core.logging import get_logger
from app.services.rag.hybrid_retriever import hybrid_retriever
from app.services.rag.relevance_grader import relevance_grader, RelevanceGrade
from app.services.rag.embeddings import embedding_service

logger = get_logger(__name__)


class CRAGAction(Enum):
    """Actions the CRAG chain can take."""
    USE_CONTEXT = "use_context"      # Use retrieved docs as context
    REFINE_QUERY = "refine_query"    # Refine query and re-retrieve
    FALLBACK = "fallback"            # No good context, use fallback


@dataclass
class CRAGResult:
    """Result from CRAG chain processing."""
    action: CRAGAction
    context: str
    documents: List[Dict[str, Any]]
    relevance_scores: List[float]
    query_used: str
    fallback_message: Optional[str] = None


class CRAGChain:
    """
    Corrective RAG Chain - The latest 2024 RAG methodology.
    
    Key features:
    - Relevance grading before generation (prevents hallucination)
    - Query refinement for ambiguous results
    - Graceful fallback when no relevant context found
    """

    def __init__(
        self,
        top_k: int = 5,
        max_context_length: int = 2000,
        max_refinement_attempts: int = 1,
    ):
        """
        Initialize CRAG chain.

        Args:
            top_k: Number of documents to retrieve
            max_context_length: Maximum context length for LLM
            max_refinement_attempts: Max query refinement attempts
        """
        self.top_k = top_k
        self.max_context_length = max_context_length
        self.max_refinement_attempts = max_refinement_attempts
        
        self.retriever = hybrid_retriever
        self.grader = relevance_grader
        
        # Fallback message when no relevant docs found
        self.fallback_message = (
            "I don't have specific information about that in my knowledge base. "
            "For accurate assistance, please call our helpline at 1800-88-99999 "
            "or visit your nearest Jio Store."
        )
        
        logger.info(
            "CRAG Chain initialized with HYBRID search (vector + BM25)",
            top_k=top_k,
            max_context=max_context_length
        )

    async def process(self, query: str, conversation_history: list = None) -> CRAGResult:
        """
        Process a query through the CRAG pipeline.

        Args:
            query: User query
            conversation_history: Previous messages for context-aware expansion

        Returns:
            CRAGResult with context and action
        """
        logger.info("CRAG processing query", query=query[:100])
        
        # Step 0: Smart query expansion based on intent AND conversation history
        expanded_query = self._expand_query_by_intent(query, conversation_history)
        
        # Step 1: Retrieve documents
        documents = await self.retriever.retrieve(expanded_query, self.top_k)
        
        if not documents:
            logger.info("No documents retrieved, using fallback")
            return CRAGResult(
                action=CRAGAction.FALLBACK,
                context="",
                documents=[],
                relevance_scores=[],
                query_used=query,
                fallback_message=self.fallback_message
            )
        
        # Step 2: Grade document relevance (CRAG core feature)
        graded_docs = await self.grader.grade_documents(query, documents)
        decision, relevant_graded = self.grader.decision(graded_docs)
        
        # Convert GradedDocument objects to dicts for context building
        relevant_docs = [{"text": g.text, "metadata": g.metadata, "score": g.relevance_score} for g in relevant_graded]
        
        # Extract scores for logging
        scores = [g.relevance_score for g in graded_docs]
        
        # Step 3: Decision gate
        if decision == "USE_CONTEXT":
            # Documents are relevant - use them
            context = self._build_context(relevant_docs)
            return CRAGResult(
                action=CRAGAction.USE_CONTEXT,
                context=context,
                documents=relevant_docs,
                relevance_scores=scores,
                query_used=query
            )
        
        elif decision == "REFINE_QUERY":
            # Try query refinement once
            refined_result = await self._try_refinement(query, graded_docs)
            if refined_result:
                return refined_result
            
            # Use ambiguous docs with lower confidence
            context = self._build_context(relevant_docs)
            return CRAGResult(
                action=CRAGAction.USE_CONTEXT,
                context=context,
                documents=relevant_docs,
                relevance_scores=scores,
                query_used=query
            )
        
        else:  # INCORRECT
            # No relevant documents found
            logger.info("CRAG: No relevant documents, using fallback")
            return CRAGResult(
                action=CRAGAction.FALLBACK,
                context="",
                documents=[],
                relevance_scores=scores,
                query_used=query,
                fallback_message=self.fallback_message
            )

    async def _try_refinement(
        self, 
        original_query: str,
        graded_docs: List[Tuple]
    ) -> Optional[CRAGResult]:
        """
        Try to refine the query for better retrieval.
        
        This is a simplified refinement - in production could use LLM to rewrite query.
        """
        # Simple refinement: expand query with keywords from ambiguous docs
        ambiguous_texts = [
            g.text[:100] 
            for g in graded_docs 
            if g.grade == RelevanceGrade.AMBIGUOUS
        ]
        
        if not ambiguous_texts:
            return None
        
        # Extract potential keywords (simplified)
        keywords = self._extract_keywords(ambiguous_texts[0])
        if not keywords:
            return None
        
        # Expand query
        refined_query = f"{original_query} {' '.join(keywords[:3])}"
        logger.info("CRAG: Attempting query refinement", refined=refined_query[:100])
        
        # Re-retrieve with refined query
        documents = await self.retriever.retrieve(refined_query, self.top_k)
        if not documents:
            return None
        
        # Re-grade
        graded = await self.grader.grade_documents(refined_query, documents)
        decision, relevant_graded = self.grader.decision(graded)
        
        if decision == "USE_CONTEXT":
            relevant = [{"text": g.text, "metadata": g.metadata, "score": g.relevance_score} for g in relevant_graded]
            context = self._build_context(relevant)
            scores = [g.relevance_score for g in graded]
            return CRAGResult(
                action=CRAGAction.USE_CONTEXT,
                context=context,
                documents=relevant,
                relevance_scores=scores,
                query_used=refined_query
            )
        
        return None

    def _expand_query_by_intent(self, query: str, conversation_history: list = None) -> str:
        """
        Expand query based on detected user intent (mobile vs fiber vs airfiber).
        Also checks conversation history to understand context from previous messages.
        This helps RAG retrieve the correct type of plans.
        """
        query_lower = query.lower()
        
        # FIRST: Check conversation history for context
        # This is crucial for follow-up queries like "any OTT plans with it"
        history_context = self._extract_context_from_history(conversation_history)
        
        # Detect explicit postpaid intent
        postpaid_keywords = ['postpaid', 'post paid', 'post-paid', 'monthly bill']
        is_postpaid = any(kw in query_lower for kw in postpaid_keywords)
        
        # Detect prepaid/recharge intent (default for mobile)
        prepaid_keywords = ['prepaid', 'recharge', 'top up', 'topup', 'validity', 
                           'data pack', '28 days', '56 days', '84 days', '90 days',
                           'best plan', 'basic plan', 'cheap plan', 'affordable',
                           'recommend', 'suggest', 'give me', 'tell me plan',
                           'unlimited call', 'unlimited data', 'daily data']
        is_prepaid = any(kw in query_lower for kw in prepaid_keywords)
        
        # Detect general mobile intent
        mobile_keywords = ['mobile', 'phone', 'sim', 'calling', '4g', '5g', 'talk time',
                          'sms', 'daily data', 'gb per day', 'gb/day', 'mobile plan',
                          'jio plan', 'data plan', 'monthly plan', 'recharge plan',
                          'voice call', 'call plan', 'unlimited', '₹', 'rupee', 'rs']
        is_mobile = any(kw in query_lower for kw in mobile_keywords)
        
        # Detect fiber intent  
        fiber_keywords = ['fiber', 'jiofiber', 'broadband', 'wifi', 'router', 'mbps', 
                         'gbps', 'home internet', 'ott', 'netflix', 'prime video']
        is_fiber = any(kw in query_lower for kw in fiber_keywords)
        
        # Detect airfiber intent
        airfiber_keywords = ['airfiber', 'air fiber', '5g home', 'wireless broadband']
        is_airfiber = any(kw in query_lower for kw in airfiber_keywords)
        
        # Detect price range queries (e.g., "500 to 700 range", "between 300 and 500")
        price_range_pattern = r'\b(\d{2,4})\s*(?:to|and|-)\s*(\d{2,4})\b'
        has_price_range = re.search(price_range_pattern, query_lower)
        
        # Expand query based on intent
        if is_postpaid:
            expansion = " jio postpaid monthly bill"
            logger.info("Query intent: POSTPAID", original=query[:50])
        elif is_airfiber:
            expansion = " jioairfiber 5g wireless"
            logger.info("Query intent: AIRFIBER", original=query[:50])
        elif is_prepaid or (is_mobile and not is_fiber and not is_airfiber):
            # Prepaid is default for mobile queries
            expansion = " jio mobile prepaid recharge plan"
            logger.info("Query intent: MOBILE PREPAID", original=query[:50])
        elif is_fiber and not is_mobile:
            expansion = " jiofiber broadband home internet"
            logger.info("Query intent: FIBER", original=query[:50])
        elif has_price_range:
            # Price range queries - assume prepaid mobile unless history says otherwise
            if history_context == "airfiber":
                expansion = " jioairfiber 5g wireless price"
            elif history_context == "fiber":
                expansion = " jiofiber broadband price"
            else:
                expansion = " jio mobile prepaid recharge plan price"
            logger.info("Query intent: PRICE RANGE", original=query[:50])
        elif history_context:
            # Use context from conversation history for ambiguous queries
            if history_context == "airfiber":
                expansion = " jioairfiber 5g wireless"
                logger.info("Query intent: AIRFIBER (from history)", original=query[:50])
            elif history_context == "fiber":
                expansion = " jiofiber broadband home internet"
                logger.info("Query intent: FIBER (from history)", original=query[:50])
            elif history_context == "mobile":
                expansion = " jio mobile prepaid recharge plan"
                logger.info("Query intent: MOBILE (from history)", original=query[:50])
            else:
                expansion = ""
        else:
            # Check for common prepaid price ranges
            if any(word in query_lower for word in ['₹199', '₹249', '₹299', '₹349', '₹479', '₹579', '₹899']):
                expansion = " jio mobile prepaid"
            elif any(word in query_lower for word in ['plan', 'plans', 'recharge', 'known', 'know']):
                # Generic plan query - default to PREPAID (more common)
                expansion = " jio mobile prepaid recharge plan"
                logger.info("Query intent: DEFAULT PREPAID", original=query[:50])
            else:
                expansion = ""
        
        return query + expansion
    
    def _extract_context_from_history(self, conversation_history: list) -> str:
        """
        Extract the topic context from recent conversation history.
        Returns: 'airfiber', 'fiber', 'mobile', or None
        """
        if not conversation_history:
            return None
        
        # Check last few messages (up to 6) for context
        recent_msgs = conversation_history[-6:] if len(conversation_history) > 6 else conversation_history
        history_text = " ".join([msg.get("content", "") for msg in recent_msgs]).lower()
        
        # Priority: Check for AirFiber first (more specific)
        airfiber_indicators = ['airfiber', 'air fiber', 'jioairfiber', '5g home', 'wireless broadband', '5g antenna']
        if any(kw in history_text for kw in airfiber_indicators):
            logger.info("History context detected: AIRFIBER")
            return "airfiber"
        
        # Then check for regular Fiber
        fiber_indicators = ['jiofiber', 'fiber', 'broadband', 'home internet', 'router']
        if any(kw in history_text for kw in fiber_indicators):
            logger.info("History context detected: FIBER")
            return "fiber"
        
        # Then check for Mobile
        mobile_indicators = ['mobile', 'recharge', 'prepaid', 'postpaid', 'sim', '4g', '5g data']
        if any(kw in history_text for kw in mobile_indicators):
            logger.info("History context detected: MOBILE")
            return "mobile"
        
        return None


    def _extract_keywords(self, text: str) -> List[str]:
        """Extract potential keywords from text (simplified)."""
        # Remove common words
        stopwords = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 
                     'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
                     'would', 'could', 'should', 'may', 'might', 'must', 'shall',
                     'can', 'to', 'of', 'in', 'for', 'on', 'with', 'at', 'by',
                     'from', 'as', 'into', 'through', 'during', 'before', 'after',
                     'above', 'below', 'between', 'under', 'again', 'further',
                     'then', 'once', 'here', 'there', 'when', 'where', 'why',
                     'how', 'all', 'each', 'few', 'more', 'most', 'other', 'some',
                     'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so',
                     'than', 'too', 'very', 'just', 'and', 'but', 'if', 'or',
                     'because', 'until', 'while', 'this', 'that', 'these', 'those',
                     'i', 'you', 'he', 'she', 'it', 'we', 'they', 'what', 'which'}
        
        words = text.lower().split()
        keywords = [w for w in words if w.isalnum() and w not in stopwords and len(w) > 2]
        return keywords[:5]

    def _build_context(self, documents: List[Dict[str, Any]]) -> str:
        """Build context string from documents."""
        context_parts = []
        current_length = 0
        
        for doc in documents:
            text = doc.get("text", "")
            source = doc.get("metadata", {}).get("source", "unknown")
            
            # Add source attribution
            chunk = f"[Source: {source}]\n{text}"
            
            if current_length + len(chunk) <= self.max_context_length:
                context_parts.append(chunk)
                current_length += len(chunk)
            else:
                # Add partial if meaningful
                remaining = self.max_context_length - current_length
                if remaining > 100:
                    context_parts.append(chunk[:remaining] + "...")
                break
        
        return "\n\n---\n\n".join(context_parts)

    async def get_context_for_query(self, query: str) -> str:
        """
        Convenience method: Get context string for a query.
        Compatible with existing knowledge_base interface.
        """
        result = await self.process(query)
        
        if result.action == CRAGAction.FALLBACK:
            # Return fallback message as context
            return f"[NOTICE: {result.fallback_message}]"
        
        return result.context


# Global CRAG chain instance
crag_chain = CRAGChain()
