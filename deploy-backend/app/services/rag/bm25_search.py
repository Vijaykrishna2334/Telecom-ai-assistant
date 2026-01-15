"""
BM25 Lexical Search Service.

Provides keyword-based search using BM25 algorithm to complement
semantic vector search. Part of the hybrid search system.

BM25 excels at:
- Exact term matches (e.g., "₹299", "JioFiber")
- Rare keyword matching
- Specific product names and codes
"""
from typing import List, Dict, Any, Optional
import re

from app.core.logging import get_logger

logger = get_logger(__name__)

# Lazy import to avoid startup issues
_bm25_index = None
_corpus = None
_documents = None


def _tokenize(text: str) -> List[str]:
    """
    Simple tokenizer for BM25.
    Handles special characters like ₹, maintains numbers and prices.
    """
    # Convert to lowercase
    text = text.lower()
    
    # Keep rupee symbol attached to numbers (₹299 -> ₹299)
    # Split on whitespace and punctuation but keep important chars
    tokens = re.findall(r'₹?\d+(?:\.\d+)?|\w+', text)
    
    # Filter very short tokens except numbers/prices
    tokens = [t for t in tokens if len(t) > 1 or t.startswith('₹') or t.isdigit()]
    
    return tokens


class BM25SearchService:
    """
    BM25 search service for lexical/keyword search.
    
    Maintains an in-memory BM25 index built from document corpus.
    Works alongside vector search for hybrid retrieval.
    """

    def __init__(self):
        """Initialize BM25 search service."""
        self.bm25 = None
        self.corpus: List[List[str]] = []  # Tokenized documents
        self.documents: List[Dict[str, Any]] = []  # Original documents
        self._initialized = False
        logger.info("BM25 search service created")

    async def build_index(self, documents: List[Dict[str, Any]]) -> None:
        """
        Build BM25 index from documents.

        Args:
            documents: List of documents with 'text' field
        """
        if not documents:
            logger.warning("No documents provided for BM25 indexing")
            return

        try:
            from rank_bm25 import BM25Okapi
            
            # Store original documents
            self.documents = documents
            
            # Tokenize all documents
            self.corpus = []
            for doc in documents:
                text = doc.get("text", "")
                tokens = _tokenize(text)
                self.corpus.append(tokens)
            
            # Build BM25 index
            self.bm25 = BM25Okapi(self.corpus)
            self._initialized = True
            
            logger.info(
                "BM25 index built successfully",
                document_count=len(documents),
                avg_tokens=sum(len(c) for c in self.corpus) / len(self.corpus) if self.corpus else 0
            )
            
        except ImportError:
            logger.error("rank-bm25 not installed. Run: pip install rank-bm25")
            raise
        except Exception as e:
            logger.error("Failed to build BM25 index", error=str(e))
            raise

    async def search(
        self, 
        query: str, 
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search using BM25 algorithm.

        Args:
            query: Search query
            top_k: Number of results to return

        Returns:
            List of documents with BM25 scores
        """
        if not self._initialized or self.bm25 is None:
            logger.warning("BM25 index not initialized, returning empty results")
            return []

        try:
            # Tokenize query
            query_tokens = _tokenize(query)
            
            if not query_tokens:
                logger.debug("Empty query tokens, returning empty results")
                return []
            
            # Get BM25 scores for all documents
            scores = self.bm25.get_scores(query_tokens)
            
            # Get top-k indices sorted by score (descending)
            import numpy as np
            top_indices = np.argsort(scores)[::-1][:top_k]
            
            # Build results
            results = []
            for idx in top_indices:
                score = float(scores[idx])
                if score > 0:  # Only include docs with positive scores
                    doc = self.documents[idx].copy()
                    doc["bm25_score"] = score
                    results.append(doc)
            
            logger.debug(
                "BM25 search completed",
                query=query[:50],
                results_count=len(results),
                top_score=results[0]["bm25_score"] if results else 0
            )
            
            return results
            
        except Exception as e:
            logger.error("BM25 search failed", error=str(e))
            return []

    @property
    def is_initialized(self) -> bool:
        """Check if BM25 index is ready."""
        return self._initialized

    @property
    def document_count(self) -> int:
        """Get number of indexed documents."""
        return len(self.documents)


# Global BM25 search service instance
bm25_service = BM25SearchService()
