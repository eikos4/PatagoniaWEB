"""Crea o actualiza el usuario admin (útil en local sin Shell de Render)."""
from app import create_app
from app.seed import seed_default_admin

app = create_app()

with app.app_context():
    seed_default_admin()
    print("Admin listo (si ADMIN_PASSWORD está definida en el entorno).")
