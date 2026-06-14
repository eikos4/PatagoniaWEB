from datetime import datetime

from app.models import Order


def next_pedido_numero():
    year = datetime.utcnow().year
    prefix = f"PED-{year}-"
    last = (
        Order.query.filter(Order.numero.like(f"{prefix}%"))
        .order_by(Order.id.desc())
        .first()
    )
    if last:
        try:
            n = int(last.numero.split("-")[-1]) + 1
        except ValueError:
            n = 1
    else:
        n = 1
    return f"{prefix}{n:04d}"


def apply_lineas(pedido, lineas_data):
    from app import db
    from app.models import OrderLine

    for old in list(pedido.lineas):
        db.session.delete(old)
    for data in lineas_data:
        pedido.lineas.append(OrderLine(**data))
    pedido.recalcular_totales()


def pedido_from_cotizacion(cot):
    """Datos iniciales para crear un pedido desde una cotización."""
    lineas = [
        {
            "descripcion": l.descripcion,
            "cantidad": l.cantidad,
            "unidad": l.unidad,
            "precio_unitario": l.precio_unitario,
            "product_id": l.product_id,
            "orden": l.orden,
        }
        for l in cot.lineas
    ]
    return {
        "quotation_id": cot.id,
        "folder_id": cot.folder_id,
        "cliente_nombre": cot.cliente_nombre,
        "cliente_empresa": cot.cliente_empresa,
        "cliente_email": cot.cliente_email,
        "cliente_telefono": cot.cliente_telefono,
        "cliente_pais": cot.cliente_pais,
        "moneda": cot.moneda,
        "incoterm": cot.incoterm,
        "descuento_pct": cot.descuento_pct or 0,
        "condiciones": cot.condiciones,
        "notas": cot.notas,
        "lineas": lineas,
    }
