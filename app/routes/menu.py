from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Form,
    UploadFile,
    Request,
    Header,
)
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.models import MenuItem, Admin,Base
from app.schemas import MenuItemCreate, MenuItemUpdate, MenuItemResponse
from .auth import *
from datetime import timedelta
import os
import shutil
import uuid
import jwt
from .init import create_initial_admin 
from app.database import engine, SessionLocal

# Configuração do router
router = APIRouter()
Base.metadata.create_all(bind=engine)

# Cria os dados iniciais
def initialize():
    db = SessionLocal()
    try:
        create_initial_admin(db)
    finally:
        db.close()

# Inicialize os dados na primeira execução
initialize()
# Configuração da pasta para upload de imagens
UPLOAD_FOLDER = "items"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/login")

# Função para obter o admin atual a partir do token

@router.post("/login", response_model=dict)
async def login(
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    admin = authenticate_admin(db, username, password)
    if not admin:
        raise HTTPException(status_code=400, detail="Usuário ou senha inválidos")

    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": admin.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}



@router.post("/admin-adicionar/")
async def add_admin(
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
    
):
    # Verifica se o administrador já existe
    existing_admin = db.query(Admin).filter(Admin.username == username).first()
    if existing_admin:
        raise HTTPException(status_code=400, detail="Administrador já existe")

    hashed_password = get_password_hash(password)
    new_admin = Admin(username=username, email=email, password=hashed_password)
    
    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)
    return new_admin



@router.put("/admin-atualizar/{admin_id}")
async def update_admin(
    admin_id: int,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    # Verifica se o administrador existe
    admin = db.query(Admin).filter(Admin.id == admin_id).first()
    if not admin:
        raise HTTPException(status_code=404, detail="Administrador não encontrado")

    # Atualiza os dados do administrador
    admin.username = username
    admin.email = email
    admin.password = get_password_hash(password)
    
    db.commit()
    db.refresh(admin)
    return admin




@router.post("/menu-adicionar/")
async def add_menu_item(
    request: Request,
    name: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    category: str = Form(...),
    especial: bool = Form(False),
    image: UploadFile = None,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
):
    image_url = None
    if image:
        unique_filename = f"{uuid.uuid4().hex}_{image.filename}"
        image_path = os.path.join("items", unique_filename)  # Caminho de salvamento
        with open(image_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        image_url = f"{request.base_url}images/{unique_filename}"  # URL da imagem

    new_item = MenuItem(
        name=name, description=description, price=price, category=category, 
        image=image_url, especial=especial
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item






# Rota para editar um item do menu
@router.put("/menu-editar/{item_id}")
async def update_menu_item(
    item_id: int,
    name: str = Form(None),
    description: str = Form(None),
    price: float = Form(None),
    category: str = Form(None),
    image: UploadFile = None,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
):
    menu_item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if not menu_item:
        raise HTTPException(status_code=404, detail="Item não encontrado")

    if name:
        menu_item.name = name
    if description:
        menu_item.description = description
    if price:
        menu_item.price = price
    if category:
        menu_item.category = category

    if image:
        unique_filename = f"{uuid.uuid4().hex}_{image.filename}"
        image_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        with open(image_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        menu_item.image = image_path

    db.commit()
    db.refresh(menu_item)
    return menu_item



# Rota para obter dados do admin atual
@router.get("/admin/dados", response_model=dict)
async def get_admin_data(current_admin: Admin = Depends(get_current_admin)):
    return {
        "id": current_admin.id,
        "username": current_admin.username,
        "email": current_admin.email,
        
    }

# Rota para deletar um item do menu
@router.delete("/menu-deletar/{item_id}")
async def delete_menu_item(
    item_id: int, db: Session = Depends(get_db), current_admin: Admin = Depends(get_current_admin)
):
    menu_item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if not menu_item:
        raise HTTPException(status_code=404, detail="Item não encontrado")

    if menu_item.image and os.path.exists(menu_item.image):
        os.remove(menu_item.image)

    db.delete(menu_item)
    db.commit()
    return {"message": "Item deletado com sucesso"}





@router.get("/menu-items/", response_model=list[dict])
def get_menu_items(db: Session = Depends(get_db)):
    """
    Retorna todos os itens do menu com um dicionário detalhado.
    """
    menu_items = db.query(MenuItem).all()

    if not menu_items:
        raise HTTPException(status_code=404, detail="Nenhum item no menu encontrado")

    result = [
        {
            "id": item.id,
            "name": item.name,
            "description": item.description,
            "price": item.price,
            "category": item.category,
            "image": item.image or "Nenhuma imagem disponível",
        }
        for item in menu_items
    ]

    return result
