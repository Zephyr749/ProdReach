from app.core.db import init_db
from app.schemas.products import Product
from typing import List, Any
import asyncio


async def ratings_float_converter():
    await init_db()
    all_products: List[Product] = await Product.find_all().to_list()
    
    for prod in all_products:
        print(prod.name)
        
    
    
asyncio.run(ratings_float_converter())