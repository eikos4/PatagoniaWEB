from datetime import datetime

from app.models import Shipment


def next_embarque_numero():
    year = datetime.utcnow().year
    prefix = f"EMB-{year}-"
    last = (
        Shipment.query.filter(Shipment.numero.like(f"{prefix}%"))
        .order_by(Shipment.id.desc())
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


def embarque_from_pedido(ped):
    return {
        "order_id": ped.id,
        "folder_id": ped.folder_id,
        "cliente_nombre": ped.cliente_nombre,
        "cliente_empresa": ped.cliente_empresa,
        "puerto_origen": "San Antonio",
        "puerto_destino": "Manzanillo",
        "tipo_carga": "refrigerado",
        "temperatura": "-1°C a +4°C",
    }


def sync_pedido_estado(pedido, embarque_estado):
    """Actualiza el estado del pedido según el embarque."""
    mapping = {
        "programado": "listo",
        "en_transito": "embarcado",
        "en_puerto": "embarcado",
        "entregado": "entregado",
        "cancelado": None,
    }
    nuevo = mapping.get(embarque_estado)
    if nuevo and pedido.estado != "cancelado":
        pedido.estado = nuevo
