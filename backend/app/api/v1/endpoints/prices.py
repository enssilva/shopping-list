from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from datetime import datetime
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
    # 1. Validação manual para evitar erros 500/CORS
    if price_in.market_id is None:
        raise HTTPException(status_code=400, detail="market_id is required")

    # 2. Converter o Schema para dicionário (mapping)
    # O exclude_unset=True evita sobrescrever campos com None se não forem enviados
    price_data = price_in.model_dump(exclude_unset=True)

    # 3. Verificar existência
    existing_price = db.query(PriceModel).filter(
        PriceModel.product_id == price_in.product_id,
        PriceModel.market_id == price_in.market_id
    ).first()

    try:
        if existing_price:
            # Lógica: Se o front não enviou data, forçamos 'agora'
            if "updated_at" not in price_data:
                existing_price.updated_at = datetime.now()
            
            # Aplicar os campos dinamicamente
            for field, value in price_data.items():
                setattr(existing_price, field, value)
            
            db.commit()
            db.refresh(existing_price)
            return existing_price
        
        # 4. Criar novo (usando o dicionário corrigido)
        new_price = PriceModel(**price_data)
        db.add(new_price)
        db.commit()
        db.refresh(new_price)
        return new_price

    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Database integrity error")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[ProductPrice])
def list_all_prices(db: Session = Depends(get_db)):
    return db.query(PriceModel).all()

@router.get("/product/{product_id}", response_model=List[ProductPrice])
def get_prices_by_product(product_id: int, db: Session = Depends(get_db)):
    # Incluindo o market para evitar 'Unknown Market' no front
    return db.query(PriceModel).options(joinedload(PriceModel.market)).filter(PriceModel.product_id == product_id).all()

@router.get("/history/{product_id}", response_model=List[ProductPrice])
def get_price_history(product_id: int, db: Session = Depends(get_db)):
    return db.query(PriceModel).options(
        joinedload(PriceModel.market)
    ).filter(PriceModel.product_id == product_id).order_by(PriceModel.updated_at.desc()).all()