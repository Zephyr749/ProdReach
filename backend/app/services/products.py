from app.schemas.requirements import ProdRequirements
from pymongo import MongoClient
from app.schemas.products import Product
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
