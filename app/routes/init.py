from sqlalchemy.orm import Session
from app.models import Admin
from .auth import get_password_hash  # Função para hashear senhas

def create_initial_admin(db: Session):
    admin_username = "admin"
    admin_email = "admin@example.com"
    admin_password = "admin123"  # Substitua por algo seguro

    # Verifica se já existe um admin
    existing_admin = db.query(Admin).filter(Admin.username == admin_username).first()
    if existing_admin:
        print("Admin já existente. Pulando criação.")
        return

    # Cria um novo admin
    new_admin = Admin(
        username=admin_username,
        email=admin_email,
        password=get_password_hash(admin_password),  # Senha hasheada
    )
    db.add(new_admin)
    db.commit()
    print(f"Admin criado com sucesso. Username: {admin_username}, Email: {admin_email}")
