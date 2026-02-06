import os
from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
from pydantic_settings import BaseSettings

# Classe para gerenciar as configurações de produção
class Settings(BaseSettings):
    # Em produção, o valor virá da variável de ambiente SECRET_KEY
    SECRET_KEY: str = os.getenv("SECRET_KEY", "chave-temporaria-so-para-dev")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 

settings = Settings()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data: dict):
    """Gera o token assinado usando as configurações da classe Settings"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    # Usamos settings.SECRET_KEY em vez da string fixa
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt