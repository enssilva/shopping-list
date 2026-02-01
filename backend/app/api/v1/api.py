from fastapi import APIRouter
from app.api.v1.endpoints import markets, products, prices, users, shopping_lists, auth

api_router = APIRouter()
# Authentication routes usually come first or are tagged specifically
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(markets.router, prefix="/markets", tags=["Markets"])
api_router.include_router(products.router, prefix="/products", tags=["Products"])
api_router.include_router(prices.router, prefix="/prices", tags=["Prices"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(shopping_lists.router, prefix="/lists", tags=["Shopping Lists"])