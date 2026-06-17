"""Tutoriales y guía de importación para el portal cliente."""

PORTAL_IMPORT_GUIDE = {
    "titulo": "Guía para importar correctamente",
    "subtitulo": "Checklist del importador · Chile → México y Latinoamérica",
    "intro": (
        "Esta guía te ayuda a recibir exportaciones de Patagonia Sur sin sorpresas en aduana: "
        "qué revisar antes del zarpe, cómo seguir el contenedor y qué documentos tener listos "
        "cuando llegue a tu puerto."
    ),
    "pasos": [
        {
            "id": "antes-zarpe",
            "titulo": "Antes del zarpe (Chile)",
            "icono": "fa-ship",
            "items": [
                "Confirma pedido y condiciones de pago con tu ejecutivo Patagonia Sur.",
                "Verifica que la factura comercial coincida con el pedido acordado.",
                "Solicita copia del certificado fitosanitario y certificado de origen.",
            ],
        },
        {
            "id": "transito",
            "titulo": "Durante el tránsito",
            "icono": "fa-water",
            "items": [
                "Sigue el estado del embarque en este portal (ETD, ETA, ubicación).",
                "Prepara al agente aduanal con datos del BL y número de contenedor.",
                "Confirma requisitos SENASICA / sanitarios según tu producto.",
            ],
        },
        {
            "id": "aduana",
            "titulo": "En aduana destino",
            "icono": "fa-passport",
            "items": [
                "Presenta pedimento con factura, packing list y certificados.",
                "Coordina inspección fitosanitaria o sanitaria si aplica.",
                "Evita demurrage: libera contenedor dentro del plazo acordado.",
            ],
        },
        {
            "id": "recepcion",
            "titulo": "Recepción de mercancía",
            "icono": "fa-warehouse",
            "items": [
                "Verifica temperatura y calidad al destufar (reefer).",
                "Reporta incidencias dentro de las 24–48 h con fotos y acta.",
                "Confirma conformidad de entrega con tu ejecutivo.",
            ],
        },
    ],
    "documentos_clave": [
        ("factura", "Factura comercial"),
        ("packing", "Packing list"),
        ("bl", "Bill of Lading"),
        ("fitosanitario", "Certificado fitosanitario"),
        ("origen", "Certificado de origen"),
    ],
    "errores_frecuentes": [
        "No revisar documentos en el portal antes del arribo del contenedor.",
        "Datos del BL o contenedor distintos a los del pedimento.",
        "Demora en inspección SENASICA por certificados incompletos.",
        "No firmar digitalmente documentos que Patagonia Sur ya envió firmados.",
        "Destufar reefer sin verificar temperatura y plazo de reclamo.",
        "Ignorar alertas de retraso o documentación pendiente en el portal.",
    ],
    "consejos_portal": [
        "Revisa Alertas al entrar: retrasos, firmas pendientes y arribos próximos.",
        "Descarga facturas y BL desde Documentos o Facturas antes del arribo.",
        "Firma digitalmente los documentos que lo requieran para trazabilidad.",
        "Usa el detalle de cada embarque para compartir ETA con tu agente aduanal.",
    ],
}

# Alias usado en portal_utils y plantillas
PORTAL_GUIA_IMPORTADOR = PORTAL_IMPORT_GUIDE

PORTAL_MODULE_TOURS = {
    "inicio": {
        "titulo": "Tu panel de importador",
        "steps": [
            {"element": "#tour-kpis", "title": "Tarjeta de bienvenida", "description": "Resumen personal, alertas urgentes, accesos rápidos y estado de tus exportaciones.", "side": "bottom"},
            {"element": "#tour-embarque", "title": "Seguimiento principal", "description": "El envío más relevante con ruta, ETA, contenedor y línea de tiempo.", "side": "top"},
            {"element": "#tour-sidebar", "title": "Accesos rápidos", "description": "Tu ejecutivo, documentos recientes, pedidos y enlace a la guía.", "side": "left"},
            {"element": "#nav-portal-guia", "title": "Guía de importación", "description": "Checklist completo para recibir carga desde Chile sin problemas aduaneros.", "side": "right"},
        ],
    },
    "embarques": {
        "titulo": "Seguimiento de embarques",
        "steps": [
            {"element": "#tour-filtros", "title": "Tu flota", "description": "Filtra por activos en tránsito o ya entregados. El hero resume el total de envíos.", "side": "bottom"},
            {"element": "#tour-lista", "title": "Tarjetas de embarque", "description": "Cada contenedor muestra ruta con barco, progreso, BL, fechas y ubicación actual.", "side": "top"},
        ],
    },
    "pedidos": {
        "titulo": "Tus pedidos",
        "steps": [
            {"element": "#tour-intro", "title": "Filtros comerciales", "description": "Filtra pedidos en curso o ya entregados. El hero resume tu operación de compra.", "side": "bottom"},
            {"element": "#tour-lista", "title": "Detalle del pedido", "description": "Flujo visual del estado, montos, productos y embarques vinculados con iconos.", "side": "top"},
        ],
    },
    "facturas": {
        "titulo": "Facturas y comerciales",
        "steps": [
            {"element": "#tour-intro", "title": "Documentos comerciales", "description": "Facturas, packing lists, BL y guías de despacho aprobados.", "side": "bottom"},
            {"element": "#tour-lista", "title": "Línea de tiempo", "description": "Comerciales agrupados por año en orden cronológico, con descarga y firma.", "side": "top"},
        ],
    },
    "documentos": {
        "titulo": "Expediente documental",
        "steps": [
            {"element": "#tour-intro", "title": "Tu documentación", "description": "Certificados, BL, facturas y documentos de exportación aprobados.", "side": "bottom"},
            {"element": "#tour-lista", "title": "Línea de tiempo", "description": "Documentos agrupados por año, en orden cronológico, con descarga y firma.", "side": "top"},
        ],
    },
    "alertas": {
        "titulo": "Centro de alertas",
        "steps": [
            {"element": "#tour-intro", "title": "Radar de exportaciones", "description": "Barco en ruta Chile → destino, resumen de alertas críticas y avisos.", "side": "bottom"},
            {"element": "#tour-lista", "title": "Tus alertas", "description": "Filtra por embarques, documentos o pagos. Cada alerta enlaza a la acción correspondiente.", "side": "top"},
        ],
    },
    "guia": {
        "titulo": "Guía del importador",
        "steps": [
            {"element": "#tour-timeline", "title": "Flujo de importación", "description": "Cuatro etapas: antes del zarpe, tránsito, aduana y recepción.", "side": "bottom"},
            {"element": "#tour-pasos", "title": "Checklist detallado", "description": "Revisa cada etapa con acciones concretas para tu equipo.", "side": "top"},
            {"element": "#tour-errores", "title": "Evita estos errores", "description": "Los problemas más frecuentes al importar frutas y mariscos desde Chile.", "side": "left"},
        ],
    },
}
