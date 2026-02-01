# Import the Base class and all models here
# This is used by Alembic to discover the database schema
from app.db.session import Base
from app.models.user import User
from app.models.product import Product
from app.models.market import Market
from app.models.product_price import ProductPrice
from app.models.shopping_list import ShoppingList
from app.models.shopping_list_item import ShoppingListItem