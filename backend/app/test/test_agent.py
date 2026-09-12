import asyncio
from app.core.db import init_db
from app.services.rag_indexer import initialize_rag_index
from app.ai.agent import run_product_research_agent

async def main():
    await init_db()
    await initialize_rag_index()

    query = "Find me a smartphone under ₹35k. Check customer reviews to see how the battery and camera perform in real life."

    print(f"\nStarting Research for: \"{query}\"\n")
    final_answer = await run_product_research_agent(query)
    
    print("\n================ FINAL AGENT RECOMMENDATION ================")
    print(final_answer)

if __name__ == "__main__":
    asyncio.run(main())