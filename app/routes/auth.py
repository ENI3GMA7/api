import jwt
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.models import Admin
from app.database import SessionLocal
from fastapi.security import OAuth2PasswordBearer

# Configurações do JWT
SECRET_KEY = "secreta_toke_de_sistema"  # Substitua por uma chave mais segura em produção
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 200  # Tempo de expiração do token em minutos






def get_db():
    """
    Obtém uma sessão de banco de dados para uso nas rotas.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
# Inicializa o esquema de autenticação
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/login")

# Contexto para criptografar senhas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Função para criar um token de acesso
def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)):
    """
    Cria um token JWT com um tempo de expiração.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Função para verificar a senha
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica se uma senha corresponde ao hash armazenado.
    """
    return pwd_context.verify(plain_password, hashed_password)

# Função para obter o admin pelo nome de usuário
def get_admin_by_username(db: Session, username: str) -> Admin:
    """
    Recupera um administrador pelo nome de usuário.
    """
    return db.query(Admin).filter(Admin.username == username).first()

# Função para autenticar o admin
def authenticate_admin(db: Session, username: str, password: str) -> Admin:
    """
    Autentica um administrador usando nome de usuário e senha.
    """
    admin = get_admin_by_username(db, username)
    if not admin or not verify_password(password, admin.password):
        raise HTTPException(
            status_code=401,
            detail="Credenciais inválidas",
        )
    return admin

# Função para obter o admin atual a partir do token
def get_current_admin(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> Admin:
    """
    Valida o token JWT e retorna o administrador associado.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Token inválido")
        
        admin = get_admin_by_username(db, username)
        if not admin:
            raise HTTPException(status_code=401, detail="Admin não encontrado")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado")
    except jwt.InvalidTokenError:  # Corrigido para lidar com tokens inválidos
        raise HTTPException(status_code=401, detail="Token inválido")
    return admin

# Função para hashear senhas
def get_password_hash(password: str) -> str:
    """
    Gera um hash seguro para a senha fornecida.
    """
    return pwd_context.hash(password)

# Dependência para obter uma sessão de banco de dados
def get_db():
    """
    Obtém uma sessão de banco de dados para uso em rotas.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
