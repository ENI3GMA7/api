from fastapi import FastAPI
from app.routes import menu
from app.database import Base, engine

# Cria as tabelas no banco de dados
Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(menu.router, prefix="/api", tags=["Menu"])

if __name__"__main__":
  import uvicorn
    uvicorn.run(app,host=0.0.0.0)
