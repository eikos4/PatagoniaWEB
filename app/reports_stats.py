from datetime import datetime, timedelta

from sqlalchemy import func, extract

from app.models import (
    ClientFolder, Order, OrderLine, Shipment, ShipmentCost,
    Quotation, ExportDocument, Contract, Product,
)
from app.embarque_utils import embarques_activos_filter


def get_reportes_data():
    now = datetime.utcnow()
    inicio_mes = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    hace_6_meses = inicio_mes - timedelta(days=180)

    # Ventas por país
    ventas_por_pais = (
        Order.query.filter(Order.estado != "cancelado", Order.cliente_pais.isnot(None))
        .with_entities(
            Order.cliente_pais,
            func.count(Order.id),
            func.coalesce(func.sum(Order.total), 0),
        )
        .group_by(Order.cliente_pais)
        .order_by(func.coalesce(func.sum(Order.total), 0).desc())
        .all()
    )

    # Ventas por producto (desde líneas de pedido)
    ventas_por_producto = (
        OrderLine.query.join(Order)
        .join(Product, OrderLine.product_id == Product.id, isouter=True)
        .filter(Order.estado != "cancelado")
        .with_entities(
            func.coalesce(Product.nombre, OrderLine.descripcion),
            func.coalesce(func.sum(OrderLine.cantidad * OrderLine.precio_unitario), 0),
            func.count(OrderLine.id),
        )
        .group_by(func.coalesce(Product.nombre, OrderLine.descripcion))
        .order_by(func.coalesce(func.sum(OrderLine.cantidad * OrderLine.precio_unitario), 0).desc())
        .limit(10)
        .all()
    )

    # Exportaciones por mes (últimos 6 meses)
    exportaciones_mes = []
    for i in range(5, -1, -1):
        mes_fecha = inicio_mes - timedelta(days=30 * i)
        mes_num = mes_fecha.month
        anio = mes_fecha.year
        count = Shipment.query.filter(
            extract("month", Shipment.created_at) == mes_num,
            extract("year", Shipment.created_at) == anio,
        ).count()
        label = mes_fecha.strftime("%b %Y")
        exportaciones_mes.append({"label": label, "count": count})

    # Ranking clientes por monto pedidos
    ranking_clientes = (
        Order.query.filter(Order.estado != "cancelado")
        .with_entities(
            Order.cliente_nombre,
            Order.cliente_pais,
            func.count(Order.id),
            func.coalesce(func.sum(Order.total), 0),
        )
        .group_by(Order.cliente_nombre, Order.cliente_pais)
        .order_by(func.coalesce(func.sum(Order.total), 0).desc())
        .limit(10)
        .all()
    )

    clientes_activos = ClientFolder.query.filter_by(estado="cliente_activo").count()
    contenedores_enviados = Shipment.query.filter(
        Shipment.estado.in_(["entregado", "cerrado", "en_transito", "en_puerto", "en_destino"])
    ).count()
    embarques_retraso = Shipment.query.filter(
        embarques_activos_filter(),
        Shipment.eta.isnot(None),
        Shipment.eta < now,
    ).count()

    # Costos y rentabilidad
    costo_total_ops = (
        ShipmentCost.query.with_entities(func.coalesce(func.sum(ShipmentCost.monto), 0)).scalar()
    )
    venta_total_ops = (
        Order.query.join(Shipment, Shipment.order_id == Order.id)
        .filter(Order.estado != "cancelado")
        .with_entities(func.coalesce(func.sum(Order.total), 0))
        .scalar()
    )
    margen_global = float(venta_total_ops or 0) - float(costo_total_ops or 0)
    costo_promedio = 0
    embarques_con_costo = Shipment.query.filter(Shipment.costos.any()).count()
    if embarques_con_costo:
        costo_promedio = float(costo_total_ops or 0) / embarques_con_costo

    # Tiempo promedio entrega (días entre etd y entrega estimada o actual)
    tiempos = []
    for emb in Shipment.query.filter(
        Shipment.estado.in_(["entregado", "cerrado"]),
        Shipment.etd.isnot(None),
    ).all():
        fin = emb.fecha_zarpe or emb.eta or emb.updated_at
        if fin and emb.etd:
            tiempos.append(max((fin - emb.etd).days, 0))
    tiempo_promedio_entrega = round(sum(tiempos) / len(tiempos), 1) if tiempos else None

    # Rentabilidad por embarque (top)
    rentabilidad_embarques = []
    for emb in Shipment.query.filter(Shipment.costos.any()).order_by(Shipment.created_at.desc()).limit(15).all():
        if emb.precio_venta > 0:
            rentabilidad_embarques.append({
                "embarque": emb,
                "venta": emb.precio_venta,
                "costo": emb.costo_total,
                "margen": emb.margen_bruto,
                "pct": emb.rentabilidad_pct,
            })
    rentabilidad_embarques.sort(key=lambda x: x["margen"], reverse=True)

    documentos_vencidos = sum(
        1 for d in ExportDocument.query.filter(ExportDocument.fecha_vencimiento.isnot(None)).all()
        if d.esta_vencido and d.estado != "aprobado"
    )
    contratos_por_vencer = Contract.query.filter(
        Contract.estado.in_(["vigente", "por_vencer"]),
        Contract.fecha_fin.isnot(None),
        Contract.fecha_fin <= now + timedelta(days=30),
    ).count()

    pedidos_mes = Order.query.filter(
        Order.fecha_pedido >= inicio_mes, Order.estado != "cancelado"
    ).count()
    monto_mes = (
        Order.query.filter(Order.fecha_pedido >= inicio_mes, Order.estado != "cancelado")
        .with_entities(func.coalesce(func.sum(Order.total), 0))
        .scalar()
    )

    return {
        "ventas_por_pais": ventas_por_pais,
        "ventas_por_producto": ventas_por_producto,
        "exportaciones_mes": exportaciones_mes,
        "ranking_clientes": ranking_clientes,
        "clientes_activos": clientes_activos,
        "contenedores_enviados": contenedores_enviados,
        "embarques_retraso": embarques_retraso,
        "costo_total_ops": float(costo_total_ops or 0),
        "venta_total_ops": float(venta_total_ops or 0),
        "margen_global": margen_global,
        "costo_promedio": round(costo_promedio, 2),
        "tiempo_promedio_entrega": tiempo_promedio_entrega,
        "rentabilidad_embarques": rentabilidad_embarques[:8],
        "documentos_vencidos": documentos_vencidos,
        "contratos_por_vencer": contratos_por_vencer,
        "pedidos_mes": pedidos_mes,
        "monto_mes": float(monto_mes or 0),
        "cotizaciones_abiertas": Quotation.query.filter(
            Quotation.estado.in_(["borrador", "enviada"])
        ).count(),
    }
