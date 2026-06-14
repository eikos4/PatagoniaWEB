from sqlalchemy import inspect

from app import db
from app.models import Product
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
