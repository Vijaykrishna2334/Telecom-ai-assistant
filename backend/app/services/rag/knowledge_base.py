"""
Knowledge base management service.
Now uses CRAG (Corrective RAG) for improved retrieval with hallucination prevention.
"""
from typing import List, Optional, Dict, Any

from app.core.logging import get_logger
from app.services.rag.embeddings import embedding_service
from app.services.rag.retriever import retriever_service
from app.services.rag.crag_chain import crag_chain, CRAGResult, CRAGAction

logger = get_logger(__name__)


class KnowledgeBaseService:
    """
    Service for managing the knowledge base.
    
    Uses CRAG (Corrective RAG) methodology for retrieval:
    - Grades document relevance before using in generation
    - Falls back gracefully when no relevant documents found
    - Prevents hallucination through architectural safeguards
    """

    def __init__(self):
        """Initialize knowledge base service."""
        self.embeddings = embedding_service
        self.retriever = retriever_service
        self.crag = crag_chain

    async def initialize(self) -> None:
        """Initialize the knowledge base."""
        logger.info("Initializing knowledge base with CRAG")
        await self.embeddings.load_model()
        await self.retriever.connect()
        logger.info("Knowledge base initialized")

    async def search(
        self, query: str, top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search the knowledge base.

        Args:
            query: Search query
            top_k: Number of results to return

        Returns:
            List of relevant documents with scores
        """
        logger.info("Searching knowledge base", query=query, top_k=top_k)
        return await self.retriever.retrieve(query, top_k)

    async def get_context_for_query(
        self, query: str, max_length: int = 2000
    ) -> str:
        """
        Get context text for a query using CRAG methodology.
        
        This method:
        1. Retrieves candidate documents
        2. Grades their relevance (CRAG core feature)
        3. Only uses relevant documents or returns fallback message

        Args:
            query: Search query
            max_length: Maximum context length

        Returns:
            Concatenated context string (or fallback message)
        """
        # Use CRAG chain for intelligent retrieval
        result: CRAGResult = await self.crag.process(query)
        
        if result.action == CRAGAction.FALLBACK:
            logger.info("CRAG: No relevant context, using fallback")
            return f"[NOTICE: {result.fallback_message}]"
        
        # Trim context to max length if needed
        context = result.context
        if len(context) > max_length:
            context = context[:max_length] + "..."
        
        logger.info(
            "CRAG: Context retrieved",
            action=result.action.value,
            doc_count=len(result.documents),
            context_length=len(context)
        )
        
        # DEBUG: Log the actual RAG context being sent to LLM
        logger.info("=" * 60)
        logger.info("📄 RAG CONTEXT BEING SENT TO LLM:")
        logger.info("=" * 60)
        for i, doc in enumerate(result.documents, 1):
            logger.info(f"--- Document {i} (score: {doc.get('score', 'N/A'):.3f}) ---")
            logger.info(f"Content: {doc.get('content', doc.get('text', 'N/A'))[:500]}")
            if doc.get('metadata'):
                logger.info(f"Metadata: {doc.get('metadata')}")
        logger.info("=" * 60)
        logger.info(f"FULL CONTEXT:\n{context}")
        logger.info("=" * 60)
        
        return context

    async def get_crag_result(self, query: str) -> CRAGResult:
        """
        Get full CRAG result with metadata.
        
        Use this when you need access to:
        - Individual document scores
        - CRAG action taken
        - Query used (may be refined)

        Args:
            query: Search query

        Returns:
            CRAGResult with full metadata
        """
        return await self.crag.process(query)

    async def add_document(
        self,
        text: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Add a document to the knowledge base.

        Args:
            text: Document text
            metadata: Optional metadata

        Returns:
            True if successful
        """
        logger.info("Adding document to knowledge base")
        return await self.retriever.add_documents([text], [metadata] if metadata else None)

    async def add_documents_batch(
        self,
        texts: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
    ) -> bool:
        """
        Add multiple documents to the knowledge base.

        Args:
            texts: List of document texts
            metadatas: Optional list of metadata dicts

        Returns:
            True if successful
        """
        logger.info("Adding documents batch", count=len(texts))
        return await self.retriever.add_documents(texts, metadatas)

    async def ingest_knowledge_files(self) -> Dict[str, Any]:
        """
        Ingest all knowledge files from the knowledge directory.
        
        Returns:
            Ingestion statistics
        """
        from app.services.rag.ingestion import ingestion_service
        return await ingestion_service.ingest_all_knowledge()

    async def get_stats(self) -> Dict[str, Any]:
        """Get knowledge base statistics."""
        return await self.retriever.get_collection_stats()


# Global knowledge base service instance
knowledge_base = KnowledgeBaseService()
