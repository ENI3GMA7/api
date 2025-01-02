from fastapi import FastAPI
from app.routes import menu
from app.database import Base, engine

# Cria as tabelas no banco de dados
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Inclui o roteador para as rotas do menu
app.include_router(menu.router, prefix="/api", tags=["Menu"])

# Corrige o nome da variável __name__ e adiciona a porta padrão
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0")
