import jwt
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException
from passlib.context import CryptContext
from app.models import Admin
from app.database import SessionLocal
from sqlalchemy.orm import Session

# Chave secreta para gerar e verificar tokens JWT
SECRET_KEY = "secreta_toke_de_sistema"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 200  # Tempo de expiração do token

# Contexto para criptografar senhas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_admin_by_username(db: Session, username: str):
    return db.query(Admin).filter(Admin.username == username).first()

def authenticate_admin(db: Session, username: str, password: str):
    admin = get_admin_by_username(db, username)
    if not admin or not verify_password(password, admin.password):
        raise HTTPException(
            status_code=401,
            detail="Credenciais inválidas",
        )
    return admin

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
