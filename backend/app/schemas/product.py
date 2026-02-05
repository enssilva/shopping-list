from pydantic import BaseModel
from typing import Optional, List
from app.schemas.product_price import ProductPrice

class ProductBase(BaseModel):
    barcode: str
    name: str
    image_path: Optional[str] = None

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    barcode: Optional[str] = None
    name: Optional[str] = None
    image_path: Optional[str] = None

class Product(ProductBase):
    id: int
    prices: List[ProductPrice] = []

    class Config:
        from_attributes = True