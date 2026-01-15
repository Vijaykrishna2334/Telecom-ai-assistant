"""
Hybrid Retriever - Combines Vector and BM25 search with RRF fusion.

This module implements hybrid search, merging results from:
- Semantic vector search (ChromaDB) - good for meaning/intent
- BM25 lexical search - good for exact terms/keywords

Uses Reciprocal Rank Fusion (RRF) to merge and re-rank results.
Reference: "Reciprocal Rank Fusion outperforms Condorcet and individual Rank Learning Methods" (2009)
"""
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict

from app.core.logging import get_logger
from app.services.rag.retriever import retriever_service
from app.services.rag.bm25_search import bm25_service

logger = get_logger(__name__)

# RRF constant - higher values give more weight to top-ranked documents
RRF_K = 60


def reciprocal_rank_fusion(
    rankings: List[List[Tuple[str, Dict[str, Any]]]],
    k: int = RRF_K
) -> List[Dict[str, Any]]:
    """
    Merge multiple rankings using Reciprocal Rank Fusion.

    RRF Score = Σ(1 / (k + rank_i))
    where rank_i is the rank of document in ranking i (1-indexed)

    Args:
        rankings: List of ranked result lists, each containing (doc_id, doc) tuples
        k: RRF constant (default 60)

    Returns:
        Merged and re-ranked list of documents with RRF scores
    """
    rrf_scores: Dict[str, float] = defaultdict(float)
    doc_map: Dict[str, Dict[str, Any]] = {}

    for ranking in rankings:
        for rank, (doc_id, doc) in enumerate(ranking, start=1):
            rrf_scores[doc_id] += 1 / (k + rank)
            if doc_id not in doc_map:
                doc_map[doc_id] = doc.copy()

    # Sort by RRF score (descending)
    sorted_ids = sorted(rrf_scores.keys(), key=lambda x: rrf_scores[x], reverse=True)

    # Build final results with RRF scores
    results = []
    for doc_id in sorted_ids:
        doc = doc_map[doc_id]
        doc["rrf_score"] = rrf_scores[doc_id]
        results.append(doc)

    return results


def _get_doc_id(doc: Dict[str, Any], index: int) -> str:
    """Generate a unique ID for a document."""
    # Use text hash as ID for deduplication
    text = doc.get("text", "")
    return str(hash(text[:200]))  # Use first 200 chars for hashing


class HybridRetriever:
    """
    Hybrid retriever combining vector and BM25 search.

    Pipeline:
    1. Run vector search (semantic)
    2. Run BM25 search (lexical)
    3. Merge with RRF
    4. Return top-k results
    """

    def __init__(
        self,
        vector_weight: float = 0.5,  # Not used in RRF but kept for future
        bm25_weight: float = 0.5,
        rrf_k: int = RRF_K,
    ):
        """
        Initialize hybrid retriever.

        Args:
            vector_weight: Weight for vector results (future use)
            bm25_weight: Weight for BM25 results (future use)
            rrf_k: RRF constant
        """
        self.vector_retriever = retriever_service
        self.bm25_service = bm25_service
        self.rrf_k = rrf_k
        self._bm25_initialized = False
        
        logger.info("Hybrid retriever initialized", rrf_k=rrf_k)

    async def initialize(self) -> None:
        """Initialize the hybrid retriever (build BM25 index)."""
        await self._ensure_bm25_index()

    async def _ensure_bm25_index(self) -> None:
        """Ensure BM25 index is built from vector store documents."""
        if self._bm25_initialized and self.bm25_service.is_initialized:
            return

        try:
            # Get all documents from vector store
            docs = await self.vector_retriever.get_all_documents()
            
            if docs:
                await self.bm25_service.build_index(docs)
                self._bm25_initialized = True
                logger.info("BM25 index initialized from vector store", doc_count=len(docs))
            else:
                logger.warning("No documents in vector store for BM25 indexing")
                
        except Exception as e:
            logger.error("Failed to initialize BM25 index", error=str(e))
            # Continue without BM25 - fall back to vector-only

    async def retrieve(
        self,
        query: str,
        top_k: int = 5,
        vector_top_k: int = 10,
        bm25_top_k: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Hybrid retrieval combining vector and BM25 search.

        Args:
            query: Search query
            top_k: Final number of results to return
            vector_top_k: Number of vector search results to consider
            bm25_top_k: Number of BM25 results to consider

        Returns:
            Merged and re-ranked list of documents
        """
        logger.info("Hybrid retrieval starting", query=query[:50])

        # Ensure BM25 is initialized
        await self._ensure_bm25_index()

        rankings = []

        # 1. Vector search (semantic)
        try:
            vector_results = await self.vector_retriever.retrieve(query, vector_top_k)
            if vector_results:
                vector_ranking = [
                    (_get_doc_id(doc, i), doc)
                    for i, doc in enumerate(vector_results)
                ]
                rankings.append(vector_ranking)
                logger.debug("Vector search returned results", count=len(vector_results))
        except Exception as e:
            logger.error("Vector search failed", error=str(e))

        # 2. BM25 search (lexical)
        if self.bm25_service.is_initialized:
            try:
                bm25_results = await self.bm25_service.search(query, bm25_top_k)
                if bm25_results:
                    bm25_ranking = [
                        (_get_doc_id(doc, i), doc)
                        for i, doc in enumerate(bm25_results)
                    ]
                    rankings.append(bm25_ranking)
                    logger.debug("BM25 search returned results", count=len(bm25_results))
            except Exception as e:
                logger.error("BM25 search failed", error=str(e))
        else:
            logger.warning("BM25 not initialized, using vector-only search")

        # 3. Merge with RRF
        if not rankings:
            logger.warning("No results from any search method")
            return []

        if len(rankings) == 1:
            # Only one method returned results
            merged = [doc for _, doc in rankings[0]]
        else:
            # Merge with RRF
            merged = reciprocal_rank_fusion(rankings, k=self.rrf_k)

        # 4. Return top-k
        results = merged[:top_k]

        logger.info(
            "Hybrid retrieval completed",
            query=query[:50],
            total_candidates=sum(len(r) for r in rankings),
            final_results=len(results),
            methods_used=len(rankings)
        )

        return results

    async def rebuild_bm25_index(self) -> None:
        """Force rebuild of BM25 index (call after adding new documents)."""
        self._bm25_initialized = False
        await self._ensure_bm25_index()


# Global hybrid retriever instance
hybrid_retriever = HybridRetriever()
