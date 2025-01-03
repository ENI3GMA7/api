from sqlalchemy import Column, Integer, String, Float
from app.database import Base

class MenuItem(Base):
    __tablename__ = "menu_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(255), nullable=False)
    price = Column(Float, nullable=False)
    category = Column(String(50), nullable=False)
    image = Column(String(255), nullable=True)
