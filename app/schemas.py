from pydantic import BaseModel

class MenuItemBase(BaseModel):
    name: str
    description: str
    price: float
    category: str
    image: str

class MenuItemCreate(MenuItemBase):
    pass

class MenuItemUpdate(MenuItemBase):
    pass

class MenuItemResponse(MenuItemBase):
    id: int

    class Config:
        orm_mode = True
