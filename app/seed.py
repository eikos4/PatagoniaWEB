from sqlalchemy import inspect

from app import db
from app.models import Product, AdminUser, Country, CountryRequirement
from app.constants import DEFAULT_PRODUCTOS, DEFAULT_PAISES


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
            admin.rol = admin.rol or "ceo"
            admin.activo = True if admin.activo is None else admin.activo
            if not admin.nombre:
                admin.nombre = "Administrador"
        else:
            admin = AdminUser(
                username=email,
                rol="ceo",
                nombre="Administrador",
                activo=True,
            )
            admin.set_password(password)
            db.session.add(admin)
        db.session.commit()
    except Exception:
        db.session.rollback()


def seed_default_countries():
    try:
        if "countries" not in inspect(db.engine).get_table_names():
            return
        if Country.query.count() > 0:
            return
    except Exception:
        return

    for data in DEFAULT_PAISES:
        pais = Country(
            nombre=data["nombre"],
            codigo=data["codigo"],
            notas=data.get("notas"),
            activo=True,
        )
        db.session.add(pais)
        db.session.flush()
        for i, req in enumerate(data.get("requisitos", [])):
            db.session.add(CountryRequirement(
                country_id=pais.id,
                tipo=req.get("tipo", "documento"),
                titulo=req["titulo"],
                descripcion=req.get("descripcion"),
                obligatorio=req.get("obligatorio", True),
                orden=i,
            ))
    db.session.commit()
