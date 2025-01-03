import os
import shutil
from fastapi import APIRouter, HTTPException, Depends, UploadFile, Form,Request
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import MenuItem
from app.schemas import MenuItemCreate, MenuItemUpdate, MenuItemResponse
import shutil
import uuid

router = APIRouter()

# Pasta para armazenar as imagens
UPLOAD_FOLDER = "items"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

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


@router.get("/menu-landingpage", response_model=list[MenuItemResponse])
def get_menu_items(db: Session = Depends(get_db)):
    return db.query(MenuItem).all()

