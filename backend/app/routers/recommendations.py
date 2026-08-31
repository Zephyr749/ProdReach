from fastapi import APIRouter
from pydantic import BaseModel
from app.schemas.recommendations import RecommendationResponse
from app.ai.requirement_extractor import extract_requirements
from app.ai.candidates_comparator import compare_candidates
from app.services.products import get_candidate_products

router = APIRouter(prefix="/api/recommendations", tags=["Recommendations"])

class ShoppingQueryRequest(BaseModel):
    query: str
    
@router.post("/generate", response_model= RecommendationResponse)
async def generate_recommendation(req: ShoppingQueryRequest):
    # Extract
    requirements = extract_requirements(req.query)
    
    # Fetch Products
    candidates = await get_candidate_products(requirements)
    if not candidates:
        return { "summary": "No products matched your exact hard criteria." }
    
    # LLM comparison and ranking
    recommendation = await compare_candidates(req.query, requirements, candidates)
    
    return recommendation

