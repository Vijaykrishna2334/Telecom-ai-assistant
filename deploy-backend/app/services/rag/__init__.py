"""
RAG (Retrieval-Augmented Generation) Services.

This module implements CRAG (Corrective RAG) - a 2024 state-of-the-art
RAG methodology that prevents hallucination through relevance grading.

Now with HYBRID SEARCH (vector + BM25 with RRF fusion) for improved accuracy.

Components:
- embeddings: BGE embedding model for semantic search
- retriever: ChromaDB vector store
- bm25_search: BM25 lexical search
- hybrid_retriever: Combines vector + BM25 with RRF fusion
- relevance_grader: CRAG relevance scoring
- crag_chain: Main orchestrator
- ingestion: Document loading and chunking
- knowledge_base: High-level interface
"""

from app.services.rag.knowledge_base import knowledge_base, KnowledgeBaseService
from app.services.rag.embeddings import embedding_service, EmbeddingService
from app.services.rag.retriever import retriever_service, RetrieverService
from app.services.rag.bm25_search import bm25_service, BM25SearchService
from app.services.rag.hybrid_retriever import hybrid_retriever, HybridRetriever
from app.services.rag.crag_chain import crag_chain, CRAGChain, CRAGResult, CRAGAction
from app.services.rag.relevance_grader import relevance_grader, RelevanceGrader, RelevanceGrade
from app.services.rag.ingestion import ingestion_service, IngestionService

__all__ = [
    # Main interfaces
    "knowledge_base",
    "KnowledgeBaseService",
    
    # CRAG components
    "crag_chain",
    "CRAGChain",
    "CRAGResult",
    "CRAGAction",
    
    # Relevance grading
    "relevance_grader",
    "RelevanceGrader",
    "RelevanceGrade",
    
    # Embeddings
    "embedding_service",
    "EmbeddingService",
    
    # Retriever (vector)
    "retriever_service",
    "RetrieverService",
    
    # BM25 Search
    "bm25_service",
    "BM25SearchService",
    
    # Hybrid Retriever (vector + BM25)
    "hybrid_retriever",
    "HybridRetriever",
    
    # Ingestion
    "ingestion_service",
    "IngestionService",
]
