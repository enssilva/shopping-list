from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# Common properties shared across schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None

# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str

# Properties to return via API (Response)
class User(UserBase):
    id: int
    created_at: datetime

    class Config:
        # Allows Pydantic to interface with SQLAlchemy models
        from_attributes = True