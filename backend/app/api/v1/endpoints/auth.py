from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User as UserModel
from app.schemas.auth import LoginRequest, LoginResponse
from passlib.context import CryptContext
from app.core.security import create_access_token, pwd_context

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/login", response_model=LoginResponse)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate a user and return their basic profile.
    """
    # 1. Find the user by email
    user = db.query(UserModel).filter(UserModel.email == login_data.email).first()
    
    # 2. Check if user exists and password matches
    # Note: In production, use pwd_context.verify(login_data.password, user.hashed_password)
    # 2. CORREÇÃO: Usa o método verify para comparar a senha plana com o hash
    if not user or not pwd_context.verify(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorretos"
        )

    # 2. Gera o Token JWT
    access_token = create_access_token(data={"sub": user.email, "id": user.id})
    
    # 3. Retorna o token e os dados do usuário para o Quasar
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }