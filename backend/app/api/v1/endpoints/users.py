from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.models.user import User as UserModel
from app.schemas.user import User, UserCreate
from passlib.context import CryptContext
from app.api.deps import get_current_user

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/", response_model=User)
def create_user(user_in: UserCreate, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    """
    Register a new user using email and password.
    """
    # Check if a user with this email already exists
    existing_user = db.query(UserModel).filter(UserModel.email == user_in.email).first()
    if existing_user:
        raise HTTPException(
            status_code=400, 
            detail="A user with this email already exists."
        )

    # Create new user instance (ignoring the login field)
    new_user = UserModel(
        email=user_in.email,
        full_name=user_in.full_name,
        hashed_password=pwd_context.hash(user_in.password)  # Note: Use hashing in production!
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.get("/", response_model=List[User])
def list_users(db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    """
    Retrieve the list of all registered users.
    """
    return db.query(UserModel).all()

@router.get("/me", response_model=User)
def get_user_me(current_user: UserModel = Depends(get_current_user)):
    # Retorna os dados de quem é o dono do token
    return current_user