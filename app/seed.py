from sqlalchemy import inspect

from app import db
from app.models import Product, AdminUser
from app.constants import DEFAULT_PRODUCTOS


def seed_default_products():
    try:
        if "products" not in inspect(db.engine).get_table_names():
            return
        if Product.query.count() > 0:
            return
    except Exception:
        return
    for p in DEFAULT_PRODUCTOS:
        db.session.add(Product(
            nombre=p["nombre"],
            categoria=p["categoria"],
            orden=p["orden"],
            activo=True,
        ))
    db.session.commit()


def seed_default_admin():
    """Crea o actualiza el admin desde variables de entorno (Render, etc.)."""
    import os

    password = os.environ.get("ADMIN_PASSWORD")
    if not password:
        return

    email = os.environ.get("ADMIN_EMAIL", "carlos@patagoniasur.cl")

    try:
        if "admin_users" not in inspect(db.engine).get_table_names():
            return
    except Exception:
        return

    try:
        admin = AdminUser.query.filter_by(username=email).first()
        if admin:
            admin.set_password(password)
        else:
            admin = AdminUser(username=email)
            admin.set_password(password)
            db.session.add(admin)
        db.session.commit()
    except Exception:
        db.session.rollback()
