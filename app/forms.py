from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, TextAreaField, SelectField, FloatField, DateField, IntegerField
from wtforms.validators import DataRequired, Email, Optional, Length, NumberRange

from app.constants import (
    CLIENTE_ESTADOS, PRODUCTO_CATEGORIAS, ABONO_TIPOS, MONEDAS,
    COTIZACION_ESTADOS, UNIDADES_LINEA, PEDIDO_ESTADOS,
    EMBARQUE_ESTADOS, CARGA_TIPOS, PUERTOS_ORIGEN, PUERTOS_DESTINO,
    DOCUMENTO_TIPOS, DOCUMENTO_ESTADOS, REQUISITO_TIPOS,
    LOGISTICA_ETAPAS, USER_ROLES, TAREA_PRIORIDADES, TAREA_ESTADOS,
    CONTENEDOR_TIPOS, COSTO_TIPOS, CONTRATO_ESTADOS, PLANTILLA_TIPOS,
    PRODUCTO_FORMATOS, CLIENTE_TIPOS, MERCADOS_PESO,
)


class ContactoForm(FlaskForm):
    nombre = StringField("Nombre", validators=[DataRequired(), Length(max=100)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=120)])
    telefono = StringField("Teléfono", validators=[Optional(), Length(max=20)])
    empresa = StringField("Empresa", validators=[Optional(), Length(max=120)])
    mensaje = TextAreaField("Mensaje", validators=[DataRequired()])


class LoginForm(FlaskForm):
    username = StringField("Usuario", validators=[DataRequired(), Length(max=120)])
    password = PasswordField("Clave", validators=[DataRequired(), Length(min=4, max=128)])


class ClientFolderForm(FlaskForm):
    nombre = StringField("Nombre del cliente / carpeta", validators=[DataRequired(), Length(max=120)])
    empresa = StringField("Empresa", validators=[Optional(), Length(max=120)])
    contacto = StringField("Contacto", validators=[Optional(), Length(max=100)])
    email = StringField("Email", validators=[Optional(), Email(), Length(max=120)])
    telefono = StringField("Teléfono", validators=[Optional(), Length(max=30)])
    pais = StringField("País", validators=[Optional(), Length(max=80)])
    ciudad = StringField("Ciudad", validators=[Optional(), Length(max=80)])
    tipo_cliente = SelectField("Tipo de cliente", choices=[(k, v) for k, v in CLIENTE_TIPOS.items()], default="importador")
    estado = SelectField("Clasificación", choices=[(k, v) for k, v in CLIENTE_ESTADOS.items()], default="prospecto")
    producto_id = SelectField("Producto de interés", coerce=int, validators=[Optional()])
    ejecutivo_id = SelectField("Ejecutivo asignado", coerce=int, validators=[Optional()])
    valor_estimado = FloatField("Valor estimado", validators=[Optional(), NumberRange(min=0)])
    moneda_estimada = SelectField("Moneda", choices=[(m, m) for m in MONEDAS], default="USD")
    condiciones_comerciales = TextAreaField("Condiciones comerciales", validators=[Optional()])
    notas = TextAreaField("Notas / información adicional", validators=[Optional()])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from app.models import Product, AdminUser
        self.producto_id.choices = [(0, "— Sin asignar —")] + [
            (p.id, p.nombre) for p in Product.query.filter_by(activo=True).order_by(Product.orden).all()
        ]
        self.ejecutivo_id.choices = [(0, "— Sin asignar —")] + [
            (u.id, u.nombre or u.username) for u in AdminUser.query.filter_by(activo=True).order_by(AdminUser.username).all()
        ]


class ClientAbonoForm(FlaskForm):
    monto = FloatField("Monto", validators=[DataRequired(), NumberRange(min=0.01)])
    moneda = SelectField("Moneda", choices=[(m, m) for m in MONEDAS], default="USD")
    tipo = SelectField("Tipo", choices=[(k, v) for k, v in ABONO_TIPOS.items()], default="abono")
    product_id = SelectField("Producto", coerce=int, validators=[Optional()])
    fecha = DateField("Fecha", validators=[DataRequired()], format="%Y-%m-%d")
    referencia = StringField("Referencia / Nº operación", validators=[Optional(), Length(max=120)])
    notas = TextAreaField("Notas", validators=[Optional()])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from app.models import Product
        self.product_id.choices = [(0, "— General —")] + [
            (p.id, p.nombre) for p in Product.query.filter_by(activo=True).order_by(Product.orden).all()
        ]


class ProductForm(FlaskForm):
    nombre = StringField("Nombre comercial", validators=[DataRequired(), Length(max=120)])
    categoria = SelectField("Categoría", choices=[(k, v) for k, v in PRODUCTO_CATEGORIAS.items()], default="otro")
    formato_venta = SelectField("Formato de venta", choices=[(k, v) for k, v in PRODUCTO_FORMATOS.items()], default="cajas")
    descripcion = TextAreaField("Descripción", validators=[Optional()])
    peso_caja_kg = FloatField("Peso por caja (kg)", validators=[Optional(), NumberRange(min=0)])
    caja_largo_cm = FloatField("Largo caja (cm)", validators=[Optional(), NumberRange(min=0)])
    caja_ancho_cm = FloatField("Ancho caja (cm)", validators=[Optional(), NumberRange(min=0)])
    caja_alto_cm = FloatField("Alto caja (cm)", validators=[Optional(), NumberRange(min=0)])
    temperatura = StringField("Temperatura requerida", validators=[Optional(), Length(max=60)])
    vida_util_dias = IntegerField("Vida útil (días)", validators=[Optional(), NumberRange(min=0)])
    paises_permitidos = StringField("Países permitidos", validators=[Optional(), Length(max=300)], description="Separados por coma")
    certificaciones = TextAreaField("Certificaciones necesarias", validators=[Optional()])
    orden = IntegerField("Orden", validators=[Optional(), NumberRange(min=0)], default=0)
    imagen = FileField("Foto del producto", validators=[Optional(), FileAllowed(["png", "jpg", "jpeg", "webp"], "Imagen")])
    ficha = FileField("Ficha técnica (PDF)", validators=[Optional(), FileAllowed(["pdf"], "Solo PDF")])


class ClientFileUploadForm(FlaskForm):
    archivo = FileField(
        "Archivo",
        validators=[
            DataRequired(),
            FileAllowed(
                ["pdf", "png", "jpg", "jpeg", "gif", "webp", "doc", "docx", "xls", "xlsx", "csv", "txt", "zip"],
                "Tipo de archivo no permitido.",
            ),
        ],
    )


class CotizacionForm(FlaskForm):
    cliente_nombre = StringField("Nombre del cliente", validators=[DataRequired(), Length(max=120)])
    cliente_empresa = StringField("Empresa", validators=[Optional(), Length(max=120)])
    cliente_email = StringField("Email", validators=[Optional(), Email(), Length(max=120)])
    cliente_telefono = StringField("Teléfono", validators=[Optional(), Length(max=30)])
    cliente_pais = StringField("País", validators=[Optional(), Length(max=80)])
    folder_id = SelectField("Cliente registrado", coerce=int, validators=[Optional()])
    estado = SelectField("Estado", choices=[(k, v) for k, v in COTIZACION_ESTADOS.items()], default="borrador")
    moneda = SelectField("Moneda", choices=[(m, m) for m in MONEDAS], default="USD")
    incoterm = SelectField("Incoterm", choices=[
        ("FOB", "FOB"), ("CIF", "CIF"), ("CFR", "CFR"), ("EXW", "EXW"), ("DAP", "DAP"),
    ], default="FOB")
    validez_dias = IntegerField("Validez (días)", validators=[DataRequired(), NumberRange(min=1, max=365)], default=15)
    descuento_pct = FloatField("Descuento %", validators=[Optional(), NumberRange(min=0, max=100)], default=0)
    condiciones = TextAreaField("Condiciones comerciales", validators=[Optional()])
    notas = TextAreaField("Notas internas", validators=[Optional()])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from app.models import ClientFolder
        self.folder_id.choices = [(0, "— Sin vincular —")] + [
            (c.id, c.nombre) for c in ClientFolder.query.order_by(ClientFolder.nombre).all()
        ]


class PedidoForm(FlaskForm):
    cliente_nombre = StringField("Nombre del cliente", validators=[DataRequired(), Length(max=120)])
    cliente_empresa = StringField("Empresa", validators=[Optional(), Length(max=120)])
    cliente_email = StringField("Email", validators=[Optional(), Email(), Length(max=120)])
    cliente_telefono = StringField("Teléfono", validators=[Optional(), Length(max=30)])
    cliente_pais = StringField("País", validators=[Optional(), Length(max=80)])
    folder_id = SelectField("Cliente registrado", coerce=int, validators=[Optional()])
    estado = SelectField("Estado", choices=[(k, v) for k, v in PEDIDO_ESTADOS.items()], default="confirmado")
    moneda = SelectField("Moneda", choices=[(m, m) for m in MONEDAS], default="USD")
    incoterm = SelectField("Incoterm", choices=[
        ("FOB", "FOB"), ("CIF", "CIF"), ("CFR", "CFR"), ("EXW", "EXW"), ("DAP", "DAP"),
    ], default="FOB")
    descuento_pct = FloatField("Descuento %", validators=[Optional(), NumberRange(min=0, max=100)], default=0)
    anticipo_monto = FloatField("Anticipo recibido", validators=[Optional(), NumberRange(min=0)], default=0)
    fecha_entrega_estimada = DateField("Entrega estimada", validators=[Optional()], format="%Y-%m-%d")
    condiciones = TextAreaField("Condiciones de entrega / pago", validators=[Optional()])
    notas = TextAreaField("Notas internas", validators=[Optional()])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from app.models import ClientFolder
        self.folder_id.choices = [(0, "— Sin vincular —")] + [
            (c.id, c.nombre) for c in ClientFolder.query.order_by(ClientFolder.nombre).all()
        ]


class EmbarqueForm(FlaskForm):
    order_id = SelectField("Pedido vinculado", coerce=int, validators=[DataRequired()])
    estado = SelectField("Estado", choices=[(k, v) for k, v in EMBARQUE_ESTADOS.items()], default="programado")
    responsable_id = SelectField("Responsable interno", coerce=int, validators=[Optional()])
    puerto_origen = SelectField("Puerto origen (Chile)", choices=[(p, p) for p in PUERTOS_ORIGEN], default="San Antonio")
    puerto_destino = SelectField("Puerto destino", choices=[(p, p) for p in PUERTOS_DESTINO], default="Manzanillo")
    naviera = StringField("Naviera / línea", validators=[Optional(), Length(max=120)])
    numero_contenedor = StringField("Nº contenedor", validators=[Optional(), Length(max=40)])
    numero_bl = StringField("Nº BL (Bill of Lading)", validators=[Optional(), Length(max=60)])
    numero_booking = StringField("Nº booking", validators=[Optional(), Length(max=60)])
    tipo_contenedor = SelectField("Tipo contenedor", choices=[(k, v) for k, v in CONTENEDOR_TIPOS.items()], default="40")
    tipo_carga = SelectField("Tipo de carga", choices=[(k, v) for k, v in CARGA_TIPOS.items()], default="refrigerado")
    temperatura = StringField("Temperatura", validators=[Optional(), Length(max=40)], default="-1°C a +4°C")
    transporte_terrestre = StringField("Transporte terrestre", validators=[Optional(), Length(max=120)])
    agente_aduana = StringField("Agente de aduana", validators=[Optional(), Length(max=120)])
    ultima_ubicacion = StringField("Última ubicación", validators=[Optional(), Length(max=200)])
    tracking_notas = TextAreaField("Notas de seguimiento", validators=[Optional()])
    etd = DateField("ETD (salida estimada)", validators=[Optional()], format="%Y-%m-%d")
    eta = DateField("ETA (llegada estimada)", validators=[Optional()], format="%Y-%m-%d")
    fecha_zarpe = DateField("Fecha de zarpe", validators=[Optional()], format="%Y-%m-%d")
    notas = TextAreaField("Notas logísticas", validators=[Optional()])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from app.models import Order, AdminUser
        pedidos = Order.query.filter(Order.estado.notin_(["cancelado", "entregado"])).order_by(Order.created_at.desc()).all()
        self.order_id.choices = [(p.id, f"{p.numero} — {p.cliente_nombre}") for p in pedidos] or [(0, "— Sin pedidos disponibles —")]
        self.responsable_id.choices = [(0, "— Sin asignar —")] + [
            (u.id, u.nombre or u.username) for u in AdminUser.query.filter_by(activo=True).order_by(AdminUser.username).all()
        ]


class TrackingUpdateForm(FlaskForm):
    ultima_ubicacion = StringField("Última ubicación", validators=[DataRequired(), Length(max=200)])
    tracking_notas = TextAreaField("Observaciones", validators=[Optional()])
    estado = SelectField("Estado del embarque", choices=[(k, v) for k, v in EMBARQUE_ESTADOS.items()])


class TareaForm(FlaskForm):
    titulo = StringField("Título", validators=[DataRequired(), Length(max=200)])
    descripcion = TextAreaField("Descripción", validators=[Optional()])
    responsable_id = SelectField("Responsable", coerce=int, validators=[Optional()])
    shipment_id = SelectField("Embarque", coerce=int, validators=[Optional()])
    folder_id = SelectField("Cliente", coerce=int, validators=[Optional()])
    prioridad = SelectField("Prioridad", choices=[(k, v) for k, v in TAREA_PRIORIDADES.items()], default="media")
    estado = SelectField("Estado", choices=[(k, v) for k, v in TAREA_ESTADOS.items()], default="pendiente")
    fecha_limite = DateField("Fecha límite", validators=[Optional()], format="%Y-%m-%d")
    comentarios = TextAreaField("Comentarios", validators=[Optional()])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from app.models import AdminUser, Shipment, ClientFolder
        self.responsable_id.choices = [(0, "— Sin asignar —")] + [
            (u.id, u.nombre or u.username) for u in AdminUser.query.filter_by(activo=True).all()
        ]
        self.shipment_id.choices = [(0, "— Sin embarque —")] + [
            (e.id, f"{e.numero} — {e.cliente_nombre}") for e in Shipment.query.order_by(Shipment.created_at.desc()).limit(50).all()
        ]
        self.folder_id.choices = [(0, "— Sin cliente —")] + [
            (c.id, c.nombre) for c in ClientFolder.query.order_by(ClientFolder.nombre).all()
        ]


class UsuarioForm(FlaskForm):
    username = StringField("Email / usuario", validators=[DataRequired(), Email(), Length(max=120)])
    nombre = StringField("Nombre", validators=[Optional(), Length(max=100)])
    rol = SelectField("Rol", choices=[(k, v) for k, v in USER_ROLES.items()], default="comercial")
    activo = SelectField("Estado", choices=[("1", "Activo"), ("0", "Inactivo")], default="1")
    password = PasswordField("Contraseña", validators=[Optional(), Length(min=4, max=128)])


class ContainerCalcForm(FlaskForm):
    mercado_destino = SelectField(
        "Mercado destino",
        choices=[(k, v["nombre"]) for k, v in MERCADOS_PESO.items()],
        default="CL",
    )
    tipo_contenedor = SelectField("Tipo contenedor", choices=[(k, v) for k, v in CONTENEDOR_TIPOS.items()], default="40")
    cajas_largo = FloatField("Largo caja (cm)", validators=[DataRequired(), NumberRange(min=1)])
    cajas_ancho = FloatField("Ancho caja (cm)", validators=[DataRequired(), NumberRange(min=1)])
    cajas_alto = FloatField("Alto caja (cm)", validators=[DataRequired(), NumberRange(min=1)])
    peso_caja = FloatField("Peso por caja (kg)", validators=[DataRequired(), NumberRange(min=0.01)])
    cantidad_cajas = IntegerField("Cantidad de cajas", validators=[DataRequired(), NumberRange(min=1)])


class CountryForm(FlaskForm):
    nombre = StringField("Nombre del país", validators=[DataRequired(), Length(max=80)])
    codigo = StringField("Código ISO", validators=[DataRequired(), Length(min=2, max=5)])
    notas = TextAreaField("Notas generales", validators=[Optional()])
    activo = SelectField("Estado", choices=[("1", "Activo"), ("0", "Inactivo")], default="1")


class CountryRequirementForm(FlaskForm):
    tipo = SelectField("Tipo", choices=[(k, v) for k, v in REQUISITO_TIPOS.items()], default="documento")
    titulo = StringField("Título", validators=[DataRequired(), Length(max=200)])
    descripcion = TextAreaField("Descripción / detalle", validators=[Optional()])
    product_id = SelectField("Producto específico", coerce=int, validators=[Optional()])
    obligatorio = SelectField("Obligatorio", choices=[("1", "Sí"), ("0", "No")], default="1")
    orden = IntegerField("Orden", validators=[Optional(), NumberRange(min=0)], default=0)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from app.models import Product
        self.product_id.choices = [(0, "— Todos los productos —")] + [
            (p.id, p.nombre) for p in Product.query.filter_by(activo=True).order_by(Product.orden).all()
        ]


class DocumentoForm(FlaskForm):
    titulo = StringField("Título del documento", validators=[DataRequired(), Length(max=200)])
    tipo = SelectField("Tipo", choices=[(k, v) for k, v in DOCUMENTO_TIPOS.items()], default="otro")
    estado = SelectField("Estado", choices=[(k, v) for k, v in DOCUMENTO_ESTADOS.items()], default="pendiente")
    folder_id = SelectField("Cliente", coerce=int, validators=[Optional()])
    shipment_id = SelectField("Embarque", coerce=int, validators=[Optional()])
    country_id = SelectField("País", coerce=int, validators=[Optional()])
    product_id = SelectField("Producto", coerce=int, validators=[Optional()])
    fecha_vencimiento = DateField("Fecha de vencimiento", validators=[Optional()], format="%Y-%m-%d")
    comentarios = TextAreaField("Comentarios internos", validators=[Optional()])
    archivo = FileField(
        "Archivo PDF",
        validators=[
            Optional(),
            FileAllowed(["pdf"], "Solo se permiten archivos PDF."),
        ],
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from app.models import ClientFolder, Shipment, Country, Product
        self.folder_id.choices = [(0, "— Sin cliente —")] + [
            (c.id, c.nombre) for c in ClientFolder.query.order_by(ClientFolder.nombre).all()
        ]
        self.shipment_id.choices = [(0, "— Sin embarque —")] + [
            (e.id, f"{e.numero} — {e.cliente_nombre}") for e in Shipment.query.order_by(Shipment.created_at.desc()).all()
        ]
        self.country_id.choices = [(0, "— Sin país —")] + [
            (p.id, p.nombre) for p in Country.query.filter_by(activo=True).order_by(Country.nombre).all()
        ]
        self.product_id.choices = [(0, "— Sin producto —")] + [
            (p.id, p.nombre) for p in Product.query.filter_by(activo=True).order_by(Product.orden).all()
        ]


class PaisDocumentoUploadForm(FlaskForm):
    titulo = StringField("Título del documento", validators=[DataRequired(), Length(max=200)])
    tipo = SelectField("Tipo", choices=[(k, v) for k, v in DOCUMENTO_TIPOS.items()], default="otro")
    fecha_vencimiento = DateField("Vencimiento", validators=[Optional()], format="%Y-%m-%d")
    comentarios = TextAreaField("Comentarios", validators=[Optional()])
    archivo = FileField(
        "Archivo PDF",
        validators=[
            DataRequired("Debes seleccionar un archivo PDF."),
            FileAllowed(["pdf"], "Solo se permiten archivos PDF."),
        ],
    )


class CostoForm(FlaskForm):
    tipo = SelectField("Tipo de costo", choices=[(k, v) for k, v in COSTO_TIPOS.items()], default="otro")
    concepto = StringField("Concepto", validators=[DataRequired(), Length(max=200)])
    monto = FloatField("Monto", validators=[DataRequired(), NumberRange(min=0)])
    moneda = SelectField("Moneda", choices=[(m, m) for m in MONEDAS], default="USD")
    notas = TextAreaField("Notas", validators=[Optional()])


class ContratoForm(FlaskForm):
    titulo = StringField("Título del contrato", validators=[DataRequired(), Length(max=200)])
    folder_id = SelectField("Cliente", coerce=int, validators=[Optional()])
    country_id = SelectField("País", coerce=int, validators=[Optional()])
    product_id = SelectField("Producto", coerce=int, validators=[Optional()])
    responsable_id = SelectField("Responsable", coerce=int, validators=[Optional()])
    estado = SelectField("Estado", choices=[(k, v) for k, v in CONTRATO_ESTADOS.items()], default="borrador")
    fecha_inicio = DateField("Fecha inicio", validators=[Optional()], format="%Y-%m-%d")
    fecha_fin = DateField("Fecha término", validators=[Optional()], format="%Y-%m-%d")
    renovacion_auto = SelectField("Renovación automática", choices=[("0", "No"), ("1", "Sí")], default="0")
    condiciones = TextAreaField("Condiciones comerciales", validators=[Optional()])
    notas = TextAreaField("Notas internas", validators=[Optional()])
    archivo = FileField(
        "Archivo PDF",
        validators=[Optional(), FileAllowed(["pdf"], "Solo PDF.")],
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from app.models import ClientFolder, Country, Product, AdminUser
        self.folder_id.choices = [(0, "— Sin cliente —")] + [
            (c.id, c.nombre) for c in ClientFolder.query.order_by(ClientFolder.nombre).all()
        ]
        self.country_id.choices = [(0, "— Sin país —")] + [
            (p.id, p.nombre) for p in Country.query.filter_by(activo=True).order_by(Country.nombre).all()
        ]
        self.product_id.choices = [(0, "— Sin producto —")] + [
            (p.id, p.nombre) for p in Product.query.filter_by(activo=True).order_by(Product.orden).all()
        ]
        self.responsable_id.choices = [(0, "— Sin asignar —")] + [
            (u.id, u.nombre or u.username) for u in AdminUser.query.filter_by(activo=True).all()
        ]


class PlantillaForm(FlaskForm):
    titulo = StringField("Título", validators=[DataRequired(), Length(max=200)])
    tipo = SelectField("Tipo", choices=[(k, v) for k, v in PLANTILLA_TIPOS.items()], default="otro")
    descripcion = TextAreaField("Descripción", validators=[Optional()])
    activo = SelectField("Estado", choices=[("1", "Activa"), ("0", "Inactiva")], default="1")
    archivo = FileField(
        "Archivo",
        validators=[
            Optional(),
            FileAllowed(["pdf", "doc", "docx", "xls", "xlsx"], "PDF, Word o Excel."),
        ],
    )


class PortalAccessForm(FlaskForm):
    portal_email = StringField("Email de acceso al portal", validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField("Contraseña del portal", validators=[DataRequired(), Length(min=4, max=128)])
    activo = SelectField("Portal activo", choices=[("1", "Sí"), ("0", "No")], default="1")


class PortalLoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Contraseña", validators=[DataRequired()])
