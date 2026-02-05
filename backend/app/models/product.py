from sqlalchemy import Column, Integer, String, Index, text
from sqlalchemy.orm import relationship
from app.db.session import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    barcode = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    image_path = Column(String, nullable=True)

    # Relationships
    prices = relationship(
        "ProductPrice", 
        back_populates="product", 
        cascade="all, delete-orphan"
    )

    # Índice atualizado para usar a função imutável
    __table_args__ = (
        Index(
            "idx_product_fts",
            text("to_tsvector('portuguese', unaccent_immutable(name))"), # Alterado aqui
            postgresql_using="gin",
        ),
    )