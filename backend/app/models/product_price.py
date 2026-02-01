from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base

class ProductPrice(Base):
    __tablename__ = "product_prices"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    market_id = Column(Integer, ForeignKey("markets.id", ondelete="CASCADE"), nullable=False)
    price = Column(Float, nullable=False)
    updated_at = Column(DateTime(timezone=True), index=True, server_default=func.now(), onupdate=func.now())

    # Relationships
    product = relationship("Product", back_populates="prices")
    market = relationship("Market", back_populates="prices")

    # Ensures one price per product per market
    __table_args__ = (
        UniqueConstraint('product_id', 'market_id', name='uq_product_market'),
        CheckConstraint('price > 0', name='check_price_positive'),
    )