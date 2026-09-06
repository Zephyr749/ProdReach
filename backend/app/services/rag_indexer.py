from app.ai.embeddings import get_embedding
from app.schemas.products import Product
from typing import List, Optional

class ReviewChunk:
    def __init__(self, product_id: str, product_name: str, review_text: str, rating: Optional[float], vector: List[float]):
        self.product_id = product_id
        self.product_name = product_name
        self.review_text = review_text
        self.rating = rating
        self.vector = vector


review_index: List[ReviewChunk] = []


# DO NOT USE THIS when using db products-->
def build_review_index(products: List[Product]):
    global review_index
    review_index.clear()
    
    review_index.extend(
        ReviewChunk(
            product_id= p.product_id,
            product_name= p.name,
            review_text= r.text,
            rating= r.rating,
            vector= get_embedding(r.text),
        )
        for p in products
        for r in (p.reviews or [])
        if r.text
    )
    
    print(f"Indexed {len(review_index)} reviews with vector embeddings")


async def initialize_rag_index():
    """Fetches all products from database and initializes the in-memory review vector index."""
    products = await Product.find_all().to_list()
    print(f"Loaded {len(products)} products from MongoDB.")

    newly_embedded_count = 0
    
    for p in products:
        product_modified = False
        
        for r in (p.reviews or []):
            if not r.text:
                continue
            
            # 1. Compute embeddings ONLY if not already saved in db
            if not r.embedding:
                print(f"Generating missing embedding for review in {p.name}...")
                r.embedding = get_embedding(r.text)
                product_modified = True
                newly_embedded_count += 1
                
            # 2. Add to in-memory search index
            review_index.append(
                ReviewChunk(
                    product_id= p.product_id,
                    product_name= p.name,
                    review_text= r.text,
                    rating= r.rating,
                    vector= r.embedding,
                )
            )
        # 3. Persist back to db for future use
        if product_modified:
            await p.save()
            
    if newly_embedded_count > 0:
        print(f" Computed and saved {newly_embedded_count} new review embeddings to MongoDB.")
    else:
        print(f"⚡ Loaded {len(review_index)} pre-computed embeddings from MongoDB (0 API calls).")
        
        
    # build_review_index(products)