from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.models.user import User as UserModel
from app.schemas.user import User, UserCreate

router = APIRouter()

@router.post("/", response_model=User)
def create_user(user_in: UserCreate, db: Session = Depends(get_db)):
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
        hashed_password=user_in.password  # Note: Use hashing in production!
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.get("/", response_model=List[User])
def list_users(db: Session = Depends(get_db)):
    """
    Retrieve the list of all registered users.
    """
    return db.query(UserModel).all()