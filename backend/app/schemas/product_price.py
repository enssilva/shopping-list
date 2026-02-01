from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from app.schemas.market import Market

# Common properties
class ProductPriceBase(BaseModel):
    price: float = Field(..., gt=0, description="The price must be greater than zero")

# Properties to receive on creation/update
class ProductPriceUpdate(ProductPriceBase):
    product_id: int
    market_id: int

# Properties to return to the client
class ProductPrice(ProductPriceBase):
    id: int
    product_id: int
    market_id: int
    updated_at: datetime
    market: Optional[Market] = None

    class Config:
        from_attributes = True