"""Utilidades del portal cliente: alertas y documentos comerciales."""

from datetime import datetime

from app.models import ExportDocument
from app.constants import DOCUMENTO_TIPOS
from app.document_checklist_utils import get_embarque_document_checklist

TIPOS_FACTURA_PORTAL = ("factura", "packing", "bl", "despacho")


def get_portal_alertas(cliente):
    """Alertas visibles para el importador en el portal."""
    now = datetime.utcnow()
    alertas = []

    for emb in cliente.embarques:
        if emb.estado in ("entregado", "cerrado", "cancelado"):
            continue
        if emb.tiene_retraso:
            alertas.append({
                "nivel": "critica",
                "categoria": "embarque",
                "titulo": f"Retraso en embarque {emb.numero}",
                "mensaje": f"ETA superada. Última ubicación: {emb.ultima_ubicacion or 'sin actualizar'}.",
                "embarque_id": emb.id,
                "icono": "fa-clock",
                "embarque_numero": emb.numero,
            })
        elif emb.eta and (emb.eta - now).days <= 5 and emb.estado in ("en_transito", "en_destino", "en_puerto"):
            dias = max((emb.eta - now).days, 0)
            alertas.append({
                "nivel": "info",
                "categoria": "embarque",
                "titulo": f"Arribo próximo · {emb.numero}",
                "mensaje": f"ETA en {dias} día(s) a {emb.puerto_destino or 'destino'}.",
                "embarque_id": emb.id,
                "icono": "fa-anchor",
                "embarque_numero": emb.numero,
            })
        if emb.estado == "documentacion_pendiente":
            alertas.append({
                "nivel": "advertencia",
                "categoria": "embarque",
                "titulo": f"Documentación pendiente · {emb.numero}",
                "mensaje": "Aún se completan certificados para este embarque.",
                "embarque_id": emb.id,
                "icono": "fa-file-circle-exclamation",
                "embarque_numero": emb.numero,
            })
        checklist = get_embarque_document_checklist(emb)
        if not checklist["completo"] and emb.estado not in ("programado",):
            faltan = checklist["total"] - checklist["aprobados"]
            if faltan > 0 and not any(a["embarque_id"] == emb.id and "Documentación" in a["titulo"] for a in alertas):
                alertas.append({
                    "nivel": "advertencia",
                    "categoria": "embarque",
                    "titulo": f"Docs incompletos · {emb.numero}",
                    "mensaje": f"{checklist['aprobados']}/{checklist['total']} documentos aprobados para {checklist['pais_nombre']}.",
                    "embarque_id": emb.id,
                    "icono": "fa-folder-open",
                    "embarque_numero": emb.numero,
                })

    for doc in cliente.documentos_export:
        if doc.estado != "aprobado":
            continue
        if doc.firma_exportador and not doc.firma_importador:
            alertas.append({
                "nivel": "info",
                "categoria": "documento",
                "titulo": f"Firma pendiente · {doc.titulo[:40]}",
                "mensaje": "Patagonia Sur ya firmó. Tu firma digital está pendiente.",
                "embarque_id": None,
                "documento_id": doc.id,
                "icono": "fa-file-signature",
            })

    for ped in cliente.pedidos:
        if ped.estado == "cancelado":
            continue
        if ped.saldo_pendiente > 0 and ped.estado in ("confirmado", "en_preparacion"):
            alertas.append({
                "nivel": "info",
                "categoria": "pago",
                "titulo": f"Saldo pendiente · {ped.numero}",
                "mensaje": f"Saldo estimado: {ped.moneda} {ped.saldo_pendiente:,.2f}",
                "embarque_id": None,
                "icono": "fa-coins",
            })

    nivel_orden = {"critica": 0, "advertencia": 1, "info": 2}
    alertas.sort(key=lambda a: nivel_orden.get(a["nivel"], 9))
    return alertas[:12]


def alertas_portal_stats(alertas):
    """Contadores por nivel y categoría para la vista de alertas."""
    stats = {
        "total": len(alertas),
        "critica": 0,
        "advertencia": 0,
        "info": 0,
        "embarques": 0,
        "documentos": 0,
        "pagos": 0,
    }
    for a in alertas:
        stats[a.get("nivel", "info")] = stats.get(a.get("nivel", "info"), 0) + 1
        cat = a.get("categoria", "otro")
        if cat == "embarque":
            stats["embarques"] += 1
        elif cat == "documento":
            stats["documentos"] += 1
        elif cat == "pago":
            stats["pagos"] += 1
    return stats


def get_documentos_comerciales(cliente):
    """Facturas, packing lists y BL aprobados para el importador."""
    return ExportDocument.query.filter(
        ExportDocument.folder_id == cliente.id,
        ExportDocument.estado == "aprobado",
        ExportDocument.tipo.in_(TIPOS_FACTURA_PORTAL),
    ).order_by(ExportDocument.uploaded_at.asc()).all()


def group_documentos_por_anio(documentos):
    """Agrupa documentos por año, orden cronológico (antiguo → reciente)."""
    buckets = {}
    for doc in documentos:
        year = doc.uploaded_at.year if doc.uploaded_at else None
        buckets.setdefault(year, []).append(doc)

    def _sort_key(d):
        return d.uploaded_at or datetime.min

    grouped = []
    dated_years = sorted(y for y in buckets if y is not None)
    for year in dated_years:
        items = sorted(buckets[year], key=_sort_key)
        grouped.append((year, items))

    if None in buckets:
        items = sorted(buckets[None], key=_sort_key)
        grouped.append((None, items))

    return grouped


def documentos_portal_stats(documentos):
    """Resumen para la vista de expediente documental."""
    years = {d.uploaded_at.year for d in documentos if d.uploaded_at}
    pendientes = sum(
        1 for d in documentos
        if d.firma_exportador and not d.firma_importador
    )
    return {
        "total": len(documentos),
        "anios": len(years),
        "pendientes_firma": pendientes,
    }


PEDIDO_FLUJO_ESTADOS = ("confirmado", "en_preparacion", "listo", "embarcado", "entregado")


def pedido_flujo_index(estado):
    """Índice del estado en el flujo comercial (0–4) o -1 si cancelado."""
    try:
        return PEDIDO_FLUJO_ESTADOS.index(estado)
    except ValueError:
        return -1


def pedidos_portal_stats(pedidos):
    """Resumen para la vista de pedidos del portal."""
    activos = {"confirmado", "en_preparacion", "listo", "embarcado"}
    moneda = pedidos[0].moneda if pedidos else "USD"
    return {
        "total": len(pedidos),
        "en_curso": sum(1 for p in pedidos if p.estado in activos),
        "entregados": sum(1 for p in pedidos if p.estado == "entregado"),
        "con_saldo": sum(1 for p in pedidos if p.saldo_pendiente > 0),
        "moneda": moneda,
    }

