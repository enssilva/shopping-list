from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List
from app.db.session import get_db
from app.models.product_price import ProductPrice as PriceModel
from app.schemas.product_price import ProductPrice, ProductPriceUpdate

router = APIRouter()

@router.post("/", response_model=ProductPrice)
def update_or_create_price(price_in: ProductPriceUpdate, db: Session = Depends(get_db)):
    """
    Update a product price if it exists for a specific market, 
    otherwise create a new record.
    """
    # Check if this product already has a price in this market
    existing_price = db.query(PriceModel).filter(
        PriceModel.product_id == price_in.product_id,
        PriceModel.market_id == price_in.market_id
    ).first()

    if existing_price:
        # Update existing price
        existing_price.price = price_in.price
        db.commit()
        db.refresh(existing_price)
        return existing_price
    
    # Create new price record
    new_price = PriceModel(**price_in.model_dump())
    db.add(new_price)
    db.commit()
    db.refresh(new_price)
    return new_price

@router.get("/", response_model=List[ProductPrice])
def list_all_prices(db: Session = Depends(get_db)):
    """
    Retrieve all prices recorded in the system.
    """
    return db.query(PriceModel).all()

@router.get("/product/{product_id}", response_model=List[ProductPrice])
def get_prices_by_product(product_id: int, db: Session = Depends(get_db)):
    """
    Retrieve all price history for a specific product.
    """
    return db.query(PriceModel).filter(PriceModel.product_id == product_id).all()

@router.get("/history/{product_id}", response_model=List[ProductPrice])
def get_price_history(product_id: int, db: Session = Depends(get_db)):
    """
    Returns all recorded prices for a product, including market details.
    """
    return db.query(PriceModel).options(
        joinedload(PriceModel.market) # Garante que o nome do mercado venha junto
    ).filter(PriceModel.product_id == product_id).order_by(PriceModel.updated_at.desc()).all()