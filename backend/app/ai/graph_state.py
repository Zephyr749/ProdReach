from app.schemas.requirements import ProdRequirements
from app.schemas.products import Product
from app.schemas.grounded_recommendations import GroundedRecommendationResponse, ReviewEvidence
from typing import TypedDict, Optional, List


class ResearchAgentState(TypedDict):
    # Inputs
    query: str
    
    # Extracted by Phase 1
    requirements: Optional[ProdRequirements]
    
    # Populated by Phase 2 (MongoDB Filter)
    candidates: list[Product]
    
    # Tracking self-healing retries
    retry_count: int
    relaxed_budget: bool
    
    # Gathered by Phase 4 (Vector RAG)
    review_evidence: dict[str, List[ReviewEvidence]] # product_id -> list of review snippets
    
    # Product by phase 5
    final_recommendation: Optional[GroundedRecommendationResponse]
    error: Optional[str]