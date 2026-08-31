from beanie import init_beanie
from pymongo import AsyncMongoClient
from app.schemas.products import Product
from app.core.config import app_settings
import logging

logger = logging.getLogger("database config")

async def init_db():
    client = AsyncMongoClient(app_settings.mongo_uri)
    await init_beanie(
        database=client[app_settings.db_name],
        document_models=[
            Product
        ]
    )
    logger.info("Database initialized successfully")
    
    