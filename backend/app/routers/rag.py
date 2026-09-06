from fastapi import APIRouter
from pydantic import BaseModel
from app.services.vector_search import search_relevant_reviews
from app.services.products import ask_questions


router = APIRouter(prefix= "/api/rag", tags= ["RAG"])


class AskReviewRequest(BaseModel):
    product_id: str
    question: str
    

@router.post("/ask")
async def ask_product_review(req: AskReviewRequest):
    # 1. Retrieve top 3 relevant review chunks
    top_reviews = search_relevant_reviews(
        query= req.question,
        product_ids= [req.product_id],
        top_k= 3
    )
    
    answer = await ask_questions(top_reviews, req.question)
    
    return {
        "question": req.question,
        "product_id": req.product_id,
        "answer": answer,
        "retrieved_evidence": [
            {"review": chunk.review_text, "similarity": round(score, 3)}
            for chunk, score in top_reviews
        ]
    }
    