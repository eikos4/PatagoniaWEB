from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, TextAreaField, SelectField, FloatField, DateField, IntegerField
from wtforms.validators import DataRequired, Email, Optional, Length, NumberRange

from app.constants import (
    CLIENTE_ESTADOS, PRODUCTO_CATEGORIAS, ABONO_TIPOS, MONEDAS,
    COTIZACION_ESTADOS, UNIDADES_LINEA, PEDIDO_ESTADOS,
    EMBARQUE_ESTADOS, CARGA_TIPOS, PUERTOS_ORIGEN, PUERTOS_DESTINO,
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
    estado = SelectField("Clasificación", choices=[(k, v) for k, v in CLIENTE_ESTADOS.items()], default="prospecto")
    producto_id = SelectField("Producto de interés", coerce=int, validators=[Optional()])
    valor_estimado = FloatField("Valor estimado", validators=[Optional(), NumberRange(min=0)])
    moneda_estimada = SelectField("Moneda", choices=[(m, m) for m in MONEDAS], default="USD")
    notas = TextAreaField("Notas / información adicional", validators=[Optional()])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from app.models import Product
        self.producto_id.choices = [(0, "— Sin asignar —")] + [
            (p.id, p.nombre) for p in Product.query.filter_by(activo=True).order_by(Product.orden).all()
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
    nombre = StringField("Nombre del producto", validators=[DataRequired(), Length(max=120)])
    categoria = SelectField("Categoría", choices=[(k, v) for k, v in PRODUCTO_CATEGORIAS.items()], default="otro")
    descripcion = TextAreaField("Descripción", validators=[Optional()])
    orden = IntegerField("Orden", validators=[Optional(), NumberRange(min=0)], default=0)


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
    puerto_origen = SelectField("Puerto origen (Chile)", choices=[(p, p) for p in PUERTOS_ORIGEN], default="San Antonio")
    puerto_destino = SelectField("Puerto destino (México)", choices=[(p, p) for p in PUERTOS_DESTINO], default="Manzanillo")
    naviera = StringField("Naviera / línea", validators=[Optional(), Length(max=120)])
    numero_contenedor = StringField("Nº contenedor", validators=[Optional(), Length(max=40)])
    numero_bl = StringField("Nº BL (Bill of Lading)", validators=[Optional(), Length(max=60)])
    tipo_carga = SelectField("Tipo de carga", choices=[(k, v) for k, v in CARGA_TIPOS.items()], default="refrigerado")
    temperatura = StringField("Temperatura", validators=[Optional(), Length(max=40)], default="-1°C a +4°C")
    etd = DateField("ETD (salida estimada)", validators=[Optional()], format="%Y-%m-%d")
    eta = DateField("ETA (llegada estimada)", validators=[Optional()], format="%Y-%m-%d")
    notas = TextAreaField("Notas logísticas", validators=[Optional()])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from app.models import Order
        pedidos = Order.query.filter(Order.estado.notin_(["cancelado", "entregado"])).order_by(Order.created_at.desc()).all()
        self.order_id.choices = [(p.id, f"{p.numero} — {p.cliente_nombre}") for p in pedidos] or [(0, "— Sin pedidos disponibles —")]
