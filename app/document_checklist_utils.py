"""Checklist documental automático por embarque según país y requisitos."""

from app.models import Country, CountryRequirement, ExportDocument
from app.constants import REQUISITO_A_DOCUMENTO_TIPO, DOCUMENTO_TIPOS

# Documentos base de toda exportación Chile
BASELINE_DOCS = [
    {"key": "fitosanitario", "titulo": "Certificado fitosanitario", "tipo": "fitosanitario"},
    {"key": "origen", "titulo": "Certificado de origen", "tipo": "origen"},
    {"key": "factura", "titulo": "Factura comercial", "tipo": "factura"},
    {"key": "packing", "titulo": "Packing list", "tipo": "packing"},
    {"key": "bl", "titulo": "Bill of Lading (BL)", "tipo": "bl"},
]


def _doc_estado_efectivo(doc):
    if doc.esta_vencido and doc.estado != "aprobado":
        return "vencido"
    return doc.estado


def _resolve_country(embarque):
    nombres = []
    if embarque.cliente and embarque.cliente.pais:
        nombres.append(embarque.cliente.pais.strip())
    if embarque.pedido and embarque.pedido.cliente_pais:
        nombres.append(embarque.pedido.cliente_pais.strip())
    destino = (embarque.puerto_destino or "").lower()
    if "manzanillo" in destino or "lázaro" in destino or "lazaro" in destino or "veracruz" in destino:
        nombres.append("México")
    if "callao" in destino or "lima" in destino:
        nombres.append("Perú")
    if "buenaventura" in destino or "cartagena" in destino:
        nombres.append("Colombia")

    for nombre in nombres:
        if not nombre:
            continue
        pais = Country.query.filter(Country.nombre.ilike(nombre)).first()
        if pais:
            return pais
        pais = Country.query.filter(Country.nombre.ilike(f"%{nombre}%")).first()
        if pais:
            return pais
    return None


def _product_ids(embarque):
    ids = set()
    if embarque.pedido:
        for linea in embarque.pedido.lineas:
            if linea.product_id:
                ids.add(linea.product_id)
    if embarque.cliente and embarque.cliente.producto_id:
        ids.add(embarque.cliente.producto_id)
    return ids


def _find_doc(docs, tipo, titulo_hint=""):
    titulo_lower = titulo_hint.lower()
    for d in docs:
        if d.tipo == tipo:
            return d
    for d in docs:
        if titulo_lower and titulo_lower in (d.titulo or "").lower():
            return d
    return None


def _item_status(doc, obligatorio=True):
    if not doc:
        return {
            "estado": "faltante",
            "label": "Faltante",
            "color": "red",
            "icon": "fa-circle-xmark",
            "doc_id": None,
        }
    eff = _doc_estado_efectivo(doc)
    if eff == "aprobado":
        return {
            "estado": "ok",
            "label": "Aprobado",
            "color": "green",
            "icon": "fa-circle-check",
            "doc_id": doc.id,
        }
    if eff == "vencido":
        return {
            "estado": "vencido",
            "label": "Vencido",
            "color": "red",
            "icon": "fa-calendar-xmark",
            "doc_id": doc.id,
        }
    if eff == "rechazado":
        return {
            "estado": "rechazado",
            "label": "Rechazado",
            "color": "red",
            "icon": "fa-ban",
            "doc_id": doc.id,
        }
    return {
        "estado": "pendiente",
        "label": "Pendiente",
        "color": "amber",
        "icon": "fa-clock",
        "doc_id": doc.id,
    }


def get_embarque_document_checklist(embarque):
    """Retorna checklist con ítems, resumen y país detectado."""
    docs = list(embarque.documentos or [])
    pais = _resolve_country(embarque)
    product_ids = _product_ids(embarque)
    items = []
    seen_keys = set()

    for base in BASELINE_DOCS:
        doc = _find_doc(docs, base["tipo"], base["titulo"])
        st = _item_status(doc)
        items.append({
            "key": base["key"],
            "titulo": base["titulo"],
            "tipo": base["tipo"],
            "tipo_label": DOCUMENTO_TIPOS.get(base["tipo"], base["tipo"]),
            "origen": "exportación",
            "obligatorio": True,
            "pais": None,
            **st,
        })
        seen_keys.add(base["key"])

    if pais:
        reqs = CountryRequirement.query.filter_by(country_id=pais.id).order_by(
            CountryRequirement.orden, CountryRequirement.titulo
        ).all()
        for req in reqs:
            if req.product_id and product_ids and req.product_id not in product_ids:
                continue
            tipo = REQUISITO_A_DOCUMENTO_TIPO.get(req.tipo, "otro")
            key = f"req_{req.id}"
            if key in seen_keys:
                continue
            doc = _find_doc(docs, tipo, req.titulo)
            st = _item_status(doc, obligatorio=req.obligatorio)
            if not doc and not req.obligatorio and st["estado"] == "faltante":
                st = {**st, "estado": "opcional", "label": "Opcional", "color": "gray", "icon": "fa-minus"}
            items.append({
                "key": key,
                "titulo": req.titulo,
                "tipo": tipo,
                "tipo_label": DOCUMENTO_TIPOS.get(tipo, tipo),
                "origen": pais.nombre,
                "obligatorio": bool(req.obligatorio),
                "pais": pais.nombre,
                **st,
            })
            seen_keys.add(key)

    obligatorios = [i for i in items if i["obligatorio"]]
    ok = sum(1 for i in obligatorios if i["estado"] == "ok")
    pendientes = sum(1 for i in obligatorios if i["estado"] in ("pendiente", "faltante", "vencido", "rechazado"))
    total_oblig = len(obligatorios) or 1
    pct = round(ok / total_oblig * 100)

    if ok == total_oblig:
        semaforo = "ok"
        resumen = "Documentación completa"
    elif pendientes and ok > 0:
        semaforo = "warn"
        resumen = f"{ok}/{total_oblig} aprobados"
    else:
        semaforo = "crit"
        resumen = f"{pendientes} pendiente(s)" if pendientes else "Sin documentos"

    return {
        "items": items,
        "pais": pais,
        "pais_nombre": pais.nombre if pais else (embarque.cliente.pais if embarque.cliente and embarque.cliente.pais else "General"),
        "total": len(obligatorios),
        "aprobados": ok,
        "pendientes": pendientes,
        "pct": pct,
        "completo": ok == total_oblig,
        "semaforo": semaforo,
        "resumen": resumen,
    }
