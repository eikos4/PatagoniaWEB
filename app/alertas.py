from datetime import datetime, timedelta

from app.models import (
    ContactMessage,
    Quotation,
    Shipment,
    ExportDocument,
    Country,
    CountryRequirement,
    InternalTask,
    Contract,
    Product,
    ClientFolder,
)


def _alert(nivel, categoria, titulo, mensaje, endpoint=None, entity_id=None, icono="fa-bell"):
    return {
        "nivel": nivel,
        "categoria": categoria,
        "titulo": titulo,
        "mensaje": mensaje,
        "endpoint": endpoint,
        "entity_id": entity_id,
        "icono": icono,
    }


def get_alertas():
    now = datetime.utcnow()
    alertas = []

    for doc in ExportDocument.query.filter(ExportDocument.fecha_vencimiento.isnot(None)).all():
        if doc.estado == "aprobado":
            continue
        dias = doc.dias_para_vencer
        if dias is not None and dias < 0:
            alertas.append(_alert(
                "critica", "documento",
                f"Documento vencido: {doc.titulo}",
                f"Venció hace {abs(dias)} días.",
                endpoint="admin.documento_detalle", entity_id=doc.id,
                icono="fa-file-circle-xmark",
            ))
        elif dias is not None and dias <= 30:
            alertas.append(_alert(
                "advertencia", "documento",
                f"Documento por vencer: {doc.titulo}",
                f"Vence en {dias} días.",
                endpoint="admin.documento_detalle", entity_id=doc.id,
                icono="fa-file-circle-exclamation",
            ))

    pendientes = ExportDocument.query.filter_by(estado="pendiente").count()
    if pendientes:
        alertas.append(_alert(
            "info", "documento",
            f"{pendientes} documento(s) pendientes de revisión",
            "Revisa y aprueba la documentación de exportación.",
            endpoint="admin.documentos",
            icono="fa-folder-open",
        ))

    for cot in Quotation.query.filter(
        Quotation.estado.in_(["borrador", "enviada"]),
        Quotation.fecha_vencimiento.isnot(None),
        Quotation.fecha_vencimiento < now,
    ).all():
        alertas.append(_alert(
            "advertencia", "comercial",
            f"Cotización vencida: {cot.numero}",
            f"{cot.cliente_nombre} — venció el {cot.fecha_vencimiento.strftime('%d/%m/%Y')}.",
            endpoint="admin.cotizacion_detalle", entity_id=cot.id,
            icono="fa-file-invoice-dollar",
        ))

    proximo_etd = now + timedelta(days=7)
    for emb in Shipment.query.filter(
        Shipment.estado.in_(["programado", "listo_despacho"]),
        Shipment.etd.isnot(None),
        Shipment.etd <= proximo_etd,
        Shipment.etd >= now,
    ).all():
        dias = (emb.etd - now).days
        alertas.append(_alert(
            "advertencia", "logistica",
            f"Embarque próximo a salir: {emb.numero}",
            f"ETD en {dias} días — {emb.puerto_origen or 'Chile'} → {emb.puerto_destino or 'destino'}.",
            endpoint="admin.embarque_detalle", entity_id=emb.id,
            icono="fa-ship",
        ))

    for emb in Shipment.query.filter(
        Shipment.estado.in_(["programado", "en_transito", "en_puerto", "en_destino"]),
        Shipment.eta.isnot(None),
        Shipment.eta < now,
    ).all():
        alertas.append(_alert(
            "critica", "logistica",
            f"Embarque con retraso: {emb.numero}",
            f"ETA superada — {emb.cliente_nombre}.",
            endpoint="admin.embarque_detalle", entity_id=emb.id,
            icono="fa-clock",
        ))

    for emb in Shipment.query.filter_by(estado="incidencia").all():
        alertas.append(_alert(
            "critica", "logistica",
            f"Incidencia en embarque: {emb.numero}",
            emb.ultima_ubicacion or emb.tracking_notas or "Requiere seguimiento inmediato.",
            endpoint="admin.embarque_detalle", entity_id=emb.id,
            icono="fa-triangle-exclamation",
        ))

    for emb in Shipment.query.filter_by(estado="documentacion_pendiente").all():
        alertas.append(_alert(
            "advertencia", "logistica",
            f"Documentación pendiente: {emb.numero}",
            f"{emb.cliente_nombre} — completa certificados antes del despacho.",
            endpoint="admin.embarque_detalle", entity_id=emb.id,
            icono="fa-file-circle-exclamation",
        ))

    proximo_limite = now + timedelta(days=3)
    for tarea in InternalTask.query.filter(
        InternalTask.estado.in_(["pendiente", "en_proceso"]),
        InternalTask.fecha_limite.isnot(None),
        InternalTask.fecha_limite <= proximo_limite,
    ).all():
        if tarea.fecha_limite < now:
            alertas.append(_alert(
                "critica", "operaciones",
                f"Tarea vencida: {tarea.titulo}",
                tarea.responsable.nombre or tarea.responsable.username if tarea.responsable else "Sin responsable asignado.",
                endpoint="admin.tarea_editar", entity_id=tarea.id,
                icono="fa-list-check",
            ))
        else:
            dias = (tarea.fecha_limite - now).days
            alertas.append(_alert(
                "advertencia", "operaciones",
                f"Tarea por vencer: {tarea.titulo}",
                f"Vence en {dias} día(s).",
                endpoint="admin.tarea_editar", entity_id=tarea.id,
                icono="fa-list-check",
            ))

    tareas_abiertas = InternalTask.query.filter(
        InternalTask.estado.in_(["pendiente", "en_proceso"])
    ).count()
    if tareas_abiertas:
        alertas.append(_alert(
            "info", "operaciones",
            f"{tareas_abiertas} tarea(s) interna(s) abiertas",
            "Revisa pendientes del equipo.",
            endpoint="admin.tareas",
            icono="fa-clipboard-list",
        ))

    for ctr in Contract.query.filter(
        Contract.estado.in_(["vigente", "por_vencer"]),
        Contract.fecha_fin.isnot(None),
        Contract.fecha_fin < now,
    ).all():
        alertas.append(_alert(
            "critica", "comercial",
            f"Contrato vencido: {ctr.numero}",
            f"{ctr.titulo} — {ctr.cliente.nombre if ctr.cliente else 'Sin cliente'}.",
            endpoint="admin.contrato_detalle", entity_id=ctr.id,
            icono="fa-file-contract",
        ))

    proximo_ctr = now + timedelta(days=30)
    for ctr in Contract.query.filter(
        Contract.estado == "vigente",
        Contract.fecha_fin.isnot(None),
        Contract.fecha_fin <= proximo_ctr,
        Contract.fecha_fin >= now,
    ).all():
        dias = (ctr.fecha_fin - now).days
        alertas.append(_alert(
            "advertencia", "comercial",
            f"Contrato por vencer: {ctr.numero}",
            f"Vence en {dias} días — {ctr.titulo}.",
            endpoint="admin.contrato_detalle", entity_id=ctr.id,
            icono="fa-file-signature",
        ))

    for prod in Product.query.filter_by(activo=True).all():
        if not prod.tiene_ficha:
            alertas.append(_alert(
                "info", "cumplimiento",
                f"Producto sin ficha técnica: {prod.nombre}",
                "Sube la ficha PDF en el catálogo de productos.",
                endpoint="admin.producto_detalle", entity_id=prod.id,
                icono="fa-file-lines",
            ))

    for cliente in ClientFolder.query.filter_by(estado="cliente_activo").all():
        if not any(p.estado != "cancelado" for p in cliente.pedidos):
            continue
        tiene_contrato = any(c.estado in ("vigente", "por_vencer") for c in cliente.contratos)
        if not tiene_contrato:
            alertas.append(_alert(
                "advertencia", "comercial",
                f"Cliente sin contrato vigente: {cliente.nombre}",
                "Registra un contrato comercial para este cliente.",
                endpoint="admin.cartera_detalle", entity_id=cliente.id,
                icono="fa-file-contract",
            ))

    mensajes = ContactMessage.query.filter_by(leido=False).count()
    if mensajes:
        alertas.append(_alert(
            "info", "comercial",
            f"{mensajes} consulta(s) web sin leer",
            "Revisa los mensajes del formulario de contacto.",
            endpoint="admin.mensajes",
            icono="fa-inbox",
        ))

    for pais in Country.query.filter_by(activo=True).all():
        if not pais.requisitos:
            alertas.append(_alert(
                "info", "cumplimiento",
                f"País sin requisitos: {pais.nombre}",
                "Agrega requisitos fitosanitarios y documentales.",
                endpoint="admin.pais_detalle", entity_id=pais.id,
                icono="fa-globe",
            ))

    orden = {"critica": 0, "advertencia": 1, "info": 2}
    alertas.sort(key=lambda a: orden.get(a["nivel"], 9))
    return alertas


def get_alertas_resumen():
    alertas = get_alertas()
    return {
        "total": len(alertas),
        "criticas": sum(1 for a in alertas if a["nivel"] == "critica"),
        "advertencias": sum(1 for a in alertas if a["nivel"] == "advertencia"),
        "lista": alertas[:12],
    }
