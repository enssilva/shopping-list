from fastapi import FastAPI
from app.api.v1.api import api_router
from app.db.session import engine
from app.db import base
from fastapi.middleware.cors import CORSMiddleware

# This command creates the tables in the database if they don't exist
# Note: In production, we usually use Alembic migrations instead of this
base.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Grocery Shopping List API",
    description="Backend for price comparison and shopping list management",
    version="1.0.0"
)

origins = [
    "http://localhost:9000", # Quasar Dev Port
    "http://localhost",      # Nginx Port
    "https://localhost:9000",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Allow all methods (GET, POST, etc.)
    allow_headers=["*"], # Allow all headers
)

# Include all V1 routes
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"message": "Grocery API is running smoothly"}