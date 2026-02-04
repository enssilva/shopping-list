from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.models.market import Market as MarketModel
from app.schemas.market import Market, MarketCreate, MarketUpdate

router = APIRouter()

@router.get("/", response_model=List[Market])
def read_markets(db: Session = Depends(get_db)):
    return db.query(MarketModel).all()

@router.post("/", response_model=Market)
def create_market(market_in: MarketCreate, db: Session = Depends(get_db)):
    new_market = MarketModel(**market_in.model_dump())
    db.add(new_market)
    db.commit()
    db.refresh(new_market)
    return new_market

@router.put("/{market_id}", response_model=Market)
def update_market(market_id: int, market_in: MarketUpdate, db: Session = Depends(get_db)):
    db_market = db.query(MarketModel).filter(MarketModel.id == market_id).first()
    if not db_market:
        raise HTTPException(status_code=404, detail="Market not found")
    
    update_data = market_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_market, field, value)
    
    db.commit()
    db.refresh(db_market)
    return db_market

@router.delete("/{market_id}")
def delete_market(market_id: int, db: Session = Depends(get_db)):
    """
    Remove a market and all its associated price history.
    """
    db_market = db.query(MarketModel).filter(MarketModel.id == market_id).first()
    
    if not db_market:
        raise HTTPException(status_code=404, detail="Market not found")
    
    try:
        db.delete(db_market)
        db.commit()
        return {"message": f"Market '{db_market.name}' and its prices deleted successfully"}
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500, 
            detail="Internal server error during market deletion"
        )