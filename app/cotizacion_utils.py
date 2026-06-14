from datetime import datetime, timedelta

from app.models import Quotation


def next_cotizacion_numero():
    year = datetime.utcnow().year
    prefix = f"COT-{year}-"
    last = (
        Quotation.query.filter(Quotation.numero.like(f"{prefix}%"))
        .order_by(Quotation.id.desc())
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


def parse_lineas_from_form(form_data):
    descs = form_data.getlist("linea_desc")
    cants = form_data.getlist("linea_cant")
    unids = form_data.getlist("linea_unidad")
    precios = form_data.getlist("linea_precio")
    productos = form_data.getlist("linea_producto")

    lineas = []
    for i, desc in enumerate(descs):
        desc = (desc or "").strip()
        if not desc:
            continue
        try:
            cant = float(cants[i]) if i < len(cants) and cants[i] else 1
            precio = float(precios[i]) if i < len(precios) and precios[i] else 0
        except (ValueError, TypeError):
            cant, precio = 1, 0
        unidad = unids[i] if i < len(unids) and unids[i] else "kg"
        prod_id = None
        if i < len(productos) and productos[i]:
            try:
                pid = int(productos[i])
                prod_id = pid if pid > 0 else None
            except ValueError:
                pass
        lineas.append({
            "descripcion": desc,
            "cantidad": cant,
            "unidad": unidad,
            "precio_unitario": precio,
            "product_id": prod_id,
            "orden": len(lineas),
        })
    return lineas


def apply_lineas(cotizacion, lineas_data):
    from app import db
    from app.models import QuotationLine
    for old in list(cotizacion.lineas):
        db.session.delete(old)
    for data in lineas_data:
        cotizacion.lineas.append(QuotationLine(**data))
    cotizacion.recalcular_totales()


def calc_fecha_vencimiento(fecha_emision, validez_dias):
    return fecha_emision + timedelta(days=validez_dias or 15)
