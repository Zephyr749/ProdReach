from pydantic import BaseModel, Field
from typing import List, Optional


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
    
    
class ReviewEvidence(BaseModel):
    product_id: str = Field(..., description="ID of the product this review belongs to")
    text: str = Field(..., description="The relevant review snippet")
    rating: Optional[float | int] = Field(default=None, description="Customer star rating (e.g. 5, 4.5)")
    similarity_score: float = Field(..., description="Cosine similarity score from vector search (e.g. 0.824)")
