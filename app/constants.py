# Constantes de negocio para el panel admin

CLIENTE_ESTADOS = {
    "prospecto": "Prospecto",
    "negociacion": "En negociación",
    "con_abono": "Con abono",
    "cliente_activo": "Cliente activo",
    "inactivo": "Inactivo",
}

CLIENTE_ESTADO_COLORS = {
    "prospecto": "#6b7280",
    "negociacion": "#EA942A",
    "con_abono": "#2563eb",
    "cliente_activo": "#15803d",
    "inactivo": "#9ca3af",
}

PRODUCTO_CATEGORIAS = {
    "frutas": "Frutas",
    "mariscos": "Mariscos",
    "vinos": "Vinos",
    "otro": "Otro",
}

ABONO_TIPOS = {
    "abono": "Abono / anticipo",
    "compra": "Compra confirmada",
    "pago_parcial": "Pago parcial",
}

MONEDAS = ["USD", "CLP", "MXN"]

COTIZACION_ESTADOS = {
    "borrador": "Borrador",
    "enviada": "Enviada",
    "aceptada": "Aceptada",
    "rechazada": "Rechazada",
    "vencida": "Vencida",
}

COTIZACION_ESTADO_COLORS = {
    "borrador": "#6b7280",
    "enviada": "#2563eb",
    "aceptada": "#15803d",
    "rechazada": "#be123c",
    "vencida": "#9ca3af",
}

UNIDADES_LINEA = ["kg", "cajas", "pallets", "litros", "unidades", "ton"]

PEDIDO_ESTADOS = {
    "confirmado": "Confirmado",
    "en_preparacion": "En preparación",
    "listo": "Listo para embarque",
    "embarcado": "Embarcado",
    "entregado": "Entregado",
    "cancelado": "Cancelado",
}

PEDIDO_ESTADO_COLORS = {
    "confirmado": "#2563eb",
    "en_preparacion": "#EA942A",
    "listo": "#7c3aed",
    "embarcado": "#587232",
    "entregado": "#15803d",
    "cancelado": "#9ca3af",
}

PEDIDO_ESTADO_ICONS = {
    "confirmado": "fa-circle-check",
    "en_preparacion": "fa-box-open",
    "listo": "fa-dolly",
    "embarcado": "fa-ship",
    "entregado": "fa-flag-checkered",
    "cancelado": "fa-ban",
}

COTIZACION_ESTADO_ICONS = {
    "borrador": "fa-pen-ruler",
    "enviada": "fa-paper-plane",
    "aceptada": "fa-thumbs-up",
    "rechazada": "fa-circle-xmark",
    "vencida": "fa-clock",
}

CLIENTE_ESTADO_ICONS = {
    "prospecto": "fa-user-plus",
    "negociacion": "fa-handshake",
    "con_abono": "fa-coins",
    "cliente_activo": "fa-user-check",
    "inactivo": "fa-user-slash",
}

EMBARQUE_ESTADOS = {
    "programado": "Programado",
    "en_transito": "En tránsito",
    "en_puerto": "En puerto destino",
    "entregado": "Entregado",
    "cancelado": "Cancelado",
}

EMBARQUE_ESTADO_COLORS = {
    "programado": "#2563eb",
    "en_transito": "#587232",
    "en_puerto": "#EA942A",
    "entregado": "#15803d",
    "cancelado": "#9ca3af",
}

EMBARQUE_ESTADO_ICONS = {
    "programado": "fa-calendar-check",
    "en_transito": "fa-ship",
    "en_puerto": "fa-anchor",
    "entregado": "fa-circle-check",
    "cancelado": "fa-ban",
}

CARGA_TIPOS = {
    "refrigerado": "Refrigerado (frutas/mariscos)",
    "congelado": "Congelado",
    "seco": "Carga seca",
    "otro": "Otro",
}

PUERTOS_ORIGEN = [
    "Valparaíso", "San Antonio", "Coronel", "Lirquén", "Puerto Montt", "Punta Arenas",
]

PUERTOS_DESTINO = [
    "Manzanillo", "Lázaro Cárdenas", "Veracruz", "Altamira", "Ensenada", "Ciudad de México (CD)",
]

DEFAULT_PRODUCTOS = [
    {"nombre": "Frutas frescas", "categoria": "frutas", "orden": 1},
    {"nombre": "Frutas procesadas", "categoria": "frutas", "orden": 2},
    {"nombre": "Mariscos", "categoria": "mariscos", "orden": 3},
    {"nombre": "Vinos", "categoria": "vinos", "orden": 4},
]
