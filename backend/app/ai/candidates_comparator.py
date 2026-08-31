import json
from typing import List
from app.schemas.requirements import ProdRequirements
from app.schemas.products import Product
from app.schemas.recommendations import RecommendationResponse
from app.ai.client import client
from app.core.config import app_settings


COMPARISON_SYSTEM_PROMPT = """
    You are an expert product advisor and comparative analyst.
    Your task is to evaluate a list of pre-filtered candidate products against the user's preferences and use cases.
    Rules:
    1. ONLY USE PROVIDED FACTS:
        - Base all pros, cons, and comparisons strictly on the provided candidate specifications and user reviews.
        - Do NOT invent specs or features not present in the candidate data.
    2. EVALUATE SOFT PREFERENCES & USE CASES:
        - Rank the candidate products based on how well they satisfy the user's soft preferences, use cases, and priority trade-offs.
        - Clearly explain why the #1 pick beats the alternatives.
    3. OBJECTIVE TRADE-OFF ANALYSIS:
        - Highlight meaningful differences (e.g., "Product A offers 2 hours longer battery life, but Product B has a 120Hz OLED screen").
"""

async def compare_candidates(
    query: str,
    requirements: ProdRequirements,
    candidates: List[Product]
) -> RecommendationResponse:
    if not candidates:
        raise ValueError("No products found")
    
    # Prepare compact payload for LLM
    candidate_context = [
        {
            "id": str(p.id),
            "name": p.name,
            "brand": p.brand,
            "price_inr": p.price_inr,
            "specifications": p.specifications.model_dump(),
            "sample_reviews": [ r.text for r in (p.reviews or [])[:3] ]
        } for p in candidates
    ]
        
    user_prompt = f"""User query: "{query}"
        Extracted Requirements:
            - Use Cases: {requirements.use_cases}
            - Soft Preferences: {requirements.preferences}
            - Avoid: {requirements.avoid}
        Filtered Candidates to Compare:
        {json.dumps(candidate_context, indent=2)}
    """
    
    response = client.chat.completions.parse(
        model= app_settings.model_name,
        messages= [
            { "role": "system", "content": COMPARISON_SYSTEM_PROMPT},
            { "role": "user", "content": user_prompt}
        ],
        response_format= RecommendationResponse,
        # temperature= 0.1,
    )
    
    return response.choices[0].message.parsed