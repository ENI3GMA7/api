from fastapi import APIRouter, Depends, HTTPException, Form, UploadFile, Request
from sqlalchemy.orm import Session
from app.models import MenuItem, Admin
from app.schemas import MenuItemCreate, MenuItemUpdate, MenuItemResponse
from app.auth import authenticate_admin, create_access_token, get_db
from datetime import timedelta
import os
import shutil
import uuid

router = APIRouter()

# Pasta para armazenar as imagens
UPLOAD_FOLDER = "items"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def get_current_admin(db: Session = Depends(get_db), username: str = Form(...), password: str = Form(...)):
    admin = authenticate_admin(db, username, password)
    return admin

@router.post("/login", response_model=str)
async def login(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    admin = authenticate_admin(db, username, password)
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": admin.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/menu-adicionar/", response_model=MenuItemResponse)
async def add_menu_item(
    request: Request,
    name: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    category: str = Form(...),
    image: UploadFile = None,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    image_path = None
    if image:
        # Gera um nome único para o arquivo
        unique_filename = f"{uuid.uuid4().hex}_{image.filename}"
        image_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        
        # Salva a imagem na pasta
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
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
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
        image_path = os.path.join(UPLOAD_FOLDER, image.filename)
        with open(image_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        menu_item.image = image_path

    db.commit()
    db.refresh(menu_item)
    return menu_item


# Rota para retornar os dados do administrador logado
@router.get("/admin/dados", response_model=dict)
async def get_admin_data(current_admin: Admin = Depends(get_current_admin)):
    return {
        "id": current_admin.id,
        "username": current_admin.username,
        "password": current_admin.password  # Você pode não querer retornar a senha
    }



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
