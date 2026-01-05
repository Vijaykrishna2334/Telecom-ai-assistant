"""
Knowledge base management service.
"""
from typing import List, Optional

from app.core.logging import get_logger
from app.services.rag.embeddings import embedding_service
from app.services.rag.retriever import retriever_service

logger = get_logger(__name__)


class KnowledgeBaseService:
    """Service for managing the knowledge base."""

    def __init__(self):
        """Initialize knowledge base service."""
        self.embeddings = embedding_service
        self.retriever = retriever_service

    async def initialize(self) -> None:
        """Initialize the knowledge base."""
        logger.info("Initializing knowledge base")
        await self.embeddings.load_model()
        await self.retriever.connect()
        logger.info("Knowledge base initialized")

    async def search(
        self, query: str, top_k: int = 3
    ) -> List[dict[str, any]]:
        """
        Search the knowledge base.

        Args:
            query: Search query
            top_k: Number of results to return

        Returns:
            List of relevant documents
        """
        logger.info("Searching knowledge base", query=query, top_k=top_k)

        # Retrieve relevant documents
        results = await self.retriever.retrieve(query, top_k)

        return results

    async def get_context_for_query(
        self, query: str, max_length: int = 1000
    ) -> str:
        """
        Get context text for a query.

        Args:
            query: Search query
            max_length: Maximum context length

        Returns:
            Concatenated context string
        """
        results = await self.search(query, top_k=3)

        context_parts = []
        current_length = 0

        for result in results:
            text = result.get("text", "")
            if current_length + len(text) <= max_length:
                context_parts.append(text)
                current_length += len(text)
            else:
                # Add partial text if it fits
                remaining = max_length - current_length
                if remaining > 100:  # Only add if meaningful amount remains
                    context_parts.append(text[:remaining])
                break

        return "\n\n".join(context_parts)

    async def add_document(
        self,
        text: str,
        metadata: Optional[dict[str, any]] = None,
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

        # Generate embedding
        embedding = await self.embeddings.embed_text(text)

        # Add to retriever
        success = await self.retriever.add_documents(
            [text], [metadata] if metadata else None
        )

        return success

    async def add_documents_batch(
        self,
        texts: List[str],
        metadatas: Optional[List[dict[str, any]]] = None,
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

        # Generate embeddings
        embeddings = await self.embeddings.embed_batch(texts)

        # Add to retriever
        success = await self.retriever.add_documents(texts, metadatas)

        return success


# Global knowledge base service instance
knowledge_base = KnowledgeBaseService()
