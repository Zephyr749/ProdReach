from typing import List
from app.schemas.requirements import ProdRequirements, Budget
from app.schemas.products import Product
from app.services.products import get_candidate_products
from app.services.vector_search import search_relevant_reviews


# 1. Python tool implementation
async def tool_search_products(
    category: str, max_price: float | None = None, avoid: List[str] | None = None
) -> List[dict]:
    req = ProdRequirements(
        category=category,
        budget=Budget(max=max_price) if max_price else None,
        avoid=avoid or [],
    )

    candidates = await get_candidate_products(req, limit=5)

    return [
        {
            "product_id": p.product_id,
            "name": p.name,
            "brand": p.brand,
            "price_inr": p.price_inr,
            "specifications": p.specifications.model_dump(exclude_none=True),
        }
        for p in candidates
    ]


async def tool_get_product_details(product_id: str) -> dict | None:
    product = await Product.find_one({"product_id": product_id})
    if not product:
        print(f"Product with id {product_id} not found")

    return product.model_dump(exclude={"reviews": {"__all__": {"embedding"}}})


async def tool_search_reviews(query: str, product_id: str | None = None) -> List[dict]:
    matches = search_relevant_reviews(
        query, product_ids=[product_id] if product_id else None, top_k=3
    )

    return [
        {
            "product_id": chunk.product_id,
            "product_name": chunk.product_name,
            "rating": chunk.rating,
            "review_text": chunk.review_text,
            "similarity": round(score, 3),
        }
        for chunk, score in matches
    ]


# 2. Tool definition for the LLM
AVAILABLE_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_products",
            "description": "Search for candidate products in the database by category, max price budget, and excluded brands/keywords.",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "e.g. 'laptop', 'smartphone', 'headphones'",
                    },
                    "max_price": {
                        "type": "integer",
                        "description": "Maximum budget in INR (e.g. 75000)",
                    },
                    "avoid": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Brands or terms to exclude",
                    },
                },
                "required": ["category"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_reviews",
            "description": "Semantically search customer reviews to verify real-world experiences (e.g. battery life, build quality, camera, heat, fan noise).",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The specific question or feature to check in reviews",
                    },
                    "product_id": {
                        "type": "string",
                        "description": "Optional product_id to limit review search to one product",
                    },
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_product_details",
            "description": "Get detailed technical specifications for a single product ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_id": {
                        "type": "string",
                        "description": "The product code, e.g. 'lap-001'",
                    }
                },
                "required": ["product_id"],
            },
        },
    },
]
