from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import MenuItem
from app.schemas import MenuItemCreate, MenuItemUpdate, MenuItemResponse

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/menu-items", response_model=list[MenuItemResponse])
def get_menu_items(db: Session = Depends(get_db)):
    return db.query(MenuItem).all()

@router.post("/menu-items", response_model=MenuItemResponse)
def add_menu_item(item: MenuItemCreate, db: Session = Depends(get_db)):
    new_item = MenuItem(**item.dict())
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item

@router.put("/menu-items/{item_id}", response_model=MenuItemResponse)
def update_menu_item(item_id: int, item: MenuItemUpdate, db: Session = Depends(get_db)):
    menu_item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if not menu_item:
        raise HTTPException(status_code=404, detail="Item not found")
    for key, value in item.dict().items():
        setattr(menu_item, key, value)
    db.commit()
    db.refresh(menu_item)
    return menu_item

@router.delete("/menu-items/{item_id}")
def delete_menu_item(item_id: int, db: Session = Depends(get_db)):
    menu_item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if not menu_item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(menu_item)
    db.commit()
    return {"message": "Item deleted successfully"}
