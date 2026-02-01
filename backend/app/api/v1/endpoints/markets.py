from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.models.market import Market as MarketModel
from app.schemas.market import Market, MarketCreate

router = APIRouter()

@router.post("/", response_model=Market)
def create_market(market_in: MarketCreate, db: Session = Depends(get_db)):
    """
    Register a new market.
    """
    new_market = MarketModel(
        name=market_in.name,
        address=market_in.address
    )
    db.add(new_market)
    db.commit()
    db.refresh(new_market)
    return new_market

@router.get("/", response_model=List[Market])
def list_markets(db: Session = Depends(get_db)):
    """
    Retrieve all registered markets.
    """
    return db.query(MarketModel).all()

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