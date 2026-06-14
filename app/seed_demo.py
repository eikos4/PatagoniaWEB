"""
Datos de demostración para presentaciones comerciales.
Ejecutar: python seed_demo.py
         python seed_demo.py --force   (recrea la demo)
"""
from datetime import datetime, timedelta

from app import db
from app.models import (
    AdminUser,
    Product,
    ClientFolder,
    ClientAbono,
    ContactMessage,
    Quotation,
    QuotationLine,
    Order,
    OrderLine,
    Shipment,
    ShipmentMilestone,
    ShipmentCost,
    ExportDocument,
    Contract,
    InternalTask,
    Country,
    ActivityLog,
    NotificationLog,
)
from app.constants import LOGISTICA_ETAPAS
from app.cotizacion_utils import next_cotizacion_numero, calc_fecha_vencimiento
from app.pedido_utils import next_pedido_numero
from app.embarque_utils import next_embarque_numero, init_shipment_milestones
from app.contract_utils import next_contrato_numero

DEMO_MARKER = "demo-"
PORTAL_EMAIL = "demo@importacionesgolfo.mx"
PORTAL_PASSWORD = "Demo2026!"
LOCAL_ADMIN_USER = "carlos@patagoniasur.cl"
LOCAL_ADMIN_PASS = "Patagonia2026!"


def _days_ago(n):
    return datetime.utcnow() - timedelta(days=n)


def _days_ahead(n):
    return datetime.utcnow() + timedelta(days=n)


def _get_admin():
    admin = AdminUser.query.filter_by(activo=True).first()
    if not admin:
        admin = AdminUser(
            username=LOCAL_ADMIN_USER,
            rol="ceo",
            nombre="Carlos Mendoza",
            activo=True,
        )
        admin.set_password(LOCAL_ADMIN_PASS)
        db.session.add(admin)
        db.session.flush()
    return admin


def _ensure_local_admin():
    import os
    if os.environ.get("ADMIN_PASSWORD"):
        return
    admin = AdminUser.query.filter_by(username=LOCAL_ADMIN_USER).first()
    if not admin:
        admin = AdminUser(
            username=LOCAL_ADMIN_USER,
            rol="ceo",
            nombre="Carlos Mendoza",
            activo=True,
        )
        db.session.add(admin)
    admin.set_password(LOCAL_ADMIN_PASS)
    admin.rol = "ceo"
    admin.activo = True
    if not admin.nombre:
        admin.nombre = "Carlos Mendoza"


def _product_by_name(nombre):
    return Product.query.filter_by(nombre=nombre).first()


def clear_demo_data():
    folders = ClientFolder.query.filter(ClientFolder.slug.like(f"{DEMO_MARKER}%")).all()
    if not folders:
        return 0
    folder_ids = [f.id for f in folders]

    shipments = Shipment.query.filter(Shipment.folder_id.in_(folder_ids)).all()
    shipment_ids = [s.id for s in shipments]
    order_ids = [o.id for o in Order.query.filter(Order.folder_id.in_(folder_ids)).with_entities(Order.id)]
    cot_ids = [c.id for c in Quotation.query.filter(Quotation.folder_id.in_(folder_ids)).with_entities(Quotation.id)]

    if shipment_ids:
        ShipmentCost.query.filter(ShipmentCost.shipment_id.in_(shipment_ids)).delete(synchronize_session=False)
        ShipmentMilestone.query.filter(ShipmentMilestone.shipment_id.in_(shipment_ids)).delete(synchronize_session=False)
        InternalTask.query.filter(InternalTask.shipment_id.in_(shipment_ids)).delete(synchronize_session=False)
        ExportDocument.query.filter(ExportDocument.shipment_id.in_(shipment_ids)).delete(synchronize_session=False)

    ExportDocument.query.filter(ExportDocument.folder_id.in_(folder_ids)).delete(synchronize_session=False)
    InternalTask.query.filter(InternalTask.folder_id.in_(folder_ids)).delete(synchronize_session=False)
    NotificationLog.query.filter(NotificationLog.folder_id.in_(folder_ids)).delete(synchronize_session=False)
    Contract.query.filter(Contract.folder_id.in_(folder_ids)).delete(synchronize_session=False)
    ClientAbono.query.filter(ClientAbono.folder_id.in_(folder_ids)).delete(synchronize_session=False)

    if shipment_ids:
        Shipment.query.filter(Shipment.id.in_(shipment_ids)).delete(synchronize_session=False)

    if order_ids:
        OrderLine.query.filter(OrderLine.order_id.in_(order_ids)).delete(synchronize_session=False)
        Order.query.filter(Order.id.in_(order_ids)).delete(synchronize_session=False)

    if cot_ids:
        QuotationLine.query.filter(QuotationLine.quotation_id.in_(cot_ids)).delete(synchronize_session=False)
        Quotation.query.filter(Quotation.id.in_(cot_ids)).delete(synchronize_session=False)

    ContactMessage.query.filter(ContactMessage.email.like("%@demo-patagoniasur.cl")).delete(synchronize_session=False)
    ClientFolder.query.filter(ClientFolder.id.in_(folder_ids)).delete(synchronize_session=False)
    db.session.commit()
    return len(folders)


def _enrich_products():
    specs = {
        "Frutas frescas": {
            "categoria": "frutas",
            "formato_venta": "pallets",
            "descripcion": "Arándanos, cerezas y frutillas premium de la Patagonia chilena. Exportación refrigerada.",
            "peso_caja_kg": 2.5,
            "caja_largo_cm": 40,
            "caja_ancho_cm": 30,
            "caja_alto_cm": 12,
            "temperatura": "0°C a +2°C",
            "vida_util_dias": 21,
            "paises_permitidos": "México, Estados Unidos, Perú, Brasil",
            "certificaciones": "GlobalG.A.P., HACCP, Certificado fitosanitario SAG",
            "orden": 1,
        },
        "Frutas procesadas": {
            "categoria": "frutas_iqf",
            "formato_venta": "cajas",
            "descripcion": "Frutas IQF (Individual Quick Frozen): arándanos, frambuesas y mix berries.",
            "peso_caja_kg": 10,
            "temperatura": "-18°C",
            "vida_util_dias": 730,
            "paises_permitidos": "México, Colombia, Chile",
            "certificaciones": "BRC, HACCP, FDA",
            "orden": 2,
        },
        "Mariscos": {
            "categoria": "mariscos",
            "formato_venta": "cajas",
            "descripcion": "Salmón atlántico filete, centolla y productos del mar con trazabilidad completa.",
            "peso_caja_kg": 15,
            "temperatura": "-2°C a 0°C",
            "vida_util_dias": 14,
            "paises_permitidos": "México, Japón, Estados Unidos",
            "certificaciones": "ASC, HACCP, Certificado sanitario SERNAPESCA",
            "orden": 3,
        },
        "Vinos": {
            "categoria": "vinos",
            "formato_venta": "pallets",
            "descripcion": "Vinos D.O. Valle del Maule y Patagonia: Carmenère, Sauvignon Blanc y blends premium.",
            "temperatura": "15°C a 18°C",
            "vida_util_dias": 1825,
            "paises_permitidos": "México, Brasil, China",
            "certificaciones": "D.O., Certificado de origen, Etiquetado NOM",
            "orden": 4,
        },
    }
    for nombre, data in specs.items():
        p = _product_by_name(nombre)
        if p:
            for k, v in data.items():
                setattr(p, k, v)
            p.activo = True


def _add_lineas_cot(cot, lineas, admin_id):
    subtotal = 0
    for i, ln in enumerate(lineas):
        sub = ln["cantidad"] * ln["precio"]
        subtotal += sub
        cot.lineas.append(QuotationLine(
            descripcion=ln["desc"],
            cantidad=ln["cantidad"],
            unidad=ln["unidad"],
            precio_unitario=ln["precio"],
            product_id=ln.get("product_id"),
            orden=i,
        ))
    cot.subtotal = subtotal
    cot.total = subtotal * (1 - (cot.descuento_pct or 0) / 100)
    cot.created_by_id = admin_id


def _create_pedido(admin, cliente, lineas, estado, dias_atras=0, cot=None):
    ped = Order(
        numero=next_pedido_numero(),
        quotation_id=cot.id if cot else None,
        folder_id=cliente.id,
        cliente_nombre=cliente.nombre,
        cliente_empresa=cliente.empresa,
        cliente_email=cliente.email,
        cliente_telefono=cliente.telefono,
        cliente_pais=cliente.pais,
        estado=estado,
        moneda="USD",
        incoterm="FOB",
        anticipo_monto=lineas[0].get("anticipo", 0),
        fecha_pedido=_days_ago(dias_atras),
        fecha_entrega_estimada=_days_ahead(14),
        condiciones="Pago 30% anticipo · 70% contra copia de BL",
        created_by_id=admin.id,
    )
    db.session.add(ped)
    db.session.flush()
    for i, ln in enumerate(lineas):
        ped.lineas.append(OrderLine(
            descripcion=ln["desc"],
            cantidad=ln["cantidad"],
            unidad=ln["unidad"],
            precio_unitario=ln["precio"],
            product_id=ln.get("product_id"),
            orden=i,
        ))
    ped.recalcular_totales()
    return ped


def _set_milestones(shipment, hasta_etapa):
    etapas = list(LOGISTICA_ETAPAS.keys())
    limite = etapas.index(hasta_etapa) if hasta_etapa in etapas else -1
    for h in shipment.hitos:
        idx = etapas.index(h.etapa) if h.etapa in etapas else 99
        if idx <= limite:
            h.completado = True
            h.fecha = _days_ago(max(limite - idx, 1))


def _create_embarque(admin, ped, cliente, cfg):
    emb = Shipment(
        numero=next_embarque_numero(),
        order_id=ped.id,
        folder_id=cliente.id,
        cliente_nombre=cliente.nombre,
        cliente_empresa=cliente.empresa,
        estado=cfg["estado"],
        puerto_origen=cfg.get("origen", "San Antonio"),
        puerto_destino=cfg.get("destino", "Manzanillo"),
        naviera=cfg.get("naviera", "MSC"),
        numero_contenedor=cfg.get("contenedor"),
        numero_bl=cfg.get("bl"),
        numero_booking=cfg.get("booking"),
        tipo_contenedor=cfg.get("tipo_contenedor", "40rf"),
        tipo_carga=cfg.get("tipo_carga", "refrigerado"),
        temperatura=cfg.get("temperatura", "-1°C a +4°C"),
        ultima_ubicacion=cfg.get("ubicacion"),
        tracking_notas=cfg.get("tracking"),
        etd=cfg.get("etd"),
        eta=cfg.get("eta"),
        fecha_zarpe=cfg.get("zarpe"),
        responsable_id=admin.id,
        created_by_id=admin.id,
        fecha_embarque=cfg.get("fecha", _days_ago(10)),
    )
    db.session.add(emb)
    db.session.flush()
    init_shipment_milestones(emb)
    db.session.flush()
    if cfg.get("hito_hasta"):
        _set_milestones(emb, cfg["hito_hasta"])
    return emb


def seed_demo_data(force=False):
    if ClientFolder.query.filter(ClientFolder.slug.like(f"{DEMO_MARKER}%")).first():
        if not force:
            return {"skipped": True, "portal_email": PORTAL_EMAIL, "portal_password": PORTAL_PASSWORD}
        clear_demo_data()

    _ensure_local_admin()
    admin = _get_admin()
    _enrich_products()

    frutas = _product_by_name("Frutas frescas")
    frutas_iqf = _product_by_name("Frutas procesadas")
    mariscos = _product_by_name("Mariscos")
    vinos = _product_by_name("Vinos")
    mexico = Country.query.filter_by(codigo="MX").first()

    # ── Cliente principal (portal) ──────────────────────────────────
    golfo = ClientFolder(
        slug=f"{DEMO_MARKER}importaciones-golfo",
        nombre="Importaciones del Golfo SA",
        empresa="Importaciones del Golfo SA",
        contacto="Roberto Vega",
        email="r.vega@importacionesgolfo.mx",
        telefono="+52 55 4821 3300",
        pais="México",
        ciudad="Ciudad de México",
        tipo_cliente="importador",
        estado="cliente_activo",
        producto_id=frutas.id if frutas else None,
        valor_estimado=485000,
        moneda_estimada="USD",
        ejecutivo_id=admin.id,
        condiciones_comerciales="Incoterm FOB Valparaíso/San Antonio\nPago: 30% anticipo · 70% contra BL\nVol. mínimo: 1 contenedor 40' RF/mes",
        notas="Cliente estratégico · 4 embarques activos en demo · Cuenta portal habilitada",
        portal_activo=True,
        portal_email=PORTAL_EMAIL,
        created_by_id=admin.id,
    )
    golfo.set_portal_password(PORTAL_PASSWORD)
    db.session.add(golfo)
    db.session.flush()

    golfo.abonos.append(ClientAbono(
        folder_id=golfo.id,
        product_id=frutas.id if frutas else None,
        monto=42000,
        moneda="USD",
        tipo="abono",
        fecha=_days_ago(45),
        referencia="WIRE-MX-2026-0142",
        notas="Anticipo temporada arándanos Q2",
        created_by_id=admin.id,
    ))

    cot_aceptada = Quotation(
        numero=next_cotizacion_numero(),
        folder_id=golfo.id,
        cliente_nombre=golfo.nombre,
        cliente_empresa=golfo.empresa,
        cliente_email=golfo.email,
        cliente_telefono=golfo.telefono,
        cliente_pais=golfo.pais,
        estado="aceptada",
        moneda="USD",
        incoterm="FOB",
        validez_dias=15,
        fecha_emision=_days_ago(60),
        created_by_id=admin.id,
    )
    cot_aceptada.fecha_vencimiento = calc_fecha_vencimiento(cot_aceptada.fecha_emision, 15)
    _add_lineas_cot(cot_aceptada, [
        {"desc": "Arándanos premium calibre Jumbo", "cantidad": 12, "unidad": "pallets", "precio": 4200, "product_id": frutas.id if frutas else None},
        {"desc": "Cerezas rojas Región de Los Lagos", "cantidad": 8, "unidad": "pallets", "precio": 5100, "product_id": frutas.id if frutas else None},
    ], admin.id)
    db.session.add(cot_aceptada)

    cot_enviada = Quotation(
        numero=next_cotizacion_numero(),
        folder_id=golfo.id,
        cliente_nombre=golfo.nombre,
        cliente_empresa=golfo.empresa,
        cliente_email=golfo.email,
        estado="enviada",
        moneda="USD",
        incoterm="CIF",
        validez_dias=20,
        fecha_emision=_days_ago(3),
        created_by_id=admin.id,
    )
    cot_enviada.fecha_vencimiento = calc_fecha_vencimiento(cot_enviada.fecha_emision, 20)
    _add_lineas_cot(cot_enviada, [
        {"desc": "Mix berries IQF exportación", "cantidad": 2000, "unidad": "cajas", "precio": 18.5, "product_id": frutas_iqf.id if frutas_iqf else None},
    ], admin.id)
    db.session.add(cot_enviada)
    db.session.flush()

    # Pedidos y embarques con distintos estados
    ped_entregado = _create_pedido(admin, golfo, [
        {"desc": "Arándanos premium calibre Jumbo", "cantidad": 12, "unidad": "pallets", "precio": 4200, "product_id": frutas.id if frutas else None, "anticipo": 15000},
    ], "entregado", dias_atras=52, cot=cot_aceptada)

    ped_transito = _create_pedido(admin, golfo, [
        {"desc": "Salmón atlántico filete skin-on", "cantidad": 1800, "unidad": "kg", "precio": 8.9, "product_id": mariscos.id if mariscos else None, "anticipo": 8000},
    ], "embarcado", dias_atras=18)

    ped_puerto = _create_pedido(admin, golfo, [
        {"desc": "Vino Carmenère Reserva 2024", "cantidad": 2400, "unidad": "cajas", "precio": 32, "product_id": vinos.id if vinos else None},
    ], "embarcado", dias_atras=35)

    ped_prep = _create_pedido(admin, golfo, [
        {"desc": "Arándanos IQF Grade A", "cantidad": 1500, "unidad": "cajas", "precio": 22, "product_id": frutas_iqf.id if frutas_iqf else None},
    ], "en_preparacion", dias_atras=5)

    ped_programado = _create_pedido(admin, golfo, [
        {"desc": "Cerezas rojas Región de Los Lagos", "cantidad": 6, "unidad": "pallets", "precio": 5100, "product_id": frutas.id if frutas else None},
    ], "listo", dias_atras=2)

    emb_entregado = _create_embarque(admin, ped_entregado, golfo, {
        "estado": "entregado",
        "origen": "San Antonio",
        "destino": "Manzanillo",
        "naviera": "MSC",
        "contenedor": "MSCU4829176",
        "bl": "MSCMEX2401287",
        "booking": "BK-2026-00841",
        "ubicacion": "CDMX · Bodega Importaciones del Golfo",
        "tracking": "Entrega confirmada · Cliente firmó conforme 12/05/2026",
        "etd": _days_ago(48),
        "eta": _days_ago(18),
        "zarpe": _days_ago(45),
        "hito_hasta": "cliente",
        "fecha": _days_ago(50),
    })

    emb_transito = _create_embarque(admin, ped_transito, golfo, {
        "estado": "en_transito",
        "origen": "Puerto Montt",
        "destino": "Lázaro Cárdenas",
        "naviera": "Hapag-Lloyd",
        "contenedor": "HLBU7291043",
        "bl": "HLCUSCL2405521",
        "booking": "BK-2026-01102",
        "ubicacion": "Océano Pacífico · 1,240 millas náuticas a destino",
        "tracking": "Zarpó 28/05/2026 · ETA estimada 18/06/2026 · Temperatura estable -1°C",
        "etd": _days_ago(17),
        "eta": _days_ahead(4),
        "zarpe": _days_ago(14),
        "temperatura": "-1°C",
        "hito_hasta": "transito",
    })

    emb_puerto = _create_embarque(admin, ped_puerto, golfo, {
        "estado": "en_puerto",
        "origen": "Valparaíso",
        "destino": "Manzanillo",
        "naviera": "CMA CGM",
        "contenedor": "CMAU3847291",
        "bl": "CMDUCHI2403319",
        "ubicacion": "Puerto Manzanillo · Terminal contenedores",
        "tracking": "Arribó 10/06/2026 · En espera de despacho aduanero",
        "etd": _days_ago(32),
        "eta": _days_ago(2),
        "zarpe": _days_ago(28),
        "tipo_carga": "seco",
        "temperatura": "15°C a 18°C",
        "hito_hasta": "arribo",
    })

    emb_prep = _create_embarque(admin, ped_prep, golfo, {
        "estado": "en_preparacion",
        "origen": "San Antonio",
        "destino": "Manzanillo",
        "naviera": "Por asignar",
        "ubicacion": "Planta procesadora Osorno · Packing en curso",
        "tracking": "Producción 65% · Certificación SAG programada",
        "eta": _days_ahead(22),
        "hito_hasta": "packing",
    })

    emb_programado = _create_embarque(admin, ped_programado, golfo, {
        "estado": "programado",
        "origen": "San Antonio",
        "destino": "Manzanillo",
        "naviera": "Maersk",
        "booking": "BK-2026-01288",
        "ubicacion": "Planta Sur Valdivia · Listo para despacho",
        "eta": _days_ahead(12),
        "etd": _days_ahead(5),
        "hito_hasta": "carga",
    })

    # Costos y rentabilidad
    for emb, costos in [
        (emb_entregado, [
            ("flete", "Flete marítimo MSC", 4200),
            ("aduana", "Agente aduanero MX", 850),
            ("seguro", "Póliza carga refrigerada", 320),
            ("otro", "Inspección fitosanitaria", 180),
        ]),
        (emb_transito, [
            ("flete", "Flete Hapag-Lloyd", 3800),
            ("inland", "Transporte terrestre origen", 620),
            ("seguro", "Seguro marítimo", 290),
        ]),
    ]:
        for tipo, concepto, monto in costos:
            emb.costos.append(ShipmentCost(
                tipo=tipo,
                concepto=concepto,
                monto=monto,
                moneda="USD",
                created_by_id=admin.id,
            ))

    # Documentos exportación (visibles en portal si aprobados)
    docs_demo = [
        ("Certificado fitosanitario — Arándanos", "fitosanitario", "aprobado", emb_entregado, frutas),
        ("Factura comercial EMB-2026", "factura", "aprobado", emb_entregado, frutas),
        ("Bill of Lading MSCMEX2401287", "bl", "aprobado", emb_entregado, None),
        ("Certificado de origen Chile-México", "origen", "aprobado", emb_entregado, frutas),
        ("Packing list salmón filete", "packing", "aprobado", emb_transito, mariscos),
        ("Guía despacho frigorífico", "despacho", "aprobado", emb_transito, mariscos),
        ("Certificado sanitario SERNAPESCA", "calidad", "aprobado", emb_transito, mariscos),
        ("BL vinos Valparaíso", "bl", "pendiente", emb_puerto, vinos),
    ]
    for titulo, tipo, estado, emb, prod in docs_demo:
        db.session.add(ExportDocument(
            titulo=titulo,
            tipo=tipo,
            estado=estado,
            folder_id=golfo.id,
            shipment_id=emb.id if emb else None,
            country_id=mexico.id if mexico else None,
            product_id=prod.id if prod else None,
            comentarios="Documento demo · Patagonia Sur",
            uploaded_by_id=admin.id,
            uploaded_at=_days_ago(5),
        ))

    if mexico:
        db.session.add(Contract(
            numero=next_contrato_numero(),
            titulo="Contrato suministro frutas premium 2026",
            folder_id=golfo.id,
            country_id=mexico.id,
            product_id=frutas.id if frutas else None,
            responsable_id=admin.id,
            estado="vigente",
            fecha_inicio=_days_ago(90),
            fecha_fin=_days_ahead(275),
            renovacion_auto=True,
            condiciones="Suministro mensual mínimo 2 contenedores · Precio revisable trimestral",
            notas="Contrato demo vigente",
            created_by_id=admin.id,
        ))

    # ── Cliente 2: negociación ──────────────────────────────────────
    pacific = ClientFolder(
        slug=f"{DEMO_MARKER}pacific-fresh",
        nombre="Pacific Fresh Imports",
        empresa="Pacific Fresh Imports LLC",
        contacto="Sarah Mitchell",
        email="s.mitchell@pacificfresh.demo-patagoniasur.cl",
        telefono="+1 310 555 0198",
        pais="Estados Unidos",
        ciudad="Los Angeles",
        tipo_cliente="distribuidor",
        estado="negociacion",
        producto_id=mariscos.id if mariscos else None,
        valor_estimado=120000,
        ejecutivo_id=admin.id,
        notas="Interesados en salmón y centolla · Cotización enviada",
        created_by_id=admin.id,
    )
    db.session.add(pacific)
    db.session.flush()

    cot_pacific = Quotation(
        numero=next_cotizacion_numero(),
        folder_id=pacific.id,
        cliente_nombre=pacific.nombre,
        cliente_empresa=pacific.empresa,
        cliente_email=pacific.email,
        cliente_pais=pacific.pais,
        estado="enviada",
        moneda="USD",
        incoterm="FOB",
        fecha_emision=_days_ago(7),
        created_by_id=admin.id,
    )
    cot_pacific.fecha_vencimiento = calc_fecha_vencimiento(cot_pacific.fecha_emision, 15)
    _add_lineas_cot(cot_pacific, [
        {"desc": "Salmón filete premium", "cantidad": 5000, "unidad": "kg", "precio": 9.2, "product_id": mariscos.id if mariscos else None},
    ], admin.id)
    db.session.add(cot_pacific)

    # ── Cliente 3: prospecto ────────────────────────────────────────
    andina = ClientFolder(
        slug=f"{DEMO_MARKER}distribuidora-andina",
        nombre="Distribuidora Andina",
        empresa="Distribuidora Andina SAC",
        contacto="Luis Fernández",
        email="l.fernandez@andina.demo-patagoniasur.cl",
        pais="Perú",
        ciudad="Lima",
        tipo_cliente="retail",
        estado="prospecto",
        producto_id=vinos.id if vinos else None,
        valor_estimado=45000,
        notas="Primer contacto vía feria APAS 2026",
        created_by_id=admin.id,
    )
    db.session.add(andina)

    # ── Mensajes web ────────────────────────────────────────────────
    mensajes = [
        ("Miguel Torres", "m.torres@demo-patagoniasur.cl", "+56 9 8765 4321", "Agroexport MX", "Buenos días, necesito cotización de arándanos para Cd. de México, 2 contenedores mensuales."),
        ("Ana Ruiz", "a.ruiz@demo-patagoniasur.cl", None, "Vinos del Pacífico", "Consulta por vinos Carmenère y Sauvignon para distribución en Guadalajara."),
        ("James Cooper", "j.cooper@demo-patagoniasur.cl", "+1 415 555 8821", "West Coast Foods", "Interesado en salmón chileno, volúmenes para retail."),
    ]
    for nombre, email, tel, empresa, texto in mensajes:
        db.session.add(ContactMessage(
            nombre=nombre,
            email=email,
            telefono=tel,
            empresa=empresa,
            mensaje=texto,
            fecha=_days_ago(2),
            leido=False,
        ))

    # ── Tareas internas ─────────────────────────────────────────────
    tareas = [
        ("Coordinar inspección SAG — IQF", "alta", "pendiente", emb_prep, golfo, _days_ahead(3)),
        ("Enviar copia BL firmada al cliente", "media", "en_proceso", emb_transito, golfo, _days_ahead(1)),
        ("Seguimiento despacho aduanero Manzanillo", "alta", "pendiente", emb_puerto, golfo, _days_ahead(2)),
        ("Preparar booking Maersk cerezas", "media", "pendiente", emb_programado, golfo, _days_ahead(4)),
        ("Llamar seguimiento Pacific Fresh", "baja", "pendiente", None, pacific, _days_ahead(5)),
    ]
    for titulo, prioridad, estado, emb, cli, limite in tareas:
        db.session.add(InternalTask(
            titulo=titulo,
            prioridad=prioridad,
            estado=estado,
            shipment_id=emb.id if emb else None,
            folder_id=cli.id,
            responsable_id=admin.id,
            fecha_limite=limite,
            created_by_id=admin.id,
        ))

    # ── Historial de operaciones ────────────────────────────────────
    logs = [
        ("crear", "cliente", golfo.id, golfo.nombre, "Cliente demo registrado"),
        ("crear", "pedido", ped_transito.id, ped_transito.numero, "Pedido salmón confirmado"),
        ("editar", "embarque", emb_transito.id, emb_transito.numero, "Estado actualizado: en tránsito"),
        ("editar", "cliente", golfo.id, golfo.nombre, "Acceso portal configurado"),
    ]
    for accion, entidad, eid, ref, detalle in logs:
        db.session.add(ActivityLog(
            user_id=admin.id,
            accion=accion,
            entidad_tipo=entidad,
            entidad_id=eid,
            entidad_ref=ref,
            detalle=detalle,
            created_at=_days_ago(1),
        ))

    db.session.commit()
    return {
        "skipped": False,
        "portal_email": PORTAL_EMAIL,
        "portal_password": PORTAL_PASSWORD,
        "admin_user": LOCAL_ADMIN_USER,
        "admin_password": LOCAL_ADMIN_PASS,
        "cliente_portal": golfo.nombre,
        "embarques": 5,
    }


def run_seed_demo(force=False):
    return seed_demo_data(force=force)
