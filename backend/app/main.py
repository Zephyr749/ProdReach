import uvicorn
from fastapi import FastAPI
from app.routers import requirements, products, recommendations, rag
from app.core import db
from app.services.rag_indexer import initialize_rag_index
from contextlib import asynccontextmanager
import logging


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await db.init_db()
    await initialize_rag_index()
    yield

app = FastAPI(title= "ProdReach", lifespan= lifespan)


app.include_router(requirements.router)
app.include_router(products.router)
app.include_router(recommendations.router)
app.include_router(rag.router)

@app.get("/")
def get_root():
    return {"message": "Hello World"}


if __name__== "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=4000, reload=True)
