import math
from app.ai.embeddings import get_embedding
from app.services.rag_indexer import review_index, ReviewChunk
from typing import List

def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    dot_product = sum(a * b for a, b in zip(v1, v2))
    magnitude_v1 = math.sqrt(sum(a * a for a in v1))
    magnitude_v2 = math.sqrt(sum(b * b for b in v2))
    
    if magnitude_v1 == 0 or magnitude_v2 == 0:
        return 0.0
    
    return dot_product / (magnitude_v1 * magnitude_v2)

def search_relevant_reviews(
    query: str,
    product_ids: List[str] | None = None,
    top_k: int = 3
) -> List[tuple[ReviewChunk, float]]:
    """
    Finds the top_k most semantically relevant reviews for a query.
    Optionally limits search to pre-filtered candidate product IDs.
    """
    
    query_vector = get_embedding(query)
    
    scored_chunks: List[tuple[ReviewChunk, float]] = []
    
    for chunk in review_index:
        # if candidate filtering is applied, skip other products
        if product_ids and chunk.product_id not in product_ids:
            continue
        
        score = cosine_similarity(query_vector, chunk.vector)
        scored_chunks.append((chunk, score))
    
    # Sort descending by similarity score
    scored_chunks.sort(key= lambda x: x[1], reverse= True)
    return scored_chunks[:top_k]