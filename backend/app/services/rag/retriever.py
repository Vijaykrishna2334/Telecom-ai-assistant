"""
Retriever service using ChromaDB for vector storage and semantic search.
"""
import chromadb
from typing import List, Dict, Any, Optional
from pathlib import Path

from app.core.config import settings
from app.core.logging import get_logger
from app.services.rag.embeddings import embedding_service

logger = get_logger(__name__)

# ChromaDB storage path
CHROMA_DB_PATH = Path(__file__).parent.parent.parent.parent / "chroma_db"


class RetrieverService:
    """Service for retrieving relevant documents from ChromaDB vector store."""

    def __init__(
        self,
        collection_name: Optional[str] = None,
        top_k: int = 5,
    ):
        """
        Initialize retriever service.

        Args:
            collection_name: Name of the ChromaDB collection
            top_k: Number of results to return
        """
        self.collection_name = collection_name or settings.chroma_collection
        self.top_k = top_k
        self.client = None
        self.collection = None
        logger.info("Initializing retriever service", collection=self.collection_name)

    async def connect(self) -> None:
        """Connect to ChromaDB (persistent storage)."""
        try:
            # Try persistent storage first
            CHROMA_DB_PATH.mkdir(parents=True, exist_ok=True)
            self.client = chromadb.PersistentClient(path=str(CHROMA_DB_PATH))
            logger.info("Connected to ChromaDB (persistent)", path=str(CHROMA_DB_PATH))
        except Exception as e:
            logger.warning("Persistent storage failed, using ephemeral", error=str(e))
            self.client = chromadb.EphemeralClient()
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}  # Use cosine similarity
        )
        logger.info("ChromaDB collection ready", name=self.collection_name)

    async def retrieve(
        self, 
        query: str, 
        top_k: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant documents for a query.

        Args:
            query: Search query
            top_k: Number of results (default: self.top_k)

        Returns:
            List of documents with text, metadata, and scores
        """
        if self.collection is None:
            await self.connect()

        k = top_k or self.top_k
        
        try:
            # Generate query embedding
            query_embedding = await embedding_service.embed_text(query)
            
            # Query ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=k,
                include=["documents", "metadatas", "distances"]
            )
            
            # Format results
            documents = []
            if results and results.get("documents"):
                for i, doc in enumerate(results["documents"][0]):
                    # Convert distance to similarity score (1 - distance for cosine)
                    distance = results["distances"][0][i] if results.get("distances") else 0
                    score = max(0, 1 - distance)  # Cosine similarity
                    
                    documents.append({
                        "text": doc,
                        "metadata": results["metadatas"][0][i] if results.get("metadatas") else {},
                        "score": score,
                    })
            
            logger.info("Retrieved documents", query=query[:50], count=len(documents))
            return documents
            
        except Exception as e:
            logger.error("Retrieval failed", error=str(e))
            return []

    async def add_documents(
        self,
        texts: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None,
    ) -> bool:
        """
        Add documents to the vector store.

        Args:
            texts: List of text documents
            metadatas: Optional list of metadata dicts
            ids: Optional list of document IDs

        Returns:
            True if successful
        """
        if self.collection is None:
            await self.connect()

        try:
            # Generate IDs if not provided
            if ids is None:
                import uuid
                ids = [str(uuid.uuid4()) for _ in texts]
            
            # Generate embeddings
            embeddings = await embedding_service.embed_batch(texts)
            
            # Prepare metadatas
            if metadatas is None:
                metadatas = [{} for _ in texts]
            
            # Add to ChromaDB
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas,
            )
            
            logger.info("Added documents to vector store", count=len(texts))
            return True
            
        except Exception as e:
            logger.error("Failed to add documents", error=str(e))
            return False

    async def delete_collection(self) -> bool:
        """Delete the entire collection."""
        try:
            if self.client:
                self.client.delete_collection(self.collection_name)
                self.collection = None
                logger.info("Deleted collection", name=self.collection_name)
                return True
        except Exception as e:
            logger.error("Failed to delete collection", error=str(e))
        return False

    async def clear_collection(self) -> bool:
        """Clear all documents from the collection and recreate it."""
        try:
            if self.client is None:
                await self.connect()
            
            # Delete existing collection
            try:
                self.client.delete_collection(self.collection_name)
                logger.info("Cleared existing collection", name=self.collection_name)
            except Exception:
                pass  # Collection may not exist
            
            # Recreate empty collection
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            logger.info("Recreated empty collection", name=self.collection_name)
            return True
            
        except Exception as e:
            logger.error("Failed to clear collection", error=str(e))
            return False

    async def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the collection."""
        if self.collection is None:
            await self.connect()
        
        try:
            count = self.collection.count()
            return {
                "name": self.collection_name,
                "count": count,
            }
        except Exception as e:
            logger.error("Failed to get stats", error=str(e))
            return {"name": self.collection_name, "count": 0}


# Global retriever service instance
retriever_service = RetrieverService()
