from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from . import db


class ContactMessage(db.Model):
    __tablename__ = "mensajes"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    telefono = db.Column(db.String(20))
    empresa = db.Column(db.String(120))
    mensaje = db.Column(db.Text, nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    leido = db.Column(db.Boolean, default=False)  # 👈 nuevo campo



class AdminUser(UserMixin, db.Model):
    __tablename__ = "admin_users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(120), nullable=False)
    categoria = db.Column(db.String(40), nullable=False, default="otro")
    descripcion = db.Column(db.Text)
    activo = db.Column(db.Boolean, default=True)
    orden = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    clientes = db.relationship("ClientFolder", back_populates="producto")
    abonos = db.relationship("ClientAbono", back_populates="producto")


class ClientFolder(db.Model):
    __tablename__ = "client_folders"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(120), nullable=False)
    slug = db.Column(db.String(140), unique=True, nullable=False)
    empresa = db.Column(db.String(120))
    contacto = db.Column(db.String(100))
    email = db.Column(db.String(120))
    telefono = db.Column(db.String(30))
    pais = db.Column(db.String(80))
    notas = db.Column(db.Text)
    estado = db.Column(db.String(30), nullable=False, default="prospecto")
    producto_id = db.Column(db.Integer, db.ForeignKey("products.id"))
    valor_estimado = db.Column(db.Float)
    moneda_estimada = db.Column(db.String(5), default="USD")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by_id = db.Column(db.Integer, db.ForeignKey("admin_users.id"))

    created_by = db.relationship("AdminUser", backref="client_folders")
    producto = db.relationship("Product", back_populates="clientes")
    files = db.relationship(
        "ClientFile",
        back_populates="folder",
        cascade="all, delete-orphan",
        order_by="ClientFile.uploaded_at.desc()",
    )
    abonos = db.relationship(
        "ClientAbono",
        back_populates="folder",
        cascade="all, delete-orphan",
        order_by="ClientAbono.fecha.desc()",
    )
    cotizaciones = db.relationship(
        "Quotation",
        back_populates="cliente",
        order_by="Quotation.created_at.desc()",
    )
    pedidos = db.relationship(
        "Order",
        back_populates="cliente",
        order_by="Order.created_at.desc()",
    )
    embarques = db.relationship(
        "Shipment",
        back_populates="cliente",
        order_by="Shipment.created_at.desc()",
    )

    @property
    def file_count(self):
        return len(self.files)

    @property
    def total_abonos(self):
        return sum(a.monto for a in self.abonos)

    @property
    def tiene_abono(self):
        return len(self.abonos) > 0


class ClientFile(db.Model):
    __tablename__ = "client_files"

    id = db.Column(db.Integer, primary_key=True)
    folder_id = db.Column(db.Integer, db.ForeignKey("client_folders.id"), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    stored_filename = db.Column(db.String(255), nullable=False)
    content_type = db.Column(db.String(120))
    size_bytes = db.Column(db.Integer, default=0)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    uploaded_by_id = db.Column(db.Integer, db.ForeignKey("admin_users.id"))

    folder = db.relationship("ClientFolder", back_populates="files")
    uploaded_by = db.relationship("AdminUser", backref="uploaded_files")


class ClientAbono(db.Model):
    __tablename__ = "client_abonos"

    id = db.Column(db.Integer, primary_key=True)
    folder_id = db.Column(db.Integer, db.ForeignKey("client_folders.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"))
    monto = db.Column(db.Float, nullable=False, default=0)
    moneda = db.Column(db.String(5), nullable=False, default="USD")
    tipo = db.Column(db.String(30), nullable=False, default="abono")
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    referencia = db.Column(db.String(120))
    notas = db.Column(db.Text)
    created_by_id = db.Column(db.Integer, db.ForeignKey("admin_users.id"))

    folder = db.relationship("ClientFolder", back_populates="abonos")
    producto = db.relationship("Product", back_populates="abonos")
    created_by = db.relationship("AdminUser", backref="abonos_registrados")


class Quotation(db.Model):
    __tablename__ = "quotations"

    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(30), unique=True, nullable=False)
    folder_id = db.Column(db.Integer, db.ForeignKey("client_folders.id"))
    mensaje_id = db.Column(db.Integer, db.ForeignKey("mensajes.id"))
    cliente_nombre = db.Column(db.String(120), nullable=False)
    cliente_empresa = db.Column(db.String(120))
    cliente_email = db.Column(db.String(120))
    cliente_telefono = db.Column(db.String(30))
    cliente_pais = db.Column(db.String(80))
    estado = db.Column(db.String(20), nullable=False, default="borrador")
    moneda = db.Column(db.String(5), nullable=False, default="USD")
    incoterm = db.Column(db.String(20), default="FOB")
    validez_dias = db.Column(db.Integer, default=15)
    condiciones = db.Column(db.Text)
    notas = db.Column(db.Text)
    descuento_pct = db.Column(db.Float, default=0)
    subtotal = db.Column(db.Float, default=0)
    total = db.Column(db.Float, default=0)
    fecha_emision = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_vencimiento = db.Column(db.DateTime)
    created_by_id = db.Column(db.Integer, db.ForeignKey("admin_users.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    cliente = db.relationship("ClientFolder", back_populates="cotizaciones")
    mensaje = db.relationship("ContactMessage", backref="cotizaciones")
    created_by = db.relationship("AdminUser", backref="cotizaciones_creadas")
    lineas = db.relationship(
        "QuotationLine",
        back_populates="cotizacion",
        cascade="all, delete-orphan",
        order_by="QuotationLine.orden",
    )
    pedidos = db.relationship(
        "Order",
        back_populates="cotizacion",
        order_by="Order.created_at.desc()",
    )

    def recalcular_totales(self):
        self.subtotal = sum(l.subtotal for l in self.lineas)
        desc = self.subtotal * (self.descuento_pct or 0) / 100
        self.total = self.subtotal - desc


class QuotationLine(db.Model):
    __tablename__ = "quotation_lines"

    id = db.Column(db.Integer, primary_key=True)
    quotation_id = db.Column(db.Integer, db.ForeignKey("quotations.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"))
    descripcion = db.Column(db.String(255), nullable=False)
    cantidad = db.Column(db.Float, nullable=False, default=1)
    unidad = db.Column(db.String(20), default="kg")
    precio_unitario = db.Column(db.Float, nullable=False, default=0)
    orden = db.Column(db.Integer, default=0)

    cotizacion = db.relationship("Quotation", back_populates="lineas")
    producto = db.relationship("Product")

    @property
    def subtotal(self):
        return (self.cantidad or 0) * (self.precio_unitario or 0)


class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(30), unique=True, nullable=False)
    quotation_id = db.Column(db.Integer, db.ForeignKey("quotations.id"))
    folder_id = db.Column(db.Integer, db.ForeignKey("client_folders.id"))
    cliente_nombre = db.Column(db.String(120), nullable=False)
    cliente_empresa = db.Column(db.String(120))
    cliente_email = db.Column(db.String(120))
    cliente_telefono = db.Column(db.String(30))
    cliente_pais = db.Column(db.String(80))
    estado = db.Column(db.String(25), nullable=False, default="confirmado")
    moneda = db.Column(db.String(5), nullable=False, default="USD")
    incoterm = db.Column(db.String(20), default="FOB")
    descuento_pct = db.Column(db.Float, default=0)
    anticipo_monto = db.Column(db.Float, default=0)
    subtotal = db.Column(db.Float, default=0)
    total = db.Column(db.Float, default=0)
    condiciones = db.Column(db.Text)
    notas = db.Column(db.Text)
    fecha_pedido = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_entrega_estimada = db.Column(db.DateTime)
    created_by_id = db.Column(db.Integer, db.ForeignKey("admin_users.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    cotizacion = db.relationship("Quotation", back_populates="pedidos")
    cliente = db.relationship("ClientFolder", back_populates="pedidos")
    created_by = db.relationship("AdminUser", backref="pedidos_creados")
    lineas = db.relationship(
        "OrderLine",
        back_populates="pedido",
        cascade="all, delete-orphan",
        order_by="OrderLine.orden",
    )
    embarques = db.relationship(
        "Shipment",
        back_populates="pedido",
        order_by="Shipment.created_at.desc()",
    )

    def recalcular_totales(self):
        self.subtotal = sum(l.subtotal for l in self.lineas)
        desc = self.subtotal * (self.descuento_pct or 0) / 100
        self.total = self.subtotal - desc

    @property
    def saldo_pendiente(self):
        return max((self.total or 0) - (self.anticipo_monto or 0), 0)


class OrderLine(db.Model):
    __tablename__ = "order_lines"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"))
    descripcion = db.Column(db.String(255), nullable=False)
    cantidad = db.Column(db.Float, nullable=False, default=1)
    unidad = db.Column(db.String(20), default="kg")
    precio_unitario = db.Column(db.Float, nullable=False, default=0)
    orden = db.Column(db.Integer, default=0)

    pedido = db.relationship("Order", back_populates="lineas")
    producto = db.relationship("Product")

    @property
    def subtotal(self):
        return (self.cantidad or 0) * (self.precio_unitario or 0)


class Shipment(db.Model):
    __tablename__ = "shipments"

    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(30), unique=True, nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)
    folder_id = db.Column(db.Integer, db.ForeignKey("client_folders.id"))
    cliente_nombre = db.Column(db.String(120), nullable=False)
    cliente_empresa = db.Column(db.String(120))
    estado = db.Column(db.String(25), nullable=False, default="programado")
    puerto_origen = db.Column(db.String(80))
    puerto_destino = db.Column(db.String(80))
    naviera = db.Column(db.String(120))
    numero_contenedor = db.Column(db.String(40))
    numero_bl = db.Column(db.String(60))
    tipo_carga = db.Column(db.String(30), default="refrigerado")
    temperatura = db.Column(db.String(40))
    etd = db.Column(db.DateTime)
    eta = db.Column(db.DateTime)
    notas = db.Column(db.Text)
    fecha_embarque = db.Column(db.DateTime, default=datetime.utcnow)
    created_by_id = db.Column(db.Integer, db.ForeignKey("admin_users.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    pedido = db.relationship("Order", back_populates="embarques")
    cliente = db.relationship("ClientFolder", back_populates="embarques")
    created_by = db.relationship("AdminUser", backref="embarques_creados")
