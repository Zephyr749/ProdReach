from fastapi import APIRouter
from pydantic import BaseModel
from app.schemas.recommendations import RecommendationResponse
from app.schemas.grounded_recommendations import GroundedRecommendationResponse
from app.ai.requirement_extractor import extract_requirements
from app.ai.candidates_comparator import compare_candidates
from app.ai.grounded_recommender import generate_grounded_recommendation
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


@router.post("/grounded", response_model= GroundedRecommendationResponse)
async def get_grounded_recommendation(req: ShoppingQueryRequest):
    # 1. Phase 1: Extract Requirements
    requirements = extract_requirements(req.query)
    
    # 2. Phase 2: Deterministic candidate filter
    candidates = await get_candidate_products(requirements)
    if not candidates:
        return { "summary": "No products matched your exact criteria." }
    
    # 3. Phase 4 + Phase 5: RAG Evidence Retrieval + Grounded Citaions
    return await generate_grounded_recommendation(req.query, requirements, candidates)