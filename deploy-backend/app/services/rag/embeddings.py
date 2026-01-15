"""
Embedding generation service using sentence-transformers.
Uses BAAI/bge-base-en-v1.5 - the top-performing 2024 model for RAG.

Model Selection Rationale (2024 Research):
- BGE models consistently outperform MiniLM on retrieval benchmarks
- bge-base-en-v1.5 has 768 dimensions with excellent semantic quality
- Optimized for RAG use cases with instruction-following capability
"""
from typing import List, Optional
import numpy as np

from app.core.logging import get_logger

logger = get_logger(__name__)

# Lazy import to avoid slow startup
_model = None

# BGE (BAAI General Embedding) - Top-performing model for RAG in 2024
# Alternatives considered: E5-large-v2, Nomic-embed-text, all-MiniLM-L6-v2
_model_name = "BAAI/bge-base-en-v1.5"  # 768 dimensions, best for RAG
_model_dimension = 768


def _get_model():
    """Lazy load the embedding model."""
    global _model
    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer
            logger.info("Loading embedding model", model=_model_name)
            _model = SentenceTransformer(_model_name)
            logger.info("Embedding model loaded successfully")
        except Exception as e:
            logger.error("Failed to load embedding model", error=str(e))
            raise
    return _model


class EmbeddingService:
    """
    Service for generating text embeddings using sentence-transformers.
    
    Uses BGE (BAAI General Embedding) model - the 2024 state-of-the-art
    for retrieval-augmented generation.
    """

    def __init__(self, model_name: str = "BAAI/bge-base-en-v1.5"):
        """
        Initialize embedding service.

        Args:
            model_name: Name of the sentence-transformers model
        """
        self.model_name = model_name
        self._dimension = _model_dimension
        logger.info("Initializing embedding service", model=model_name)

    async def load_model(self) -> None:
        """Load the embedding model (lazy initialization)."""
        try:
            _get_model()
            logger.info("Embedding model ready", model=self.model_name)
        except Exception as e:
            logger.error("Failed to load embedding model", error=str(e))
            raise

    @property
    def dimension(self) -> int:
        """Get embedding dimension."""
        return self._dimension

    async def embed_text(self, text: str, add_instruction: bool = True) -> List[float]:
        """
        Generate embedding for a single text.
        
        BGE models work best with query instructions for retrieval tasks.

        Args:
            text: Text to embed
            add_instruction: Whether to add BGE query instruction

        Returns:
            Embedding vector as list of floats
        """
        logger.debug("Generating embedding", text_length=len(text))
        
        try:
            model = _get_model()
            
            # BGE models perform better with instruction prefix for queries
            if add_instruction and len(text) < 500:  # Likely a query
                text = f"Represent this sentence for searching relevant passages: {text}"
            
            embedding = model.encode(text, convert_to_numpy=True, normalize_embeddings=True)
            return embedding.tolist()
        except Exception as e:
            logger.error("Failed to generate embedding", error=str(e))
            raise

    async def embed_batch(
        self, 
        texts: List[str], 
        batch_size: int = 32,
        add_instruction: bool = False  # Usually False for documents
    ) -> List[List[float]]:
        """
        Generate embeddings for multiple texts (documents).

        Args:
            texts: List of texts to embed
            batch_size: Batch size for encoding
            add_instruction: Whether to add instruction prefix

        Returns:
            List of embedding vectors
        """
        logger.info("Generating batch embeddings", count=len(texts))
        
        try:
            model = _get_model()
            
            # For documents, we typically don't add instruction
            processed_texts = texts
            if add_instruction:
                processed_texts = [
                    f"Represent this sentence for searching relevant passages: {t}" 
                    for t in texts
                ]
            
            embeddings = model.encode(
                processed_texts, 
                convert_to_numpy=True, 
                normalize_embeddings=True,
                batch_size=batch_size,
                show_progress_bar=len(texts) > 10
            )
            return embeddings.tolist()
        except Exception as e:
            logger.error("Failed to generate batch embeddings", error=str(e))
            raise

    async def compute_similarity(self, text1: str, text2: str) -> float:
        """
        Compute cosine similarity between two texts.

        Args:
            text1: First text
            text2: Second text

        Returns:
            Similarity score (0-1)
        """
        emb1 = await self.embed_text(text1, add_instruction=False)
        emb2 = await self.embed_text(text2, add_instruction=False)
        
        # Cosine similarity (embeddings are already normalized)
        similarity = np.dot(emb1, emb2)
        return float(max(0, min(1, similarity)))  # Clamp to 0-1


# Global embedding service instance
embedding_service = EmbeddingService()
