
from app.services.vector_search import search_relevant_reviews
from app.schemas.requirements import ProdRequirements
from app.schemas.grounded_recommendations import GroundedRecommendationResponse
from app.ai.client import client
from app.core.config import app_settings
from typing import List


GROUNDED_SYSTEM_PROMPT = """
    You are an evidence-based product research assistant.
    Your goal is to evaluate candidate products and produce a recommendation where EVERY claim is backed by explicit citations.
    
    Rules:
        1. STRICTLY GROUNDING:
            - You may ONLY make claims that are explicitly supported by the provided [Spec] or [Review #N] context.
            - Do NOT invent claims, extrapolate unsupported opinions, or assume features.
            
        2. MANDATORY CITATIONS:
            - For every pro, con, or factual claim, you MUST provide the exact source ciatation:
                * e.g., "[Review #1: 'Battery life is good for a full day...']"
                * e.g., "[Spec: refresh_hz = 120]"
        3. UNMENTIONED ATTRIBUTES:
            - If the user asked about something not mentioned in the reviews or specs, state explicitly that no evidence was found rather than guessing.
"""

async def generate_grounded_recommendation(
    query: str,
    requirements: ProdRequirements,
    candidates: List
) -> GroundedRecommendationResponse:
    candidate_packets = []
    
    for p in candidates:
        relevant_reviews = search_relevant_reviews(
            query,
            product_ids= [p.product_id],
            top_k= 3
        )
        
        review_evidence_text = '\n'.join([
            f" - [Review # {idx}]: \"{chunk.review_text}\" (Rating: {chunk.rating}*)"
            for idx, (chunk, score) in enumerate(relevant_reviews, start= 1)
        ])
        
        specs_text = "\n".join([
            f" - [Spec: {k} = {v}]"
            for k, v in p.specifications.model_dump(exclude_none= True).items()
        ])
        
        packet = f"""
            Product: {p.name} (ID: {p.product_id})
            Brand: {p.brand}, Price: ₹{p.price_inr}
            Specifications:
            {specs_text}
            Customer Review Evidence:
            {review_evidence_text or '  - No relevant reviews found.'}
        """
        
        candidate_packets.append(packet)
        
        full_context = "\n----------------------------------------\n".join(candidate_packets)
        
        user_prompt = f"""
        User Request: "{query}"
        
        Extracted Intent:
            - Use Cases: {requirements.use_cases}
            - Soft Preferences: {requirements.preferences}
            - Avoid {requirements.avoid}
            
        Candidate Products & Verified Evidence:
        {full_context}
        
        Please evaluate the candidates and produce an evidence-grounded recommendation.
        """
        
        response = client.chat.completions.parse(
            model= app_settings.base_model_name,
            messages= [
                { "role": "system", "content": GROUNDED_SYSTEM_PROMPT },
                { "role": "user", "content": user_prompt}
            ],
            response_format= GroundedRecommendationResponse,
            # temperature= 0.0
        )
        
        return response.choices[0].message.parsed