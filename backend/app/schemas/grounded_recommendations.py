from pydantic import BaseModel, Field
from typing import List


class GroundedClaim(BaseModel):
    statement: str = Field(..., description= "The factual claim about the product")
    citation: str = Field(..., description= "Exact source, e.g. '[Review #1: ...]' or '[Spec: battery_mah = 5000]")
    

class GroundedCandidate(BaseModel):
    product_id: str
    product_name: str
    rank: int
    pros: List[GroundedClaim] = Field(..., description="Pros strictly supported by citations")
    cons: list[GroundedClaim] = Field(..., description="Cons or compromises supported by citations")
    fit_summary: str
    
    
class GroundedRecommendationResponse(BaseModel):
    top_pick_id: str
    recommendation_summary: str
    candidates: List[GroundedCandidate]