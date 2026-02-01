from pydantic import BaseModel
from typing import Optional

class ProductBase(BaseModel):
    barcode: str
    name: str
    image_path: Optional[str] = None

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: int

    class Config:
        from_attributes = True