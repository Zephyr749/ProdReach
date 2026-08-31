from pydantic import BaseModel, Field
from typing import List

class CandidateEvaluation(BaseModel):
    product_id: str = Field(..., description= "Unique identifier of the product")
    product_name: str = Field(..., description= "Product name")
    rank: int = Field(..., description= "Rank among the candidates. (1 = best fit)")
    pros: List[str] = Field(..., description= "Pros according to user's usecases")
    cons: List[str] = Field(..., description= "Cons or compromises relavent to user")
    fit_summary: str = Field(..., description= "Why this product does or does not meet the user's needs")
    
class RecommendationResponse(BaseModel):
    top_pick_id: str = Field(..., description= "The id of the top recommended product")
    summary: str = Field(..., description= "A 2-3 line recommendation summary")
    ranked_candidates: List[CandidateEvaluation] = Field(..., description= "List of ranked product candidates")
    trade_off_analysis: str = Field(..., description= "Detailed explanation of the key trade-offs between options")
    
    