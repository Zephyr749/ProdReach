import asyncio
from app.core.db import init_db
from app.services.rag_indexer import initialize_rag_index
from app.ai.graph import research_graph


async def main():
    # 1. Initialize MongoDB & load pre-computed vector index
    await init_db()
    await initialize_rag_index()

    # 2. Define a test shopping query
    query = "Find me a smartphone under ₹28,000 with a solid battery and good daylight camera."

    print(f"\n========================================================")
    print(f"🚀 Invoking LangGraph for: \"{query}\"")
    print(f"========================================================")

    initial_state = {
        "query": query,
        "requirements": None,
        "candidates": [],
        "retry_count": 0,
        "relaxed_budget": False,
        "review_evidence": {},
        "final_recommendation": None,
        "error": None,
    }

    # 3. Execute the Graph
    final_state = await research_graph.ainvoke(initial_state)

    # 4. Inspect the Result
    rec = final_state.get("final_recommendation")
    if rec:
        print("\n================ FINAL RECOMMENDATION ================")
        print(f"🏆 Top Pick: {rec.top_pick_id}")
        print(f"Summary: {rec.recommendation_summary}\n")
        
        for c in rec.candidates:
            print(f"• {c.product_name} (Rank #{c.rank})")
            print("  Pros:")
            for pro in c.pros:
                print(f"    [+] {pro.statement}")
                print(f"        ↳ Citation: {pro.citation}")
            print("  Cons:")
            for con in c.cons:
                print(f"    [-] {con.statement}")
                print(f"        ↳ Citation: {con.citation}")
    else:
        print("No recommendation was generated.")


if __name__ == "__main__":
    asyncio.run(main())