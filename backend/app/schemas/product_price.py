from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from app.schemas.market import Market

# Common properties
class ProductPriceBase(BaseModel):
    product_id: int
    market_id: int
    price: float = Field(..., gt=0, description="The price must be greater than zero")
    updated_at: Optional[datetime] = None
    market: Optional[Market] = None

# Properties to receive on creation/update
class ProductPriceUpdate(ProductPriceBase):
    product_id: int
    market_id: int

# Properties to return to the client
class ProductPrice(ProductPriceBase):
    id: int

    class Config:
        from_attributes = True