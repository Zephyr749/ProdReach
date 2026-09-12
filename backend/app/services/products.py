from app.schemas.requirements import ProdRequirements
from pymongo import MongoClient
from app.schemas.products import Product
from app.services.rag_indexer import ReviewChunk 
from app.ai.client import client
from app.core.config import app_settings
from typing import List


def build_product_query(requirements: ProdRequirements):
    query:dict = {}
    
    # 1. Category filter (case-insensitive)
    if requirements.category:
        query["category"] = { "$regex": f"^{requirements.category}", "$options": "i" }
        
    # 2. Budget filter
    price_filter = {}
    if requirements.budget:
        if requirements.budget.max:
            price_filter["$lte"] = requirements.budget.max
        if requirements.budget.min:
            price_filter["$gte"] = requirements.budget.min
            
    if price_filter:
        query["price_inr"] = price_filter
        
    # 3. Availability filter
    query["availability"] = "in_stock"
    
    # 4. Avoid terms (Filter out matching brands or keywords)
    if requirements.avoid:
        # Ensure brand or name does not match any avoid keywords
        avoid_patterns = [{"brand": {"$regex": term, "$options": "i"}} for term in requirements.avoid]
        avoid_patterns += [{"name": {"$regex": term, "$options": "i"}} for term in requirements.avoid]
        
        query["$nor"] = avoid_patterns
        
    return query

async def get_candidate_products(requirements: ProdRequirements, limit:int = 10) -> List[Product]:
    query = build_product_query(requirements)
    print("Query::", query)
    
    data = await Product.find(query).limit(limit).to_list()
    
    return data

async def ask_questions(top_reviews: List[tuple[ReviewChunk, float]], question: str) -> str | None:
    # 2. Format context
    context = "\n".join([f"- [Score: {score:.2f}]: \"{chunk.review_text}\"" for chunk, score in top_reviews])
    
    # 3. Prompt LLM with retrieved context
    prompt = f"""
        You are answering a question about a product based strictly on customer reviews.
        Relevant cusotmer Reviews:
        {context}
        
        Question: "{question}
        
        Answer the question factually based ONLY on the customer reviews above. If the reviews don't mention it, say so.
        """
        
    response = client.chat.completions.create(
        model= app_settings.base_model_name,
        messages= [{"role": "user", "content": prompt}],
        # temperature= 0.0
    )
    
    return response.choices[0].message.content