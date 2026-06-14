from datetime import datetime

from app.models import Shipment, ShipmentMilestone
from app.constants import LOGISTICA_ETAPAS


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
        "tipo_contenedor": "40rf",
    }


def sync_pedido_estado(pedido, embarque_estado):
    mapping = {
        "en_preparacion": "en_preparacion",
        "documentacion_pendiente": "en_preparacion",
        "listo_despacho": "listo",
        "programado": "listo",
        "en_transito": "embarcado",
        "en_puerto": "embarcado",
        "en_destino": "embarcado",
        "entregado": "entregado",
        "cerrado": "entregado",
        "incidencia": None,
        "cancelado": None,
    }
    nuevo = mapping.get(embarque_estado)
    if nuevo and pedido.estado != "cancelado":
        pedido.estado = nuevo


def init_shipment_milestones(shipment):
    """Crea hitos logísticos vacíos si el embarque no tiene."""
    if shipment.hitos:
        return
    for i, etapa in enumerate(LOGISTICA_ETAPAS.keys()):
        db_hito = ShipmentMilestone(
            shipment_id=shipment.id,
            etapa=etapa,
            orden=i,
            completado=False,
        )
        from app import db
        db.session.add(db_hito)


def embarques_activos_filter():
    return Shipment.estado.notin_(["entregado", "cerrado", "cancelado"])
