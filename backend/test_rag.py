"""
Quick RAG Test Script - Test hybrid search and CRAG directly.
Run this from the backend directory with your venv activated.
"""
import asyncio
import sys

# Add backend to path
sys.path.insert(0, '.')

async def test_rag(query: str):
    """Test RAG with a query and show results."""
    # Direct imports to avoid loading all services
    from app.services.rag.crag_chain import crag_chain
    from app.services.rag.hybrid_retriever import hybrid_retriever
    from app.services.rag.retriever import retriever_service
    from app.services.rag.embeddings import embedding_service
    
    print(f"\n{'='*60}")
    print(f"QUERY: {query}")
    print(f"{'='*60}\n")
    
    # Initialize
    print("Initializing RAG components...")
    await embedding_service.load_model()
    await retriever_service.connect()
    await hybrid_retriever.initialize()
    print("Initialization complete!\n")
    
    # Test hybrid retriever directly
    print("HYBRID RETRIEVER RESULTS:")
    print("-" * 40)
    results = await hybrid_retriever.retrieve(query, top_k=5)
    
    if not results:
        print("No results from hybrid retriever!")
    else:
        for i, doc in enumerate(results, 1):
            text = doc.get('text', '')[:200]
            score = doc.get('score', 0)
            rrf = doc.get('rrf_score', '-')
            bm25 = doc.get('bm25_score', '-')
            source = doc.get('metadata', {}).get('source', 'unknown')
            print(f"\n{i}. [Vector: {score:.3f}] [RRF: {rrf}] [BM25: {bm25}]")
            print(f"   Source: {source}")
            print(f"   Text: {text}...")
    
    print(f"\n{'='*60}")
    print("CRAG CHAIN RESULT:")
    print("-" * 40)
    
    # Test full CRAG chain
    result = await crag_chain.process(query)
    print(f"Action: {result.action.value}")
    print(f"Documents found: {len(result.documents)}")
    print(f"Query used: {result.query_used[:100]}...")
    print(f"\nRelevance scores: {result.relevance_scores}")
    print(f"\nContext Preview (first 2000 chars):")
    print(result.context[:2000] if result.context else "No context")
    
    if result.fallback_message:
        print(f"\nFALLBACK: {result.fallback_message}")
    
    print(f"\n{'='*60}\n")

if __name__ == "__main__":
    # Default test queries
    queries = [
        "I need a plan between 500 to 700 rupees",
    ]
    
    # Or use command line argument
    if len(sys.argv) > 1:
        queries = [" ".join(sys.argv[1:])]
    
    for q in queries:
        asyncio.run(test_rag(q))
