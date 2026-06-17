from datetime import datetime, timedelta

from sqlalchemy import func

from app.models import (
    ContactMessage, ClientFolder, ClientAbono, ClientFile, Product,
    Quotation, Order, Shipment, ExportDocument, Country,
)
from app.constants import CLIENTE_ESTADOS, PRODUCTO_CATEGORIAS, PEDIDO_ESTADOS, EMBARQUE_ESTADOS
from app.embarque_utils import embarques_activos_filter
from app.alertas import get_alertas_resumen
from app.document_checklist_utils import get_embarque_document_checklist


def _doc_estado_efectivo(doc):
    if doc.esta_vencido and doc.estado != "aprobado":
        return "vencido"
    return doc.estado


def _embarque_doc_resumen(emb):
    docs = emb.documentos
    if not docs:
        return "Sin documentos", "warn"
    aprobados = sum(1 for d in docs if _doc_estado_efectivo(d) == "aprobado")
    pendientes = sum(1 for d in docs if _doc_estado_efectivo(d) in ("pendiente", "vencido"))
    if pendientes:
        return f"{aprobados}/{len(docs)} aprobados", "warn"
    return "Documentos completos", "ok"


def get_dashboard_kpis():
    now = datetime.utcnow()
    inicio_mes = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    total_clientes = ClientFolder.query.count()
    clientes_con_abono = ClientFolder.query.filter(
        ClientFolder.id.in_(
            ClientAbono.query.with_entities(ClientAbono.folder_id).distinct()
        )
    ).count()

    total_abonos_usd = (
        ClientAbono.query.filter_by(moneda="USD")
        .with_entities(func.coalesce(func.sum(ClientAbono.monto), 0))
        .scalar()
    )
    total_abonos_clp = (
        ClientAbono.query.filter_by(moneda="CLP")
        .with_entities(func.coalesce(func.sum(ClientAbono.monto), 0))
        .scalar()
    )

    abonos_mes = ClientAbono.query.filter(ClientAbono.fecha >= inicio_mes).count()
    monto_mes_usd = (
        ClientAbono.query.filter(ClientAbono.fecha >= inicio_mes, ClientAbono.moneda == "USD")
        .with_entities(func.coalesce(func.sum(ClientAbono.monto), 0))
        .scalar()
    )

    mensajes_total = ContactMessage.query.count()
    mensajes_pendientes = ContactMessage.query.filter_by(leido=False).count()
    mensajes_mes = ContactMessage.query.filter(ContactMessage.fecha >= inicio_mes).count()

    total_archivos = ClientFile.query.count()
    productos_activos = Product.query.filter_by(activo=True).count()
    cotizaciones_total = Quotation.query.count()
    cotizaciones_pendientes = Quotation.query.filter(
        Quotation.estado.in_(["borrador", "enviada"])
    ).count()

    pedidos_total = Order.query.count()
    pedidos_activos = Order.query.filter(
        Order.estado.notin_(["entregado", "cancelado"])
    ).count()
    pedidos_mes = Order.query.filter(Order.fecha_pedido >= inicio_mes).count()
    monto_pedidos_mes = (
        Order.query.filter(Order.fecha_pedido >= inicio_mes, Order.estado != "cancelado")
        .with_entities(func.coalesce(func.sum(Order.total), 0))
        .scalar()
    )
    pedidos_recientes = Order.query.order_by(Order.created_at.desc()).limit(5).all()

    embarques_total = Shipment.query.count()
    embarques_activos = Shipment.query.filter(embarques_activos_filter()).count()
    embarques_en_transito = Shipment.query.filter_by(estado="en_transito").count()
    embarques_recientes = Shipment.query.order_by(Shipment.created_at.desc()).limit(5).all()

    paises_atendidos = Country.query.filter_by(activo=True).count()
    paises_con_clientes = (
        ClientFolder.query.filter(ClientFolder.pais.isnot(None), ClientFolder.pais != "")
        .with_entities(ClientFolder.pais, func.count(ClientFolder.id))
        .group_by(ClientFolder.pais)
        .order_by(func.count(ClientFolder.id).desc())
        .all()
    )

    documentos_total = ExportDocument.query.count()
    documentos_pendientes = ExportDocument.query.filter_by(estado="pendiente").count()
    documentos_vencidos = sum(
        1 for d in ExportDocument.query.filter(ExportDocument.fecha_vencimiento.isnot(None)).all()
        if d.esta_vencido and d.estado != "aprobado"
    )

    ventas_por_pais = (
        Order.query.filter(Order.estado != "cancelado", Order.cliente_pais.isnot(None))
        .with_entities(Order.cliente_pais, func.count(Order.id), func.coalesce(func.sum(Order.total), 0))
        .group_by(Order.cliente_pais)
        .order_by(func.coalesce(func.sum(Order.total), 0).desc())
        .limit(8)
        .all()
    )

    operaciones_activas = []
    for emb in Shipment.query.filter(
        Shipment.estado.notin_(["entregado", "cancelado"])
    ).order_by(Shipment.created_at.desc()).limit(8).all():
        eta_dias = None
        if emb.eta:
            eta_dias = max((emb.eta - now).days, 0)
        doc_txt, doc_status = _embarque_doc_resumen(emb)
        checklist = get_embarque_document_checklist(emb)
        operaciones_activas.append({
            "embarque": emb,
            "ruta": f"Chile → {emb.puerto_destino or (emb.cliente.pais if emb.cliente else 'Destino')}",
            "contenedores": 1 if emb.numero_contenedor else 0,
            "doc_texto": checklist["resumen"],
            "doc_status": checklist["semaforo"] if checklist["semaforo"] != "ok" else "ok",
            "checklist_pct": checklist["pct"],
            "checklist_completo": checklist["completo"],
            "eta_dias": eta_dias,
            "cliente_pais": emb.cliente.pais if emb.cliente else None,
            "estado_label": EMBARQUE_ESTADOS.get(emb.estado, emb.estado),
        })

    alertas = get_alertas_resumen()

    por_estado = {
        estado: ClientFolder.query.filter_by(estado=estado).count()
        for estado in CLIENTE_ESTADOS
    }

    por_producto = (
        ClientFolder.query.filter(ClientFolder.producto_id.isnot(None))
        .join(Product)
        .with_entities(Product.nombre, func.count(ClientFolder.id))
        .group_by(Product.id)
        .all()
    )

    abonos_por_producto = (
        ClientAbono.query.filter(ClientAbono.product_id.isnot(None))
        .join(Product)
        .with_entities(Product.nombre, func.count(ClientAbono.id), func.sum(ClientAbono.monto))
        .group_by(Product.id)
        .all()
    )

    clientes_recientes = ClientFolder.query.order_by(ClientFolder.updated_at.desc()).limit(5).all()
    abonos_recientes = ClientAbono.query.order_by(ClientAbono.fecha.desc()).limit(5).all()

    return {
        "total_clientes": total_clientes,
        "clientes_con_abono": clientes_con_abono,
        "total_abonos_usd": float(total_abonos_usd or 0),
        "total_abonos_clp": float(total_abonos_clp or 0),
        "abonos_mes": abonos_mes,
        "monto_mes_usd": float(monto_mes_usd or 0),
        "mensajes_total": mensajes_total,
        "mensajes_pendientes": mensajes_pendientes,
        "mensajes_mes": mensajes_mes,
        "total_archivos": total_archivos,
        "productos_activos": productos_activos,
        "cotizaciones_total": cotizaciones_total,
        "cotizaciones_pendientes": cotizaciones_pendientes,
        "pedidos_total": pedidos_total,
        "pedidos_activos": pedidos_activos,
        "pedidos_mes": pedidos_mes,
        "monto_pedidos_mes": float(monto_pedidos_mes or 0),
        "pedidos_recientes": pedidos_recientes,
        "pedido_estados_labels": PEDIDO_ESTADOS,
        "embarques_total": embarques_total,
        "embarques_activos": embarques_activos,
        "embarques_en_transito": embarques_en_transito,
        "embarques_recientes": embarques_recientes,
        "embarque_estados_labels": EMBARQUE_ESTADOS,
        "paises_atendidos": paises_atendidos,
        "paises_con_clientes": paises_con_clientes,
        "documentos_total": documentos_total,
        "documentos_pendientes": documentos_pendientes,
        "documentos_vencidos": documentos_vencidos,
        "ventas_por_pais": ventas_por_pais,
        "operaciones_activas": operaciones_activas,
        "alertas": alertas,
        "por_estado": por_estado,
        "por_producto": por_producto,
        "abonos_por_producto": abonos_por_producto,
        "clientes_recientes": clientes_recientes,
        "abonos_recientes": abonos_recientes,
        "estados_labels": CLIENTE_ESTADOS,
        "categorias_labels": PRODUCTO_CATEGORIAS,
    }
