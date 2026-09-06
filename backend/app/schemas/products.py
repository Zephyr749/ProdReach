from pydantic import BaseModel, Field, ConfigDict, field_serializer
from beanie import Document, Indexed, PydanticObjectId
from datetime import datetime, UTC
from typing import Optional, List

# --- Embedded Models (BaseModels) ---

class TimeStamps(BaseModel):
    """Base model to include timestamp fields."""
    createdAt: datetime = Field(default_factory=lambda: datetime.now(UTC), description="Record creation time")
    updatedAt: datetime = Field(default_factory=lambda: datetime.now(UTC), description="Last update time")
    deletedAt: Optional[datetime] = Field(None, description="Soft deletion timestamp") 
    

class Review(BaseModel):
    rating: Optional[float | int] = Field(..., description="Customer ratings (e.g. 5, 3.5)")
    text: Optional[str] = Field(..., description="Review text content")
    embedding: Optional[List[float]] = Field(
        default= None,
        description= "Cached 1536-dim vector embedding of the review"
    )
    
class Seller(BaseModel):
    type: Optional[str] = Field(default="marketplace_synthatic")
    region: Optional[str] = Field(default="India")

class ProductSpecification(BaseModel):
    """
    Common specs across categories.
    extra='allow' allows category-specific specs (e.g. display_in, camera_mp for phones,
    or usbc_charging for laptops) without failing validation.
    """
    model_config = ConfigDict(extra="allow")
    ram_gb: int | None = None
    storage_gb: int | None = None
    display_in: float | None = None
    refresh_hz: int | None = None
    battery_mah: int | None = None
    battery_hours: float | None = None
    camera_mp: int | None = None
    wifi: str | None = None
    nfc: bool | None = None

class Product(Document):
    model_config = ConfigDict(
        populate_by_name = True,
        serialize_by_alias=True,
        arbitrary_types_allowed= True
    )
    
    # Maps MongoDB's '_id' to a string
    product_id: str = Field(..., description= "Unique product code (e.g. 'sma-001')")
    category: str = Field(..., description= "Product category (e.g. 'smartphone')")
    brand: str = Field(..., description= "Brand name (e.g. 'Samsung')")
    name: str = Field(..., description= "Full product name")
    specifications: ProductSpecification = Field(..., description="Product specifications")
    price_inr: int = Field(..., description= "Price in Indian rupee")
    availability: str = Field(..., description= "Stock availability (e.g. 'in_stock')")
    market: str = Field(..., description= "Country market")
    description: str = Field(..., description= "Product description")
    reviews: Optional[List[Review]] = Field(default_factory= List, description= "Product reviews")
    seller: Optional[Seller] = Field(default_factory=Seller)
    
    # @field_serializer("mongo_id", when_used= "always")
    # def serialize_object_id(self, v: Optional[PydanticObjectId]) -> Optional[str]:
    #     return str(v) if v is not None else None
    
    class Settings:
        name = "products"
        
    
