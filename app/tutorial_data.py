"""Contenido de tutoriales y guía de importación/exportación."""

IMPORT_GUIDE = {
    "titulo": "Guía para una buena importación",
    "subtitulo": "Proceso completo Chile → mercado internacional · frutas y productos del mar",
    "intro": (
        "Esta guía resume las buenas prácticas para exportar desde Chile e importar en destino "
        "sin retrasos aduaneros ni documentación incompleta. Sigue el flujo en orden y usa la "
        "plataforma Patagonia Sur en cada etapa."
    ),
    "capitulos": [
        {
            "id": "planificacion",
            "numero": 1,
            "titulo": "Planificación comercial",
            "icono": "fa-clipboard-list",
            "resumen": "Define volumen, temporada, puerto destino e incoterm antes de cotizar.",
            "puntos": [
                "Confirma producto (fruta fresca o marisco), volumen en kg y ventanas de cosecha o captura.",
                "Elige puerto destino (ej. Manzanillo, Lázaro Cárdenas) y ciudad final del importador.",
                "Acuerda incoterm: FOB Chile, CIF destino o DAP según quién asume flete y seguro.",
                "Revisa requisitos del país en el módulo Países antes de comprometer precio.",
            ],
            "modulo": {"nombre": "Países y requisitos", "endpoint": "admin.paises"},
            "alerta": "Cotizar sin revisar requisitos fitosanitarios es la causa #1 de reprocesos.",
        },
        {
            "id": "cliente",
            "numero": 2,
            "titulo": "Registro del cliente importador",
            "icono": "fa-users",
            "resumen": "CRM ordenado: empresa, contacto, país y condiciones comerciales.",
            "puntos": [
                "Crea la ficha del importador con empresa, contacto, email y país destino.",
                "Clasifica el estado: prospecto → negociación → cliente activo.",
                "Registra abonos o anticipos cuando existan compromisos de pago.",
                "Activa el portal cliente para que el importador vea embarques y documentos.",
            ],
            "modulo": {"nombre": "Clientes", "endpoint": "admin.clientes"},
            "alerta": "Sin contrato vigente o ficha incompleta, no avances a embarque.",
        },
        {
            "id": "cotizacion",
            "numero": 3,
            "titulo": "Cotización comercial",
            "icono": "fa-file-invoice-dollar",
            "resumen": "Presupuesto formal con líneas, moneda, validez y PDF.",
            "puntos": [
                "Selecciona cliente y agrega líneas de producto con cantidad y precio unitario.",
                "Indica incoterm, puerto destino, moneda (USD, CLP) y validez de la oferta.",
                "Genera PDF y envía al importador; cambia estado a Enviada.",
                "Al aceptar, convierte la cotización en pedido con un clic.",
            ],
            "modulo": {"nombre": "Cotizaciones", "endpoint": "admin.cotizaciones"},
            "alerta": "Precio y condiciones deben coincidir con lo que luego irá en factura comercial.",
        },
        {
            "id": "pedido",
            "numero": 4,
            "titulo": "Pedido confirmado",
            "icono": "fa-cart-shopping",
            "resumen": "Orden de compra interna tras aceptación del cliente.",
            "puntos": [
                "El pedido hereda líneas y totales de la cotización aceptada.",
                "Confirma fechas de preparación y condiciones de pago acordadas.",
                "Pasa a En preparación cuando inicie packing y certificación.",
                "Desde el pedido puedes crear el embarque asociado.",
            ],
            "modulo": {"nombre": "Pedidos", "endpoint": "admin.pedidos"},
            "alerta": "No embarcar sin pedido confirmado o sin abono según política comercial.",
        },
        {
            "id": "documentacion",
            "numero": 5,
            "titulo": "Documentación de exportación",
            "icono": "fa-folder-open",
            "resumen": "Checklist fitosanitario, origen, factura, packing list y BL.",
            "puntos": [
                "Sube certificado fitosanitario, certificado de origen y factura comercial.",
                "Packing list debe coincidir con pesos y bultos reales de la carga.",
                "Bill of Lading (BL) se vincula al embarque; revisa número de contenedor.",
                "Aprueba documentos antes del zarpe; pendientes generan alertas automáticas.",
            ],
            "modulo": {"nombre": "Documentación", "endpoint": "admin.documentos"},
            "alerta": "Documento vencido o rechazado puede detener la carga en aduana destino.",
        },
        {
            "id": "packing",
            "numero": 6,
            "titulo": "Packing y cadena de frío",
            "icono": "fa-snowflake",
            "resumen": "Dimensiones, peso y temperatura reefer correctos.",
            "puntos": [
                "Frutas: reefer 0°C a +2°C. Mariscos: -2°C a 0°C según producto.",
                "Usa la calculadora de contenedores para validar peso y volumen por mercado.",
                "Peso por caja y cantidad deben ser consistentes en packing list y BL.",
                "Evita sobrepeso: revisa límites viales del país destino.",
            ],
            "modulo": {"nombre": "Calculadora", "endpoint": "admin.calculadora_contenedores"},
            "alerta": "Diferencia entre peso declarado y peso real es motivo frecuente de multas.",
        },
        {
            "id": "embarque",
            "numero": 7,
            "titulo": "Embarque y logística",
            "icono": "fa-ship",
            "resumen": "Booking, contenedor, hitos y tracking hasta destino.",
            "puntos": [
                "Registra puerto origen/destino, naviera, booking, BL y tipo de contenedor.",
                "Actualiza hitos: producción → packing → certificación → zarpe → tránsito → arribo.",
                "Registra número de contenedor y ETA para el importador.",
                "Asocia costos logísticos para análisis de rentabilidad.",
            ],
            "modulo": {"nombre": "Embarques", "endpoint": "admin.embarques"},
            "alerta": "Cut-off de puerto incumplido implica rollover de nave y costos extra.",
        },
        {
            "id": "transito",
            "numero": 8,
            "titulo": "Tránsito marítimo",
            "icono": "fa-water",
            "resumen": "Seguimiento y comunicación al importador durante el viaje.",
            "puntos": [
                "Chile → México: típicamente 18–25 días según puerto y naviera.",
                "Actualiza tracking y notifica retrasos de inmediato.",
                "El importador puede seguir el estado desde el portal cliente.",
                "Mantén documentos aprobados disponibles para inspección en ruta si aplica.",
            ],
            "modulo": {"nombre": "Portal clientes", "endpoint": "portal.login"},
            "alerta": "Silencio logístico genera ansiedad comercial; comunica hitos clave.",
        },
        {
            "id": "aduana",
            "numero": 9,
            "titulo": "Aduana en destino",
            "icono": "fa-passport",
            "resumen": "Pedimento, inspección SENASICA/SAG equivalente y liberación.",
            "puntos": [
                "El importador presenta pedimento con documentos que enviaste desde Chile.",
                "Inspección fitosanitaria o sanitaria según producto (fruta vs marisco).",
                "Verifica que etiquetado y certificados cumplan requisitos del módulo Países.",
                "Resuelve incidencias documentales antes de que el contenedor genere demurrage.",
            ],
            "modulo": {"nombre": "Países y requisitos", "endpoint": "admin.paises"},
            "alerta": "Demurrage por documentos tardíos puede superar el margen de la operación.",
        },
        {
            "id": "cierre",
            "numero": 10,
            "titulo": "Entrega y cierre",
            "icono": "fa-circle-check",
            "resumen": "Conformidad del cliente y lecciones aprendidas.",
            "puntos": [
                "Confirma entrega en planta o CD del importador.",
                "Marca embarque como Entregado y pedido según corresponda.",
                "Archiva documentación final y revisa alertas pendientes.",
                "Registra incidencias en historial para mejorar la próxima operación.",
            ],
            "modulo": {"nombre": "Historial", "endpoint": "admin.historial"},
            "alerta": "Cierra operaciones para que reportes y KPIs reflejen la realidad.",
        },
    ],
    "errores_frecuentes": [
        "Documento pendiente o vencido al momento del zarpe.",
        "Packing list no coincide con factura ni con peso del contenedor.",
        "Requisitos del país no revisados antes de cotizar.",
        "Contenedor con sobrepeso o sobrevolumen.",
        "Cliente sin contrato vigente o sin acceso al portal.",
        "No actualizar ETA ni tracking durante el tránsito.",
    ],
}


MODULE_TOURS = {
    "resumen": {
        "titulo": "Panel ejecutivo",
        "steps": [
            {"element": "#tour-kpis", "title": "Indicadores clave", "description": "Exportaciones activas, países, documentos pendientes y alertas críticas en un vistazo.", "side": "bottom"},
            {"element": "#tour-operaciones", "title": "Operaciones activas", "description": "Cada fila muestra ruta, cliente, contenedores, ETA y estado documental.", "side": "top"},
            {"element": "#tour-alertas-panel", "title": "Alertas", "description": "Revisa documentos vencidos, embarques retrasados y tareas urgentes.", "side": "left"},
            {"element": "#nav-guia-importacion", "title": "Guía de importación", "description": "Accede siempre a la guía completa del proceso exportador desde el menú lateral.", "side": "right"},
        ],
    },
    "clientes": {
        "titulo": "Gestión de clientes",
        "steps": [
            {"element": "#tour-btn-nuevo", "title": "Nuevo cliente", "description": "Registra importadores con empresa, país, contacto y producto de interés.", "side": "bottom"},
            {"element": "#tour-kpis", "title": "Resumen CRM", "description": "Activos, prospectos y clientes con abono registrado.", "side": "bottom"},
            {"element": "#tour-filtros", "title": "Filtros", "description": "Filtra por estado comercial, abonos o línea de producto.", "side": "bottom"},
            {"element": "#tour-lista", "title": "Ficha del cliente", "description": "Entra al detalle para abonos, archivos, portal y historial comercial.", "side": "top"},
        ],
    },
    "cotizaciones": {
        "titulo": "Cotizaciones comerciales",
        "steps": [
            {"element": "#tour-btn-nuevo", "title": "Nueva cotización", "description": "Crea presupuestos con líneas de producto, incoterm y moneda.", "side": "bottom"},
            {"element": "#tour-kpis", "title": "Estados", "description": "Borradores, enviadas y aceptadas. Convierte aceptadas en pedido.", "side": "bottom"},
            {"element": "#tour-filtros", "title": "Filtrar por estado", "description": "Localiza cotizaciones vencidas o pendientes de respuesta.", "side": "bottom"},
            {"element": "#tour-lista", "title": "Acciones", "description": "PDF, editar y ver detalle. Desde el detalle puedes generar el pedido.", "side": "top"},
        ],
    },
    "pedidos": {
        "titulo": "Pedidos confirmados",
        "steps": [
            {"element": "#tour-btn-nuevo", "title": "Nuevo pedido", "description": "Crea manualmente o desde una cotización aceptada.", "side": "bottom"},
            {"element": "#tour-kpis", "title": "Pipeline comercial", "description": "Confirmados, en preparación y entregados.", "side": "bottom"},
            {"element": "#tour-filtros", "title": "Estados del pedido", "description": "Sigue el avance hasta la creación del embarque.", "side": "bottom"},
            {"element": "#tour-lista", "title": "Detalle y embarque", "description": "Desde el pedido confirmado puedes iniciar el embarque logístico.", "side": "top"},
        ],
    },
    "embarques": {
        "titulo": "Embarques y logística",
        "steps": [
            {"element": "#tour-btn-nuevo", "title": "Nuevo embarque", "description": "Registra la operación con puertos, naviera, contenedor y fechas.", "side": "bottom"},
            {"element": "#tour-pipeline", "title": "Flujo comercial", "description": "Cotización → Pedido → Embarque → Entrega. Este módulo es el núcleo logístico.", "side": "bottom"},
            {"element": "#tour-kpis", "title": "Estado operativo", "description": "Embarques en curso, en tránsito y entregados.", "side": "bottom"},
            {"element": "#tour-filtros", "title": "Filtros logísticos", "description": "Filtra por estado: preparación, tránsito, destino, incidencias.", "side": "bottom"},
            {"element": "#tour-lista", "title": "Detalle del embarque", "description": "Hitos, tracking, costos, documentos y timeline de la operación.", "side": "top"},
        ],
    },
    "documentos": {
        "titulo": "Gestión documental",
        "steps": [
            {"element": "#tour-btn-nuevo", "title": "Subir documento", "description": "Certificados, BL, facturas, packing list. Clasifica por tipo y embarque.", "side": "bottom"},
            {"element": "#tour-kpis", "title": "Control documental", "description": "Pendientes, aprobados y vencidos. Prioriza los que bloquean el zarpe.", "side": "bottom"},
            {"element": "#tour-filtros-estado", "title": "Por estado", "description": "Aprueba o rechaza documentos. Los pendientes alimentan las alertas.", "side": "bottom"},
            {"element": "#tour-filtros-tipo", "title": "Por tipo", "description": "Fitosanitario, origen, BL, factura comercial, etc.", "side": "bottom"},
            {"element": "#tour-lista", "title": "Listado", "description": "Descarga, edita estado y vincula a cliente, país o embarque.", "side": "top"},
        ],
    },
    "guia": {
        "titulo": "Guía de importación",
        "steps": [
            {"element": "#tour-timeline", "title": "Flujo completo", "description": "10 etapas desde planificación hasta cierre. Haz clic en cada número para ir al capítulo.", "side": "bottom"},
            {"element": "#tour-errores", "title": "Evita estos errores", "description": "Los problemas más comunes en aduana y logística. Revísalos antes de cada embarque.", "side": "left"},
        ],
    },
    "paises": {
        "titulo": "Países y requisitos",
        "steps": [
            {"element": "#tour-btn-nuevo", "title": "Nuevo país", "description": "Registra mercados destino con código ISO y normativa de importación.", "side": "bottom"},
            {"element": "#tour-kpis", "title": "Cobertura", "description": "Países activos, requisitos totales y obligatorios por mercado.", "side": "bottom"},
            {"element": "#tour-lista", "title": "Ficha por país", "description": "Entra al detalle para editar requisitos fitosanitarios, documentos y notas.", "side": "top"},
        ],
    },
    "alertas": {
        "titulo": "Centro de alertas",
        "steps": [
            {"element": "#tour-intro", "title": "Priorización automática", "description": "El sistema cruza embarques, documentos y cotizaciones para señalar lo urgente.", "side": "bottom"},
            {"element": "#tour-lista", "title": "Alertas activas", "description": "Cada tarjeta indica nivel (crítica, advertencia, info) y enlace al módulo correspondiente.", "side": "top"},
            {"element": "#tour-dashboard-link", "title": "Volver al resumen", "description": "Desde aquí puedes ir al panel ejecutivo para ver KPIs y operaciones activas.", "side": "bottom"},
        ],
    },
    "tareas": {
        "titulo": "Tareas internas",
        "steps": [
            {"element": "#tour-intro", "title": "Operaciones del equipo", "description": "Asigna pendientes de documentación, booking o inspección vinculados a embarques.", "side": "bottom"},
            {"element": "#tour-btn-nuevo", "title": "Nueva tarea", "description": "Asigna pendientes al equipo con responsable, prioridad y fecha límite.", "side": "bottom"},
            {"element": "#tour-filtros", "title": "Estados", "description": "Filtra pendientes, en curso, completadas o canceladas.", "side": "bottom"},
            {"element": "#tour-lista", "title": "Seguimiento", "description": "Vincula tareas a embarques. Marca completadas desde el listado.", "side": "top"},
        ],
    },
    "calculadora": {
        "titulo": "Calculadora de contenedores",
        "steps": [
            {"element": "#tour-form", "title": "Datos de carga", "description": "Selecciona mercado destino, tipo de contenedor y dimensiones de caja en cm.", "side": "right"},
            {"element": "#tour-resultado", "title": "Resultado", "description": "Volumen, peso y cajas máximas según límites del país seleccionado.", "side": "left"},
            {"element": "#tour-comparativa", "title": "Comparativa multi-mercado", "description": "Tras calcular, compara la misma carga en Chile, México, Perú y otros destinos.", "side": "top"},
        ],
    },
    "productos": {
        "titulo": "Catálogo de productos",
        "steps": [
            {"element": "#tour-btn-nuevo", "title": "Nuevo producto", "description": "Define categoría, temperatura, dimensiones y ficha técnica.", "side": "bottom"},
            {"element": "#tour-lista", "title": "Líneas de exportación", "description": "Alimenta cotizaciones, requisitos por país y la calculadora de contenedores.", "side": "top"},
        ],
    },
    "mensajes": {
        "titulo": "Bandeja de mensajes",
        "steps": [
            {"element": "#tour-kpis", "title": "Resumen", "description": "Pendientes, leídos y total de consultas del formulario web.", "side": "bottom"},
            {"element": "#tour-filtros", "title": "Buscar y filtrar", "description": "Localiza por nombre, email o empresa. Filtra pendientes vs leídos.", "side": "bottom"},
            {"element": "#tour-lista", "title": "Acciones", "description": "Crear cotización, marcar leído o responder por email al importador.", "side": "top"},
        ],
    },
    "notificaciones": {
        "titulo": "Notificaciones por email",
        "steps": [
            {"element": "#tour-btn-enviar", "title": "Enviar resumen", "description": "Dispara manualmente un email con las alertas activas al equipo comercial.", "side": "bottom"},
            {"element": "#tour-smtp", "title": "Estado SMTP", "description": "Verifica que el servidor de correo esté configurado en variables de entorno.", "side": "bottom"},
            {"element": "#tour-lista", "title": "Historial", "description": "Registro de cada envío: fecha, destinatario, título y estado.", "side": "top"},
        ],
    },
    "reportes": {
        "titulo": "Reportes e indicadores",
        "steps": [
            {"element": "#tour-kpis", "title": "KPIs del mes", "description": "Ventas, clientes activos, contenedores enviados y margen global.", "side": "bottom"},
            {"element": "#tour-ventas", "title": "Ventas por país y producto", "description": "Distribución comercial para priorizar mercados y líneas.", "side": "top"},
            {"element": "#tour-analisis", "title": "Tendencias y clientes", "description": "Exportaciones mensuales y ranking de importadores por volumen.", "side": "top"},
            {"element": "#tour-rentabilidad", "title": "Rentabilidad por embarque", "description": "Compara venta vs costos logísticos registrados en cada operación.", "side": "top"},
        ],
    },
    "contratos": {
        "titulo": "Gestión de contratos",
        "steps": [
            {"element": "#tour-intro", "title": "Acuerdos marco", "description": "Registra contratos por cliente y país con vigencia y PDF firmado.", "side": "bottom"},
            {"element": "#tour-btn-nuevo", "title": "Nuevo contrato", "description": "Crea un acuerdo comercial con fechas de inicio y fin.", "side": "bottom"},
            {"element": "#tour-filtros", "title": "Estados", "description": "Filtra vigentes, por vencer, vencidos o borradores.", "side": "bottom"},
            {"element": "#tour-lista", "title": "Listado", "description": "Entra al detalle para revisar condiciones y renovar antes del vencimiento.", "side": "top"},
        ],
    },
    "plantillas": {
        "titulo": "Biblioteca de plantillas",
        "steps": [
            {"element": "#tour-intro", "title": "Formatos estándar", "description": "Repositorio de documentos modelo para facturación, packing y procedimientos.", "side": "bottom"},
            {"element": "#tour-btn-nuevo", "title": "Nueva plantilla", "description": "Sube formatos modelo: facturas, packing lists, contratos y procedimientos.", "side": "bottom"},
            {"element": "#tour-filtros", "title": "Por tipo", "description": "Filtra documentos comerciales, logísticos o internos.", "side": "bottom"},
            {"element": "#tour-lista", "title": "Repositorio", "description": "Descarga y edita plantillas activas para estandarizar la operación.", "side": "top"},
        ],
    },
    "historial": {
        "titulo": "Historial de auditoría",
        "steps": [
            {"element": "#tour-filtros", "title": "Filtrar por entidad", "description": "Clientes, embarques, documentos, contratos y más.", "side": "bottom"},
            {"element": "#tour-lista", "title": "Registro de acciones", "description": "Quién hizo qué, cuándo y sobre qué registro. Útil para cumplimiento.", "side": "top"},
        ],
    },
    "usuarios": {
        "titulo": "Usuarios y roles",
        "steps": [
            {"element": "#tour-btn-nuevo", "title": "Nuevo usuario", "description": "Crea accesos con email corporativo y rol (CEO, comercial, operaciones, lectura).", "side": "bottom"},
            {"element": "#tour-lista", "title": "Equipo", "description": "Activa o desactiva usuarios y edita permisos desde cada fila.", "side": "top"},
            {"element": "#tour-roles", "title": "Roles disponibles", "description": "CEO tiene acceso total; lectura solo consulta sin editar.", "side": "top"},
        ],
    },
}


def get_tour(module_key):
    return MODULE_TOURS.get(module_key)
