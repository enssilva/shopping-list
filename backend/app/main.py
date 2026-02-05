from fastapi import FastAPI
from app.api.v1.api import api_router
from app.db.session import engine
from app.db import base
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy.orm import Session
from app.db.session import SessionLocal, engine
from app.models.user import User as UserModel
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_admin_user():
    db: Session = SessionLocal()
    try:
        # Verifica se o admin já existe
        admin = db.query(UserModel).filter(UserModel.email == "admin@admin.com").first()
        
        if not admin:
            print("Criando usuário administrador padrão...")
            password_plain = "admin"
            hashed_pw = pwd_context.hash(password_plain)
            new_admin = UserModel(
                full_name="Administrator",
                email="admin@admin.com",
                hashed_password=hashed_pw,
            )
            db.add(new_admin)
            db.commit()
            print("Usuário admin@admin.com criado com sucesso!")
    except Exception as e:
        print(f"Erro ao criar admin: {e}")
    finally:
        db.close()


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

# Executa ao iniciar o servidor
@app.on_event("startup")
def startup_event():
    # Cria as tabelas se não existirem (incluindo o índice FTS se configurado)
    # Base.metadata.create_all(bind=engine) 
    create_admin_user()