from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List
from app.db.session import get_db
from app.models.shopping_list import ShoppingList as ListModel
from app.models.shopping_list_item import ShoppingListItem as ItemModel
from app.schemas import shopping_list as schemas

router = APIRouter()

# --- List Management ---

@router.post("/", response_model=schemas.ShoppingList)
def create_shopping_list(list_in: schemas.ShoppingListCreate, db: Session = Depends(get_db)):
    """
    Create a new shopping list for a specific user.
    """
    new_list = ListModel(**list_in.model_dump())
    db.add(new_list)
    db.commit()
    db.refresh(new_list)
    return new_list

@router.get("/{user_id}", response_model=List[schemas.ShoppingList])
def get_user_shopping_lists(user_id: int, db: Session = Depends(get_db)):
    """
    Retrieve all shopping lists belonging to a user.
    """
    return db.query(ListModel).filter(ListModel.user_id == user_id).all()

@router.get("/details/{list_id}", response_model=schemas.ShoppingList)
def get_list_details(list_id: int, db: Session = Depends(get_db)):
    """
    Retrieve details of a specific shopping list including its items.
    """
    db_list = db.query(ListModel).options(
        joinedload(ListModel.items).joinedload(ItemModel.product)
    ).filter(ListModel.id == list_id).first()
    if not db_list:
        raise HTTPException(status_code=404, detail="List not found")
    return db_list

# --- Item Management ---

@router.post("/items", response_model=schemas.ShoppingListItem)
def add_item_to_list(item_in: schemas.ShoppingListItemCreate, db: Session = Depends(get_db)):
    """
    Add a product to an existing shopping list.
    """
    new_item = ItemModel(**item_in.model_dump())
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item

@router.patch("/items/{item_id}", response_model=schemas.ShoppingListItem)
def update_item_quantity(
    item_id: int, 
    quantity: int, 
    db: Session = Depends(get_db)
):
    """
    Update the quantity of a specific item in the shopping list.
    """
    db_item = db.query(ItemModel).filter(ItemModel.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    if quantity < 1:
        raise HTTPException(status_code=400, detail="Quantity must be at least 1")

    db_item.quantity = quantity
    db.commit()
    db.refresh(db_item)
    return db_item

@router.delete("/items/{item_id}")
def delete_shopping_list_item(
    item_id: int, 
    db: Session = Depends(get_db)
):
    """
    Remove a specific item from a shopping list.
    """
    # 1. Search for the item in the database
    db_item = db.query(ItemModel).filter(ItemModel.id == item_id).first()
    
    # 2. If not found, raise a 404 error
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found on this list")
    
    # 3. Perform the deletion
    db.delete(db_item)
    db.commit()
    
    return {"message": "Item successfully removed from list"}