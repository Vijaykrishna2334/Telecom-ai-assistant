"""
Knowledge Base API endpoints.
Provides endpoints for managing the CRAG-powered knowledge base.
"""
from typing import Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.core.logging import get_logger
from app.services.rag import knowledge_base, ingestion_service

logger = get_logger(__name__)
router = APIRouter()


class IngestResponse(BaseModel):
    """Response for knowledge ingestion."""
    files_processed: int
    chunks_created: int
    errors: list[str]


class SearchRequest(BaseModel):
    """Request for knowledge search."""
    query: str
    top_k: int = 5


class SearchResult(BaseModel):
    """A single search result."""
    text: str
    score: float
    source: Optional[str] = None


class SearchResponse(BaseModel):
    """Response for knowledge search."""
    results: list[SearchResult]
    query: str


class StatsResponse(BaseModel):
    """Knowledge base statistics."""
    collection_name: str
    document_count: int


@router.post(
    "/ingest",
    response_model=IngestResponse,
    status_code=status.HTTP_200_OK,
    tags=["Knowledge Base"],
)
async def ingest_knowledge() -> IngestResponse:
    """
    Ingest all knowledge files into the vector database.
    
    This will:
    1. Read all files from the knowledge/ directory
    2. Chunk them appropriately (FAQ by Q&A, plans by item, etc.)
    3. Generate embeddings using BGE model
    4. Store in ChromaDB for semantic search
    """
    try:
        logger.info("Starting knowledge base ingestion")
        stats = await knowledge_base.ingest_knowledge_files()
        
        return IngestResponse(
            files_processed=stats.get("files_processed", 0),
            chunks_created=stats.get("chunks_created", 0),
            errors=stats.get("errors", [])
        )
    except Exception as e:
        logger.error("Knowledge ingestion failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to ingest knowledge: {str(e)}"
        )


@router.post(
    "/search",
    response_model=SearchResponse,
    status_code=status.HTTP_200_OK,
    tags=["Knowledge Base"],
)
async def search_knowledge(request: SearchRequest) -> SearchResponse:
    """
    Search the knowledge base.
    
    Uses CRAG (Corrective RAG) which:
    1. Retrieves candidate documents
    2. Grades their relevance
    3. Returns only relevant results
    """
    try:
        logger.info("Searching knowledge base", query=request.query)
        
        # Get CRAG result for detailed scores
        crag_result = await knowledge_base.get_crag_result(request.query)
        
        results = []
        for i, doc in enumerate(crag_result.documents):
            score = crag_result.relevance_scores[i] if i < len(crag_result.relevance_scores) else 0.0
            results.append(SearchResult(
                text=doc.get("text", ""),
                score=score,
                source=doc.get("metadata", {}).get("source")
            ))
        
        return SearchResponse(
            results=results,
            query=crag_result.query_used
        )
    except Exception as e:
        logger.error("Knowledge search failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search knowledge: {str(e)}"
        )


@router.get(
    "/stats",
    response_model=StatsResponse,
    status_code=status.HTTP_200_OK,
    tags=["Knowledge Base"],
)
async def get_stats() -> StatsResponse:
    """Get knowledge base statistics."""
    try:
        stats = await knowledge_base.get_stats()
        return StatsResponse(
            collection_name=stats.get("name", "unknown"),
            document_count=stats.get("count", 0)
        )
    except Exception as e:
        logger.error("Failed to get stats", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get stats: {str(e)}"
        )


@router.post(
    "/reingest",
    response_model=IngestResponse,
    status_code=status.HTTP_200_OK,
    tags=["Knowledge Base"],
)
async def reingest_knowledge() -> IngestResponse:
    """
    Clear and re-ingest all knowledge files.
    
    This will:
    1. DELETE all existing documents from the vector store
    2. Re-read and re-chunk all knowledge files
    3. Generate fresh embeddings
    4. Store in ChromaDB
    
    Use this to fix stale embeddings or duplicates.
    """
    try:
        from app.services.rag import retriever_service
        
        logger.info("Starting knowledge base re-ingestion (clearing first)")
        
        # Step 1: Clear existing collection
        cleared = await retriever_service.clear_collection()
        if not cleared:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to clear existing collection"
            )
        logger.info("Cleared existing knowledge base")
        
        # Step 2: Re-ingest all files
        stats = await knowledge_base.ingest_knowledge_files()
        
        logger.info(
            "Re-ingestion complete",
            files=stats.get("files_processed", 0),
            chunks=stats.get("chunks_created", 0)
        )
        
        return IngestResponse(
            files_processed=stats.get("files_processed", 0),
            chunks_created=stats.get("chunks_created", 0),
            errors=stats.get("errors", [])
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Knowledge re-ingestion failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to re-ingest knowledge: {str(e)}"
        )
