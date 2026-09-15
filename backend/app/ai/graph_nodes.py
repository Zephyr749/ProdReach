from app.ai.graph_state import ResearchAgentState
from app.ai.requirement_extractor import extract_requirements
from app.ai.grounded_recommender import generate_grounded_recommendation
from app.services.vector_search import search_relevant_reviews
from app.services.products import get_candidate_products
from app.schemas.requirements import ProdRequirements
from app.schemas.grounded_recommendations import ReviewEvidence
from typing import List


# --- Node 1: Intent Extraction (Phase 1) ---
async def extract_intent_node(state: ResearchAgentState) -> dict:
    print("\n--- [Node 1] Extracting Requirements ---")
    requirements = extract_requirements(state["query"])
    
    print(f" Extracted: Category={requirements.category}, Budget={requirements.budget}")
    return { "requirements": requirements }


# --- Node 2: Deterministic Filtering (Phase 2) ---
async def filter_candidates_node(state: ResearchAgentState) -> dict:
    print("\n--- [Node 2] Filtering Candidates from MongoDB ---")
    req = state["requirements"] or ProdRequirements()
    
    # Returns List[Product] directly from Beanie/MongoDB
    candidates = await get_candidate_products(req)
    print(f" Found {len(candidates)} candidate product(s).")
    
    return {"candidates": candidates}


# --- Node 3: Self Healing / Budget Relaxer ---
async def relax_criteria_node(state: ResearchAgentState) -> dict:
    print("\n--- [Fallback Node] Few Candidates Found: Relaxing Budget by 15% ---")
    req = state["requirements"].model_copy(deep=True) if state["requirements"] else ProdRequirements()
    
    # Relax budget by 15%
    if req.budget and req.budget.max:
        old_max = req.budget.max
        req.budget.max = int(old_max * 1.15)
        print(f" Adjusted budget max from ₹{old_max} to ₹{req.budget.max}")

    return {
        "requirements": req,
        "retry_count": state.get("retry_count", 0) + 1,
        "relaxed_budget": True,   
    }


# --- Node 4: Review RAG Evidence Gathering (Phase 4) ---
async def gather_review_evidence_node(state: ResearchAgentState) -> dict:
    print("\n--- [Node 3] Gathering Review Evidence via Vector RAG ---")
    evidence_map: dict[str, List[ReviewEvidence]] = {}
    
    # State["candidates"] contains typed Product models
    for product in state["candidates"]:
        matches = search_relevant_reviews(
            state["query"],
            product_ids= [product.product_id],
            top_k= 2
        )
        
        evidence_map[product.product_id] = [
            ReviewEvidence(
                product_id= product.product_id,
                text= chunk.review_text,
                rating= chunk.rating,
                similarity_score= round(score, 3),
            )
            for chunk, score in matches
        ]
        
        print(f" Collected {len(evidence_map[product.product_id])} review evidence item(s) for {product.name}")
        
    return { "review_evidence": evidence_map }
    
    
# --- Node 5: Grounded Recommendation Synthesis (Phase 5) ---
async def synthesize_recommendation_node(state: ResearchAgentState) -> dict:
    print("\n--- [Node 4] Generating Grounded Recommendation with Citations ---")
    
    # Pass the typed Product list directly to your grounded recommender
    recommendation = await generate_grounded_recommendation(
        state["query"],
        state["requirements"] or ProdRequirements(),
        state["candidates"]
    )
    
    return { "final_recommendation": recommendation }