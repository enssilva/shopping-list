from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.db.session import Base

class Market(Base):
    __tablename__ = "markets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    address = Column(String)

    # Relationships
    prices = relationship(
        "ProductPrice", 
        back_populates="market",
        cascade="all, delete-orphan"
    )