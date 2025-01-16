from fastapi import FastAPI
from app.routes import menu
from app.database import Base, engine
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
# Cria as tabelas no banco de dados
Base.metadata.create_all(bind=engine)

app = FastAPI()


app.mount("/images", StaticFiles(directory="items"), name="images")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Lista de origens permitidas
    allow_credentials=True,  # Permitir envio de cookies ou credenciais
    allow_methods=["*"],  # Permitir todos os métodos HTTP (GET, POST, etc.)
    allow_headers=["*"],  # Permitir todos os cabeçalhos
)
# Inclui o roteador para as rotas do menu
app.include_router(menu.router, prefix="/api", tags=["Menu"])

# Corrige o nome da variável __name__ e adiciona a porta padrão
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0")
