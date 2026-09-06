import asyncio
from app.core.db import init_db
from app.schemas.products import Product
from app.services.rag_indexer import initialize_rag_index
from app.services.vector_search import search_relevant_reviews

test_queries = [
    "How is the battery backup for long travels?",
    "Is the camera good in low light and night shots?",
    "Does the device get warm or throttle under heavy workloads?",
]


async def main():
    # 1. Initialize DB and build in-memory vector index
    await init_db()
    await initialize_rag_index()
    # 2. Run semantic search queries
    for query in test_queries:
        print(f"\n==================================================")
        print(f"🔍 USER QUERY: \"{query}\"")
        print(f"==================================================")

        matches = search_relevant_reviews(query, top_k=2)
        for i, (chunk, score) in enumerate(matches, start=1):
            print(f"\n[{i}] Product: {chunk.product_name} (Score: {score:.4f})")
            print(f"    Rating: {chunk.rating} ⭐")
            print(f"    Evidence: \"{chunk.review_text}\"")


if __name__ == "__main__":
    asyncio.run(main())

