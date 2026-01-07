"""
Document ingestion service for loading knowledge files into ChromaDB.
Supports smart chunking for different document types.
"""
import json
import re
from pathlib import Path
from typing import List, Dict, Any, Optional

from app.core.logging import get_logger
from app.services.rag.retriever import retriever_service

logger = get_logger(__name__)

# Knowledge base path
KNOWLEDGE_PATH = Path(__file__).parent.parent.parent.parent.parent / "knowledge"


class DocumentChunker:
    """Chunks documents based on their type for optimal retrieval."""

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        """
        Initialize chunker.

        Args:
            chunk_size: Maximum characters per chunk
            chunk_overlap: Overlap between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_markdown(self, content: str, source: str) -> List[Dict[str, Any]]:
        """
        Chunk markdown files by sections (## headers).
        Prepends document title to each chunk for better context.
        """
        chunks = []
        
        # Extract document title (first # header)
        title_match = re.search(r'^#\s+(.+?)$', content, re.MULTILINE)
        doc_title = title_match.group(1).strip() if title_match else source
        
        # Split by ## headers
        sections = re.split(r'\n(?=## )', content)
        
        for section in sections:
            section = section.strip()
            if not section or len(section) < 20:
                continue
            
            # Check if this section has a table (|---| pattern)
            has_table = '|---|' in section or '| ---' in section
            
            # For sections with tables, keep them together even if long
            if has_table:
                # Prepend document title for context
                chunk_with_context = f"[{doc_title}]\n\n{section}"
                chunks.append({
                    "text": chunk_with_context,
                    "metadata": {"source": source, "type": "section", "has_table": True}
                })
            # If section is too long and has no table, split further
            elif len(section) > self.chunk_size * 2:
                # Split by ### headers or paragraphs
                sub_chunks = self._split_long_section(section)
                for sub in sub_chunks:
                    # Prepend document title for context
                    chunk_with_context = f"[{doc_title}]\n\n{sub}"
                    chunks.append({
                        "text": chunk_with_context,
                        "metadata": {"source": source, "type": "section"}
                    })
            else:
                # Prepend document title for context
                chunk_with_context = f"[{doc_title}]\n\n{section}"
                chunks.append({
                    "text": chunk_with_context,
                    "metadata": {"source": source, "type": "section"}
                })
        
        return chunks

    def chunk_faq(self, content: str, source: str) -> List[Dict[str, Any]]:
        """
        Chunk FAQ files by Q&A pairs.
        """
        chunks = []
        
        # Split by Q: or ## Q: patterns
        qa_pattern = r'\n(?=(?:Q:|## Q:|\*\*Q:))'
        qa_sections = re.split(qa_pattern, content)
        
        for qa in qa_sections:
            qa = qa.strip()
            if not qa or len(qa) < 30:
                continue
            
            chunks.append({
                "text": qa,
                "metadata": {"source": source, "type": "faq"}
            })
        
        return chunks

    def chunk_json(self, content: str, source: str) -> List[Dict[str, Any]]:
        """
        Chunk JSON files - each item becomes a chunk.
        """
        chunks = []
        
        try:
            data = json.loads(content)
            
            if isinstance(data, list):
                for item in data:
                    text = json.dumps(item, indent=2)
                    chunks.append({
                        "text": text,
                        "metadata": {"source": source, "type": "json_item"}
                    })
            elif isinstance(data, dict):
                # For dict, chunk by top-level keys
                for key, value in data.items():
                    text = f"{key}: {json.dumps(value, indent=2)}"
                    chunks.append({
                        "text": text,
                        "metadata": {"source": source, "type": "json_item", "key": key}
                    })
        except json.JSONDecodeError:
            # Fall back to text chunking
            chunks = self._simple_chunk(content, source)
        
        return chunks

    def _split_long_section(self, section: str) -> List[str]:
        """Split a long section into smaller chunks."""
        chunks = []
        paragraphs = section.split('\n\n')
        
        current_chunk = ""
        for para in paragraphs:
            if len(current_chunk) + len(para) < self.chunk_size:
                current_chunk += para + "\n\n"
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = para + "\n\n"
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks

    def _simple_chunk(self, content: str, source: str) -> List[Dict[str, Any]]:
        """Simple character-based chunking."""
        chunks = []
        start = 0
        
        while start < len(content):
            end = start + self.chunk_size
            chunk_text = content[start:end]
            
            chunks.append({
                "text": chunk_text,
                "metadata": {"source": source, "type": "text"}
            })
            
            start = end - self.chunk_overlap
        
        return chunks


class IngestionService:
    """Service for ingesting knowledge documents into the vector store."""

    def __init__(self):
        """Initialize ingestion service."""
        self.chunker = DocumentChunker()
        logger.info("Initializing ingestion service")

    async def ingest_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Ingest a single file into the vector store.

        Args:
            file_path: Path to the file

        Returns:
            Stats about the ingestion
        """
        try:
            content = file_path.read_text(encoding='utf-8')
            source = file_path.name
            
            # Choose chunking strategy based on file type and path
            if file_path.suffix == '.json':
                chunks = self.chunker.chunk_json(content, source)
            elif 'faq' in str(file_path).lower():
                chunks = self.chunker.chunk_faq(content, source)
            elif file_path.suffix == '.md':
                chunks = self.chunker.chunk_markdown(content, source)
            else:
                chunks = self.chunker._simple_chunk(content, source)
            
            if not chunks:
                return {"file": source, "chunks": 0, "error": "No chunks created"}
            
            # Add to vector store
            texts = [c["text"] for c in chunks]
            metadatas = [c["metadata"] for c in chunks]
            
            success = await retriever_service.add_documents(texts, metadatas)
            
            return {
                "file": source,
                "chunks": len(chunks),
                "success": success
            }
            
        except Exception as e:
            logger.error("Failed to ingest file", file=str(file_path), error=str(e))
            return {"file": str(file_path), "chunks": 0, "error": str(e)}

    async def ingest_all_knowledge(self) -> Dict[str, Any]:
        """
        Ingest all knowledge files from the knowledge directory.

        Returns:
            Statistics about the ingestion
        """
        if not KNOWLEDGE_PATH.exists():
            logger.error("Knowledge path doesn't exist", path=str(KNOWLEDGE_PATH))
            return {"files_processed": 0, "chunks_created": 0, "errors": ["Knowledge path not found"]}
        
        # Connect to retriever first
        await retriever_service.connect()
        
        stats = {
            "files_processed": 0,
            "chunks_created": 0,
            "errors": []
        }
        
        # Find all files
        extensions = ['.md', '.json', '.txt']
        files = []
        for ext in extensions:
            files.extend(KNOWLEDGE_PATH.rglob(f'*{ext}'))
        
        logger.info("Found knowledge files", count=len(files))
        
        for file_path in files:
            result = await self.ingest_file(file_path)
            stats["files_processed"] += 1
            stats["chunks_created"] += result.get("chunks", 0)
            
            if result.get("error"):
                stats["errors"].append(f"{result['file']}: {result['error']}")
            else:
                logger.info("Ingested file", file=result["file"], chunks=result["chunks"])
        
        logger.info(
            "Ingestion complete",
            files=stats["files_processed"],
            chunks=stats["chunks_created"],
            errors=len(stats["errors"])
        )
        
        return stats


# Global ingestion service instance
ingestion_service = IngestionService()
