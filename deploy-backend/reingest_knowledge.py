"""
Minimal script to clear and re-ingest knowledge base.
Avoids importing redis and other optional dependencies.
Run from backend directory with venv active: python reingest_knowledge.py
"""
import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def main():
    # Import only what we need
    from app.services.rag.retriever import retriever_service
    from app.services.rag.embeddings import embedding_service
    from app.services.rag.ingestion import ingestion_service
    
    print("=" * 60)
    print("CLEARING AND RE-INGESTING KNOWLEDGE BASE")
    print("=" * 60)
    
    # Step 1: Load embedding model
    print("\n[1/4] Loading embedding model...")
    await embedding_service.load_model()
    print("✅ Embedding model loaded")
    
    # Step 2: Clear existing collection
    print("\n[2/4] Clearing existing ChromaDB collection...")
    cleared = await retriever_service.clear_collection()
    if cleared:
        print("✅ Collection cleared successfully")
    else:
        print("❌ Failed to clear collection")
        return
    
    # Step 3: Ingest all files
    print("\n[3/4] Ingesting knowledge files...")
    stats = await ingestion_service.ingest_all_knowledge()
    
    # Step 4: Get stats
    print("\n[4/4] Getting collection stats...")
    final_stats = await retriever_service.get_collection_stats()
    
    print("\n" + "=" * 60)
    print("✅ INGESTION COMPLETE")
    print("=" * 60)
    print(f"Files processed: {stats.get('files_processed', 0)}")
    print(f"Chunks created:  {stats.get('chunks_created', 0)}")
    print(f"Total documents: {final_stats.get('count', 0)}")
    if stats.get('errors'):
        print(f"Errors: {stats.get('errors')}")
    print("=" * 60)
    print("\nYou can now restart your backend server to use the updated knowledge base.")

if __name__ == "__main__":
    asyncio.run(main())
