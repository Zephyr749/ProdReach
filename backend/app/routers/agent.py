from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.ai.graph import research_graph
from app.schemas.grounded_recommendations import GroundedRecommendationResponse

router = APIRouter(prefix="/api/agent", tags=["Agent"])


class AgentResearchRequest(BaseModel):
    query: str


class AgentResearchResponse(BaseModel):
    query: str
    relaxed_budget: bool
    retry_count: int
    recommendation: GroundedRecommendationResponse | None


@router.post("/research", response_model=AgentResearchResponse)
async def research_product_endpoint(req: AgentResearchRequest):
    initial_state = {
        "query": req.query,
        "requirements": None,
        "candidates": [],
        "retry_count": 0,
        "relaxed_budget": False,
        "review_evidence": {},
        "final_recommendation": None,
        "error": None,
    }

    # Execute LangGraph
    final_state = await research_graph.ainvoke(initial_state)

    if not final_state.get("final_recommendation"):
        raise HTTPException(status_code=404, detail="Could not find or synthesize matching products.")

    return AgentResearchResponse(
        query=req.query,
        relaxed_budget=final_state.get("relaxed_budget", False),
        retry_count=final_state.get("retry_count", 0),
        recommendation=final_state.get("final_recommendation"),
    )