from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.models.product import Product as ProductModel
from app.schemas.product import Product, ProductCreate, ProductUpdate

router = APIRouter()

@router.post("/", response_model=Product)
def create_product(product_in: ProductCreate, db: Session = Depends(get_db)):
    # Check if barcode already exists
    existing = db.query(ProductModel).filter(ProductModel.barcode == product_in.barcode).first()
    if existing:
        raise HTTPException(status_code=400, detail="Product with this barcode already exists")
    
    new_product = ProductModel(**product_in.model_dump())
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product

@router.get("/", response_model=List[Product])
def get_all_products(db: Session = Depends(get_db)):
    return db.query(ProductModel).all()

@router.get("/search", response_model=List[Product])
def search_products(q: str, db: Session = Depends(get_db)):
    """
    Search products by name or barcode for quick adding.
    """
    return db.query(ProductModel).filter(
        (ProductModel.name.ilike(f"%{q}%")) | 
        (ProductModel.barcode.ilike(f"%{q}%"))
    ).limit(10).all()

@router.get("/barcode/{barcode}", response_model=Product)
def get_product_by_barcode(barcode: str, db: Session = Depends(get_db)):
    """
    Search for a product using its barcode string.
    """
    product = db.query(ProductModel).filter(ProductModel.barcode == barcode).first()
    
    if not product:
        # Returning 404 triggers the "New Product" logic in the frontend
        raise HTTPException(status_code=404, detail="Product not found")
        
    return product

@router.delete("/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    """
    Permanently removes a product from the database.
    """
    db_product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
    
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    try:
        db.delete(db_product)
        db.commit()
        return {"message": f"Product {product_id} deleted successfully"}
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=400, 
            detail="Cannot delete product."
        )

@router.put("/{product_id}", response_model=Product)
def update_product(
    product_id: int, 
    product_in: ProductUpdate, 
    db: Session = Depends(get_db)
):
    # CORREÇÃO: Usar ProductModel (SQLAlchemy) e não Product (Schema)
    db_product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
    
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # CORREÇÃO: Usar model_dump para Pydantic v2
    update_data = product_in.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_product, field, value)
    
    db.commit()
    db.refresh(db_product)
    return db_product