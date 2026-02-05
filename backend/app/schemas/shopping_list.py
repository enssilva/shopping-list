from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from app.schemas.product import Product

# --- Shopping List Item Schemas ---

class ShoppingListItemBase(BaseModel):
    product_id: int
    quantity: int = 1
    is_checked: bool = False

class ShoppingListItemCreate(ShoppingListItemBase):
    shopping_list_id: int

class ShoppingListItemUpdate(BaseModel):
    quantity: Optional[int] = None
    is_checked: Optional[bool] = None

class ShoppingListItem(ShoppingListItemBase):
    id: int
    product: Product
    
    class Config:
        from_attributes = True

# --- Shopping List Schemas ---

class ShoppingListBase(BaseModel):
    name: str
    description: Optional[str] = None

class ShoppingListCreate(ShoppingListBase):
    user_id: int

class ShoppingList(ShoppingListBase):
    id: int
    user_id: int
    created_at: datetime
    items: List[ShoppingListItem] = [] # Nested items included in the response

    class Config:
        from_attributes = True