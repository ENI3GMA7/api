import os
import shutil
from fastapi import APIRouter, HTTPException, Depends, UploadFile, Form,Request
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import MenuItem
from app.schemas import MenuItemCreate, MenuItemUpdate, MenuItemResponse
import shutil
import uuid
from passlib.context import CryptContext

# Contexto de hash para senhas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
router = APIRouter()




def hash_password(password: str) -> str:
    return pwd_context.hash(password)


# Pasta para armazenar as imagens
UPLOAD_FOLDER = "items"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.mount("/images", StaticFiles(directory=UPLOAD_FOLDER), name="images")
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/menu-adicinar/", response_model=MenuItemResponse)
async def add_menu_item(
    request: Request,
    name: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    category: str = Form(...),
    image: UploadFile = None,
    db: Session = Depends(get_db)
):
    image_path = None
    if image:
        # Gera um nome único para o arquivo
        unique_filename = f"{uuid.uuid4().hex}_{image.filename}"
        image_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        
        # Salva a imagem na pasta 'socinho'
        with open(image_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

        # Constrói a URL da imagem
        image_url = f"{request.base_url}images/{unique_filename}"
    else:
        image_url = None

    new_item = MenuItem(name=name, description=description, price=price, category=category, image=image_url)
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item

@router.put("/menu-editar/{item_id}", response_model=MenuItemResponse)
async def update_menu_item(
    item_id: int,
    name: str = Form(None),
    description: str = Form(None),
    price: float = Form(None),
    category: str = Form(None),
    image: UploadFile = None,  # Atualizado para 'image'
    db: Session = Depends(get_db)
):
    menu_item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if not menu_item:
        raise HTTPException(status_code=404, detail="Item not found")

    if name:
        menu_item.name = name
    if description:
        menu_item.description = description
    if price:
        menu_item.price = price
    if category:
        menu_item.category = category

    if image:
        image_path = os.path.join(UPLOAD_FOLDER, image.filename)
        with open(image_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        menu_item.image = image_path

    db.commit()
    db.refresh(menu_item)
    return menu_item

@router.delete("/menu-deletar/{item_id}")
def delete_menu_item(item_id: int, db: Session = Depends(get_db)):
    menu_item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if not menu_item:
        raise HTTPException(status_code=404, detail="Item not found")

    if menu_item.image and os.path.exists(menu_item.image):
        os.remove(menu_item.image)

    db.delete(menu_item)
    db.commit()
    return {"message": "Item deleted successfully"}







# Rota para adicionar um administrador
@router.post("/admin/adicionar", response_model=dict)
async def add_admin(
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    # Verifica se o username já existe
    existing_admin = db.query(Admin).filter(Admin.username == username).first()
    if existing_admin:
        raise HTTPException(status_code=400, detail="Usuário já existe.")
    
    # Cria o novo administrador
    hashed_password = hash_password(password)
    new_admin = Admin(username=username, password=hashed_password)
    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)

    return {"message": "Administrador adicionado com sucesso!", "admin_id": new_admin.id}

# Rota para atualizar um administrador
@router.put("/admin/atualizar/{admin_id}", response_model=dict)
async def update_admin(
    admin_id: int,
    username: str = Form(None),
    password: str = Form(None),
    db: Session = Depends(get_db)
):
    # Busca o administrador pelo ID
    admin = db.query(Admin).filter(Admin.id == admin_id).first()
    if not admin:
        raise HTTPException(status_code=404, detail="Administrador não encontrado.")

    # Atualiza os dados fornecidos
    if username:
        # Verifica se o novo username já existe para outro admin
        existing_admin = db.query(Admin).filter(Admin.username == username, Admin.id != admin_id).first()
        if existing_admin:
            raise HTTPException(status_code=400, detail="Outro administrador já utiliza este nome de usuário.")
        admin.username = username

    if password:
        admin.password = hash_password(password)

    # Salva as alterações no banco de dados
    db.commit()
    db.refresh(admin)

    return {"message": "Administrador atualizado com sucesso!", "admin_id": admin.id}



@router.get("/mostrar-cardapio-prato", response_model=list[MenuItemResponse])
def get_menu_items(db: Session = Depends(get_db)):
    return db.query(MenuItem).all()

