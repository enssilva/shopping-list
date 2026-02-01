from sqlalchemy.orm import Session
from app.db.session import SessionLocal, engine
from app.db import base
from app.models.user import User
from app.models.product import Product
from app.models.market import Market
from app.models.product_price import ProductPrice
from app.models.shopping_list import ShoppingList
from app.models.shopping_list_item import ShoppingListItem

def seed_db():
    db = SessionLocal()
    # Cria as tabelas se não existirem
    base.Base.metadata.create_all(bind=engine)

    try:
        # 1. Usuário Admin
        admin = db.query(User).filter(User.email == "admin@admin.com").first()
        if not admin:
            admin = User(email="admin@admin.com", hashed_password="admin", full_name="Ebenezer Admin")
            db.add(admin)
            db.flush() # Para pegar o ID

        # 2. Mercados (3 unidades)
        markets = [
            Market(name="Supermercado Vitória", address="Av. Dante Michelini, Vitória"),
            Market(name="Carrefour", address="Shopping Vitória"),
            Market(name="Extra", address="Enseada do Suá")
        ]
        for m in markets:
            if not db.query(Market).filter(Market.name == m.name).first():
                db.add(m)
        db.flush()

        # 3. Produtos (10 unidades)
        products_data = [
            ("78910001", "Arroz Tio João 5kg"), ("78910002", "Feijão Camil 1kg"),
            ("78910003", "Açúcar União 1kg"), ("78910004", "Café Pilão 500g"),
            ("78910005", "Leite Ninho 1L"), ("78910006", "Óleo de Soja 900ml"),
            ("78910007", "Macarrão Adria 500g"), ("78910008", "Detergente Ypê"),
            ("78910009", "Sabonete Dove"), ("78910010", "Creme Dental Colgate")
        ]
        products = []
        for barcode, name in products_data:
            p = db.query(Product).filter(Product.barcode == barcode).first()
            if not p:
                p = Product(barcode=barcode, name=name)
                db.add(p)
            products.append(p)
        db.flush()

        # 4. Preços (13 registros)
        # Distribuindo preços variados entre os mercados
        existing_markets = db.query(Market).all()
        prices = [
            (products[0].id, existing_markets[0].id, 25.90),
            (products[0].id, existing_markets[1].id, 27.50),
            (products[1].id, existing_markets[0].id, 8.40),
            (products[1].id, existing_markets[2].id, 7.90),
            (products[2].id, existing_markets[1].id, 4.20),
            (products[4].id, existing_markets[0].id, 5.50),
            (products[4].id, existing_markets[1].id, 5.80),
            (products[4].id, existing_markets[2].id, 5.30),
            (products[5].id, existing_markets[0].id, 6.70),
            (products[6].id, existing_markets[2].id, 3.90),
            (products[7].id, existing_markets[1].id, 2.20),
            (products[8].id, existing_markets[0].id, 3.50),
            (products[9].id, existing_markets[1].id, 4.80)
        ]
        for p_id, m_id, val in prices:
            exists = db.query(ProductPrice).filter_by(product_id=p_id, market_id=m_id).first()
            if not exists:
                db.add(ProductPrice(product_id=p_id, market_id=m_id, price=val))

        # 5. Lista de Compras
        my_list = db.query(ShoppingList).filter(ShoppingList.name == "Compra do Mês").first()
        if not my_list:
            my_list = ShoppingList(name="Compra do Mês", user_id=admin.id)
            db.add(my_list)
            db.flush()
            # Adicionando 2 itens iniciais à lista
            db.add(ShoppingListItem(shopping_list_id=my_list.id, product_id=products[0].id, quantity=1))
            db.add(ShoppingListItem(shopping_list_id=my_list.id, product_id=products[1].id, quantity=2))

        db.commit()
        print("Database seeded successfully!")
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_db()