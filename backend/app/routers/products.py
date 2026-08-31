from fastapi import APIRouter
from pydantic import BaseModel
from app.ai.requirement_extractor import extract_requirements
from app.services.products import get_candidate_products
from app.schemas.requirements import ProdRequirements
from app.schemas.products import Product

router = APIRouter(prefix= "/api/products", tags= ["Products"])

class SearchRequest(BaseModel):
    query: str
    
class SearchResponse(BaseModel):
    query: str
    extracted_requirements: ProdRequirements
    total_candidates: int
    candidates: list[Product]
    
@router.post("/search", response_model=SearchResponse)
async def search_products(req: SearchRequest):
    # Step 1: Extract intent
    extracted_requirements: ProdRequirements = extract_requirements(req.query)
    
    # Step 2: Query Database
    candidates = await get_candidate_products(extracted_requirements)
    
    return SearchResponse(
        query= req.query,
        extracted_requirements= extracted_requirements,
        total_candidates= len(candidates),
        candidates= candidates
    )