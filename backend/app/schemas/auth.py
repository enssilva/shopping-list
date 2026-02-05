from pydantic import BaseModel, EmailStr
from app.schemas.user import User

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: User # Define que os dados do usuário estão aninhados aqui

    class Config:
        from_attributes = True # Permite que o Pydantic leia objetos do SQLAlchemy