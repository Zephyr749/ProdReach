from fastapi import APIRouter, Query, Request
from pydantic import BaseModel

from app.schemas.requirements import ProdRequirements
from app.ai.requirement_extractor import extract_requirements

router= APIRouter(prefix="/api/requirements", tags=["Requirements"])

class ExtractionData(BaseModel):
    query: str


@router.post("/extract", response_model= ProdRequirements)
def extract_query(data: ExtractionData):
    query= data.query
    print("extracting...", query)
    return extract_requirements(query)