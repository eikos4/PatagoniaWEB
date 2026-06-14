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
    "frutas": "Frutas frescas",
    "frutas_iqf": "Frutas congeladas IQF",
    "mariscos": "Productos del mar",
    "vinos": "Vinos",
    "procesados": "Alimentos procesados",
    "otro": "Otro",
}

PRODUCTO_FORMATOS = {
    "cajas": "Cajas",
    "kg": "Kilogramos",
    "pallets": "Pallets",
    "bins": "Bins",
    "otro": "Otro",
}

CLIENTE_TIPOS = {
    "importador": "Importador",
    "distribuidor": "Distribuidor",
    "retail": "Retail / cadena",
    "foodservice": "Food service",
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
    "en_preparacion": "En preparación",
    "documentacion_pendiente": "Documentación pendiente",
    "listo_despacho": "Listo para despacho",
    "programado": "Programado",
    "en_transito": "En tránsito",
    "en_puerto": "En puerto destino",
    "en_destino": "En destino",
    "entregado": "Entregado",
    "cerrado": "Cerrado",
    "incidencia": "Con incidencia",
    "cancelado": "Cancelado",
}

EMBARQUE_ESTADO_COLORS = {
    "en_preparacion": "#6b7280",
    "documentacion_pendiente": "#EA942A",
    "listo_despacho": "#7c3aed",
    "programado": "#2563eb",
    "en_transito": "#587232",
    "en_puerto": "#EA942A",
    "en_destino": "#0d9488",
    "entregado": "#15803d",
    "cerrado": "#374151",
    "incidencia": "#be123c",
    "cancelado": "#9ca3af",
}

EMBARQUE_ESTADO_ICONS = {
    "en_preparacion": "fa-box-open",
    "documentacion_pendiente": "fa-file-circle-exclamation",
    "listo_despacho": "fa-dolly",
    "programado": "fa-calendar-check",
    "en_transito": "fa-ship",
    "en_puerto": "fa-anchor",
    "en_destino": "fa-warehouse",
    "entregado": "fa-circle-check",
    "cerrado": "fa-lock",
    "incidencia": "fa-triangle-exclamation",
    "cancelado": "fa-ban",
}

LOGISTICA_ETAPAS = {
    "produccion": "Producción",
    "packing": "Packing",
    "certificacion": "Certificación",
    "carga": "Carga",
    "puerto_origen": "Puerto origen",
    "zarpe": "Zarpe",
    "transito": "Tránsito",
    "arribo": "Arribo",
    "aduana": "Aduana",
    "cliente": "Entrega cliente",
}

LOGISTICA_ETAPA_ICONS = {
    "produccion": "fa-industry",
    "packing": "fa-boxes-stacked",
    "certificacion": "fa-certificate",
    "carga": "fa-truck-ramp-box",
    "puerto_origen": "fa-anchor",
    "zarpe": "fa-ship",
    "transito": "fa-water",
    "arribo": "fa-flag",
    "aduana": "fa-passport",
    "cliente": "fa-handshake",
}

USER_ROLES = {
    "ceo": "CEO / Gerente general",
    "comercial": "Encargado comercial",
    "documental": "Encargado documental",
    "logistico": "Encargado logístico",
    "lectura": "Solo lectura",
}

TAREA_PRIORIDADES = {
    "baja": "Baja",
    "media": "Media",
    "alta": "Alta",
    "critica": "Crítica",
}

TAREA_PRIORIDAD_COLORS = {
    "baja": "#6b7280",
    "media": "#2563eb",
    "alta": "#EA942A",
    "critica": "#be123c",
}

TAREA_ESTADOS = {
    "pendiente": "Pendiente",
    "en_proceso": "En proceso",
    "completada": "Completada",
    "cancelada": "Cancelada",
}

TAREA_ESTADO_COLORS = {
    "pendiente": "#EA942A",
    "en_proceso": "#2563eb",
    "completada": "#15803d",
    "cancelada": "#9ca3af",
}

CONTENEDOR_TIPOS = {
    "20": "20 pies estándar",
    "40": "40 pies estándar",
    "40hc": "40 pies High Cube",
    "20rf": "20 pies Reefer",
    "40rf": "40 pies Reefer",
}

CONTENEDOR_DIMENSIONES = {
    "20": {"largo": 5.9, "ancho": 2.35, "alto": 2.39, "peso_max": 21770},
    "40": {"largo": 12.03, "ancho": 2.35, "alto": 2.39, "peso_max": 26500},
    "40hc": {"largo": 12.03, "ancho": 2.35, "alto": 2.69, "peso_max": 26500},
    "20rf": {"largo": 5.44, "ancho": 2.29, "alto": 2.27, "peso_max": 21770},
    "40rf": {"largo": 11.58, "ancho": 2.29, "alto": 2.40, "peso_max": 26500},
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

DOCUMENTO_TIPOS = {
    "fitosanitario": "Certificado fitosanitario",
    "origen": "Certificado de origen",
    "factura": "Factura comercial",
    "packing": "Packing list",
    "bl": "Bill of Lading (BL)",
    "despacho": "Guía de despacho",
    "contrato": "Contrato",
    "seguro": "Póliza de seguro",
    "aduana": "Documento aduanero",
    "etiqueta": "Etiquetas",
    "calidad": "Certificado de calidad",
    "cliente": "Documento del cliente",
    "contenedor": "Documento del contenedor",
    "otro": "Otro",
}

DOCUMENTO_ESTADOS = {
    "pendiente": "Pendiente",
    "aprobado": "Aprobado",
    "rechazado": "Rechazado",
    "vencido": "Vencido",
}

DOCUMENTO_ESTADO_COLORS = {
    "pendiente": "#EA942A",
    "aprobado": "#15803d",
    "rechazado": "#be123c",
    "vencido": "#9ca3af",
}

DOCUMENTO_ESTADO_ICONS = {
    "pendiente": "fa-clock",
    "aprobado": "fa-circle-check",
    "rechazado": "fa-circle-xmark",
    "vencido": "fa-calendar-xmark",
}

REQUISITO_TIPOS = {
    "fitosanitario": "Requisito fitosanitario",
    "documento": "Documento obligatorio",
    "etiquetado": "Etiquetado requerido",
    "autoridad": "Autoridad regulatoria",
    "certificacion": "Certificación necesaria",
    "comercial": "Condición comercial",
    "producto": "Observación por producto",
}

REQUISITO_A_DOCUMENTO_TIPO = {
    "fitosanitario": "fitosanitario",
    "documento": "aduana",
    "etiquetado": "etiqueta",
    "autoridad": "aduana",
    "certificacion": "calidad",
    "comercial": "contrato",
    "producto": "otro",
}

DEFAULT_PAISES = [
    {
        "nombre": "México",
        "codigo": "MX",
        "notas": "Mercado principal. Requiere certificación SAG/SENASICA según producto.",
        "requisitos": [
            {"tipo": "fitosanitario", "titulo": "Certificado fitosanitario SAG", "descripcion": "Emitido por el Servicio Agrícola y Ganadero de Chile.", "obligatorio": True},
            {"tipo": "documento", "titulo": "Factura comercial", "descripcion": "Factura con datos del exportador e importador.", "obligatorio": True},
            {"tipo": "documento", "titulo": "Certificado de origen", "descripcion": "Acredita origen chileno de la mercancía.", "obligatorio": True},
            {"tipo": "autoridad", "titulo": "SENASICA", "descripcion": "Autoridad sanitaria mexicana para ingreso de alimentos.", "obligatorio": True},
            {"tipo": "documento", "titulo": "Pedimento de importación", "descripcion": "Documento aduanero mexicano.", "obligatorio": True},
        ],
    },
    {
        "nombre": "Colombia",
        "codigo": "CO",
        "notas": "Mercado Andino. Verificar aranceles y requisitos ICA.",
        "requisitos": [
            {"tipo": "fitosanitario", "titulo": "Certificado fitosanitario", "descripcion": "Requerido para frutas y productos agrícolas.", "obligatorio": True},
            {"tipo": "documento", "titulo": "Factura comercial", "descripcion": "Documento de venta internacional.", "obligatorio": True},
            {"tipo": "autoridad", "titulo": "ICA Colombia", "descripcion": "Instituto Colombiano Agropecuario.", "obligatorio": False},
        ],
    },
    {
        "nombre": "España",
        "codigo": "ES",
        "notas": "Unión Europea. Cumplimiento normativa UE.",
        "requisitos": [
            {"tipo": "certificacion", "titulo": "Registro sanitario UE", "descripcion": "Según categoría de producto alimentario.", "obligatorio": True},
            {"tipo": "documento", "titulo": "EUR.1 o declaración de origen", "descripcion": "Preferencia arancelaria si aplica.", "obligatorio": False},
        ],
    },
    {
        "nombre": "Holanda",
        "codigo": "NL",
        "notas": "Hub logístico europeo. Puerto Rotterdam.",
        "requisitos": [
            {"tipo": "documento", "titulo": "CMR / documentos de transporte", "descripcion": "Para carga terrestre o marítima.", "obligatorio": True},
        ],
    },
    {
        "nombre": "Estados Unidos",
        "codigo": "US",
        "notas": "FDA y USDA según tipo de producto.",
        "requisitos": [
            {"tipo": "autoridad", "titulo": "FDA", "descripcion": "Food and Drug Administration.", "obligatorio": True},
            {"tipo": "fitosanitario", "titulo": "Permiso fitosanitario USDA", "descripcion": "Para productos agrícolas.", "obligatorio": True},
        ],
    },
    {
        "nombre": "China",
        "codigo": "CN",
        "notas": "Requisitos GACC y registro de establecimientos.",
        "requisitos": [
            {"tipo": "autoridad", "titulo": "GACC", "descripcion": "General Administration of Customs China.", "obligatorio": True},
            {"tipo": "etiquetado", "titulo": "Etiquetado en chino", "descripcion": "Información en idioma local según producto.", "obligatorio": True},
        ],
    },
    {
        "nombre": "Brasil",
        "codigo": "BR",
        "notas": "Mercosur. Requisitos MAPA.",
        "requisitos": [
            {"tipo": "autoridad", "titulo": "MAPA Brasil", "descripcion": "Ministerio de Agricultura.", "obligatorio": True},
            {"tipo": "documento", "titulo": "Factura comercial", "descripcion": "Documento de exportación.", "obligatorio": True},
        ],
    },
]

COSTO_TIPOS = {
    "producto": "Producto / materia prima",
    "packing": "Packing y embalaje",
    "transporte": "Transporte interno",
    "certificacion": "Certificaciones",
    "aduana": "Aduana / despacho",
    "flete": "Flete marítimo",
    "seguro": "Seguro",
    "comision": "Comisión comercial",
    "bancario": "Costos bancarios",
    "otro": "Otros gastos",
}

COSTO_TIPO_ICONS = {
    "producto": "fa-box",
    "packing": "fa-boxes-stacked",
    "transporte": "fa-truck",
    "certificacion": "fa-certificate",
    "aduana": "fa-passport",
    "flete": "fa-ship",
    "seguro": "fa-shield-halved",
    "comision": "fa-hand-holding-dollar",
    "bancario": "fa-building-columns",
    "otro": "fa-ellipsis",
}

CONTRATO_ESTADOS = {
    "borrador": "Borrador",
    "vigente": "Vigente",
    "por_vencer": "Por vencer",
    "vencido": "Vencido",
    "renovado": "Renovado",
    "cancelado": "Cancelado",
}

CONTRATO_ESTADO_COLORS = {
    "borrador": "#6b7280",
    "vigente": "#15803d",
    "por_vencer": "#EA942A",
    "vencido": "#be123c",
    "renovado": "#2563eb",
    "cancelado": "#9ca3af",
}

PLANTILLA_TIPOS = {
    "factura": "Factura comercial",
    "packing": "Packing list",
    "contrato": "Contrato tipo",
    "cotizacion": "Formato cotización",
    "ficha": "Ficha técnica",
    "etiqueta": "Etiquetas",
    "manual": "Manual interno",
    "procedimiento": "Procedimiento por país",
    "otro": "Otro",
}

AUDIT_ENTIDADES = {
    "embarque": "Embarque",
    "pedido": "Pedido",
    "cotizacion": "Cotización",
    "documento": "Documento",
    "contrato": "Contrato",
    "cliente": "Cliente",
    "tarea": "Tarea",
    "costo": "Costo",
    "plantilla": "Plantilla",
    "producto": "Producto",
    "usuario": "Usuario",
}

AUDIT_ACCIONES = {
    "crear": "Creación",
    "editar": "Edición",
    "eliminar": "Eliminación",
    "subir": "Subida archivo",
    "aprobar": "Aprobación",
    "estado": "Cambio de estado",
    "tracking": "Actualización seguimiento",
}
