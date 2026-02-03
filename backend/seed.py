from sqlalchemy.orm import Session
from app.db.session import SessionLocal, engine
from app.db import base
from app.models.user import User
from app.models.product import Product
from app.models.market import Market
from app.models.product_price import ProductPrice
from app.models.shopping_list import ShoppingList
from app.models.shopping_list_item import ShoppingListItem

def generate_ean13(code: str) -> str:
    """Calcula o dígito verificador para transformar 12 dígitos em um EAN-13 válido."""
    if len(code) != 12:
        return code.ljust(13, '0')
    
    # Lógica de cálculo do dígito verificador EAN-13
    sum_odd = sum(int(code[i]) for i in range(0, 12, 2))
    sum_even = sum(int(code[i]) for i in range(1, 12, 2))
    total = sum_odd + (sum_even * 3)
    check_digit = (10 - (total % 10)) % 10
    return f"{code}{check_digit}"

def seed_db():
    db = SessionLocal()
    base.Base.metadata.create_all(bind=engine)

    try:
        # 1. Usuário Admin
        admin = db.query(User).filter(User.email == "admin@admin.com").first()
        if not admin:
            admin = User(email="admin@admin.com", hashed_password="admin", full_name="Ebenezer Admin")
            db.add(admin)
            db.flush()

        # 2. Mercados
        market_names = ["Supermercado Vitória", "Carrefour", "Extra"]
        markets = []
        for name in market_names:
            m = db.query(Market).filter(Market.name == name).first()
            if not m:
                m = Market(name=name, address=f"Endereço {name}, Vitória")
                db.add(m)
                db.flush()
            markets.append(m)

        # 3. Produtos com EAN-13 Válidos
        # Usamos 12 dígitos base e a função gera o 13º (verificador)
        products_data = [
            ("789100010001", "Arroz Tio João 5kg"), ("789100010002", "Feijão Camil 1kg"),
            ("789100010003", "Açúcar União 1kg"), ("789100010004", "Café Pilão 500g"),
            ("789100010005", "Leite Ninho 1L"), ("789100010006", "Óleo de Soja 900ml"),
            ("789100010007", "Macarrão Adria 500g"), ("789100010008", "Detergente Ypê"),
            ("789100010009", "Sabonete Dove"), ("789100010010", "Creme Dental Colgate")
        ]
        
        db_products = []
        for base_code, name in products_data:
            valid_barcode = generate_ean13(base_code) # Gera código válido
            p = db.query(Product).filter(Product.barcode == valid_barcode).first()
            if not p:
                p = Product(barcode=valid_barcode, name=name)
                db.add(p)
                db.flush()
            db_products.append(p)

        # 4. Preços Variados
        import random
        for p in db_products:
            # Adiciona preços em 1 ou 2 mercados aleatórios
            chosen_markets = random.sample(markets, random.randint(1, 2))
            for m in chosen_markets:
                exists = db.query(ProductPrice).filter_by(product_id=p.id, market_id=m.id).first()
                if not exists:
                    price_val = round(random.uniform(3.50, 28.90), 2)
                    db.add(ProductPrice(product_id=p.id, market_id=m.id, price=price_val))

        db.commit()
        print("Database seeded with VALID EAN-13 codes!")
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_db()