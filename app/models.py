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
    rol = db.Column(db.String(20), nullable=False, default="ceo")
    nombre = db.Column(db.String(100))
    activo = db.Column(db.Boolean, default=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def puede_editar(self):
        return self.rol != "lectura"


class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(120), nullable=False)
    categoria = db.Column(db.String(40), nullable=False, default="otro")
    descripcion = db.Column(db.Text)
    formato_venta = db.Column(db.String(40), default="cajas")
    peso_caja_kg = db.Column(db.Float)
    caja_largo_cm = db.Column(db.Float)
    caja_ancho_cm = db.Column(db.Float)
    caja_alto_cm = db.Column(db.Float)
    temperatura = db.Column(db.String(60))
    vida_util_dias = db.Column(db.Integer)
    paises_permitidos = db.Column(db.Text)
    certificaciones = db.Column(db.Text)
    imagen_filename = db.Column(db.String(255))
    ficha_stored = db.Column(db.String(255))
    ficha_original = db.Column(db.String(255))
    activo = db.Column(db.Boolean, default=True)
    orden = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    clientes = db.relationship("ClientFolder", back_populates="producto")
    abonos = db.relationship("ClientAbono", back_populates="producto")

    @property
    def tiene_ficha(self):
        return bool(self.ficha_stored)

    @property
    def tiene_imagen(self):
        return bool(self.imagen_filename)

    @property
    def paises_lista(self):
        if not self.paises_permitidos:
            return []
        return [p.strip() for p in self.paises_permitidos.split(",") if p.strip()]


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
    ciudad = db.Column(db.String(80))
    tipo_cliente = db.Column(db.String(30), default="importador")
    condiciones_comerciales = db.Column(db.Text)
    notas = db.Column(db.Text)
    estado = db.Column(db.String(30), nullable=False, default="prospecto")
    producto_id = db.Column(db.Integer, db.ForeignKey("products.id"))
    valor_estimado = db.Column(db.Float)
    moneda_estimada = db.Column(db.String(5), default="USD")
    ejecutivo_id = db.Column(db.Integer, db.ForeignKey("admin_users.id"))
    portal_activo = db.Column(db.Boolean, default=False)
    portal_email = db.Column(db.String(120))
    portal_password_hash = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by_id = db.Column(db.Integer, db.ForeignKey("admin_users.id"))

    created_by = db.relationship("AdminUser", foreign_keys=[created_by_id], backref="client_folders")
    ejecutivo = db.relationship("AdminUser", foreign_keys=[ejecutivo_id], backref="clientes_asignados")
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

    def set_portal_password(self, password):
        self.portal_password_hash = generate_password_hash(password)

    def check_portal_password(self, password):
        if not self.portal_password_hash:
            return False
        return check_password_hash(self.portal_password_hash, password)

    @property
    def total_pedidos(self):
        return sum(p.total or 0 for p in self.pedidos if p.estado != "cancelado")

    @property
    def historial_compras_count(self):
        return len([p for p in self.pedidos if p.estado != "cancelado"])


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
    estado = db.Column(db.String(30), nullable=False, default="programado")
    puerto_origen = db.Column(db.String(80))
    puerto_destino = db.Column(db.String(80))
    naviera = db.Column(db.String(120))
    numero_contenedor = db.Column(db.String(40))
    numero_bl = db.Column(db.String(60))
    numero_booking = db.Column(db.String(60))
    tipo_contenedor = db.Column(db.String(10), default="40")
    tipo_carga = db.Column(db.String(30), default="refrigerado")
    temperatura = db.Column(db.String(40))
    transporte_terrestre = db.Column(db.String(120))
    agente_aduana = db.Column(db.String(120))
    ultima_ubicacion = db.Column(db.String(200))
    tracking_notas = db.Column(db.Text)
    responsable_id = db.Column(db.Integer, db.ForeignKey("admin_users.id"))
    etd = db.Column(db.DateTime)
    eta = db.Column(db.DateTime)
    fecha_zarpe = db.Column(db.DateTime)
    notas = db.Column(db.Text)
    fecha_embarque = db.Column(db.DateTime, default=datetime.utcnow)
    created_by_id = db.Column(db.Integer, db.ForeignKey("admin_users.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    pedido = db.relationship("Order", back_populates="embarques")
    cliente = db.relationship("ClientFolder", back_populates="embarques")
    created_by = db.relationship("AdminUser", foreign_keys=[created_by_id], backref="embarques_creados")
    responsable = db.relationship("AdminUser", foreign_keys=[responsable_id], backref="embarques_responsable")
    documentos = db.relationship(
        "ExportDocument",
        back_populates="embarque",
        order_by="ExportDocument.uploaded_at.desc()",
    )
    hitos = db.relationship(
        "ShipmentMilestone",
        back_populates="embarque",
        cascade="all, delete-orphan",
        order_by="ShipmentMilestone.orden",
    )
    tareas = db.relationship(
        "InternalTask",
        back_populates="embarque",
        order_by="InternalTask.fecha_limite",
    )
    costos = db.relationship(
        "ShipmentCost",
        back_populates="embarque",
        cascade="all, delete-orphan",
        order_by="ShipmentCost.created_at",
    )

    @property
    def dias_transito(self):
        inicio = self.fecha_zarpe or self.etd
        if not inicio:
            return None
        fin = datetime.utcnow()
        return max((fin - inicio).days, 0)

    @property
    def tiene_retraso(self):
        if not self.eta:
            return False
        if self.estado in ("entregado", "cerrado", "cancelado"):
            return False
        return self.eta < datetime.utcnow()

    @property
    def etapas_completadas(self):
        return sum(1 for h in self.hitos if h.completado)

    @property
    def precio_venta(self):
        if self.pedido:
            return self.pedido.total or 0
        return 0

    @property
    def costo_total(self):
        return sum(c.monto or 0 for c in self.costos)

    @property
    def margen_bruto(self):
        return (self.precio_venta or 0) - self.costo_total

    @property
    def rentabilidad_pct(self):
        venta = self.precio_venta or 0
        if venta <= 0:
            return None
        return round((self.margen_bruto / venta) * 100, 1)


class ShipmentMilestone(db.Model):
    __tablename__ = "shipment_milestones"

    id = db.Column(db.Integer, primary_key=True)
    shipment_id = db.Column(db.Integer, db.ForeignKey("shipments.id"), nullable=False)
    etapa = db.Column(db.String(30), nullable=False)
    orden = db.Column(db.Integer, default=0)
    completado = db.Column(db.Boolean, default=False)
    fecha = db.Column(db.DateTime)
    notas = db.Column(db.Text)
    updated_by_id = db.Column(db.Integer, db.ForeignKey("admin_users.id"))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    embarque = db.relationship("Shipment", back_populates="hitos")
    updated_by = db.relationship("AdminUser", backref="hitos_actualizados")


class InternalTask(db.Model):
    __tablename__ = "internal_tasks"

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.Text)
    responsable_id = db.Column(db.Integer, db.ForeignKey("admin_users.id"))
    shipment_id = db.Column(db.Integer, db.ForeignKey("shipments.id"))
    folder_id = db.Column(db.Integer, db.ForeignKey("client_folders.id"))
    prioridad = db.Column(db.String(15), nullable=False, default="media")
    estado = db.Column(db.String(20), nullable=False, default="pendiente")
    fecha_limite = db.Column(db.DateTime)
    comentarios = db.Column(db.Text)
    created_by_id = db.Column(db.Integer, db.ForeignKey("admin_users.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    responsable = db.relationship("AdminUser", foreign_keys=[responsable_id], backref="tareas_asignadas")
    created_by = db.relationship("AdminUser", foreign_keys=[created_by_id], backref="tareas_creadas")
    embarque = db.relationship("Shipment", back_populates="tareas")
    cliente = db.relationship("ClientFolder", backref="tareas")

    @property
    def esta_vencida(self):
        if not self.fecha_limite or self.estado in ("completada", "cancelada"):
            return False
        return self.fecha_limite < datetime.utcnow()


class Country(db.Model):
    __tablename__ = "countries"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80), nullable=False, unique=True)
    codigo = db.Column(db.String(5), nullable=False, unique=True)
    notas = db.Column(db.Text)
    activo = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    requisitos = db.relationship(
        "CountryRequirement",
        back_populates="pais",
        cascade="all, delete-orphan",
        order_by="CountryRequirement.orden",
    )
    documentos = db.relationship("ExportDocument", back_populates="pais")

    @property
    def requisitos_obligatorios(self):
        return [r for r in self.requisitos if r.obligatorio]


class CountryRequirement(db.Model):
    __tablename__ = "country_requirements"

    id = db.Column(db.Integer, primary_key=True)
    country_id = db.Column(db.Integer, db.ForeignKey("countries.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"))
    tipo = db.Column(db.String(30), nullable=False, default="documento")
    titulo = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.Text)
    obligatorio = db.Column(db.Boolean, default=True)
    orden = db.Column(db.Integer, default=0)

    pais = db.relationship("Country", back_populates="requisitos")
    producto = db.relationship("Product", backref="requisitos_pais")


class ExportDocument(db.Model):
    __tablename__ = "export_documents"

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    tipo = db.Column(db.String(30), nullable=False, default="otro")
    estado = db.Column(db.String(20), nullable=False, default="pendiente")
    folder_id = db.Column(db.Integer, db.ForeignKey("client_folders.id"))
    shipment_id = db.Column(db.Integer, db.ForeignKey("shipments.id"))
    country_id = db.Column(db.Integer, db.ForeignKey("countries.id"))
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"))
    original_filename = db.Column(db.String(255))
    stored_filename = db.Column(db.String(255))
    content_type = db.Column(db.String(120))
    size_bytes = db.Column(db.Integer, default=0)
    fecha_vencimiento = db.Column(db.DateTime)
    comentarios = db.Column(db.Text)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    uploaded_by_id = db.Column(db.Integer, db.ForeignKey("admin_users.id"))

    cliente = db.relationship("ClientFolder", backref="documentos_export")
    embarque = db.relationship("Shipment", back_populates="documentos")
    pais = db.relationship("Country", back_populates="documentos")
    producto = db.relationship("Product", backref="documentos")
    uploaded_by = db.relationship("AdminUser", backref="documentos_subidos")

    @property
    def tiene_archivo(self):
        return bool(self.stored_filename)

    @property
    def esta_vencido(self):
        if not self.fecha_vencimiento:
            return False
        return self.fecha_vencimiento < datetime.utcnow()

    @property
    def dias_para_vencer(self):
        if not self.fecha_vencimiento:
            return None
        return (self.fecha_vencimiento - datetime.utcnow()).days


class ShipmentCost(db.Model):
    __tablename__ = "shipment_costs"

    id = db.Column(db.Integer, primary_key=True)
    shipment_id = db.Column(db.Integer, db.ForeignKey("shipments.id"), nullable=False)
    tipo = db.Column(db.String(30), nullable=False, default="otro")
    concepto = db.Column(db.String(200), nullable=False)
    monto = db.Column(db.Float, nullable=False, default=0)
    moneda = db.Column(db.String(5), nullable=False, default="USD")
    notas = db.Column(db.Text)
    created_by_id = db.Column(db.Integer, db.ForeignKey("admin_users.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    embarque = db.relationship("Shipment", back_populates="costos")
    created_by = db.relationship("AdminUser", backref="costos_registrados")


class Contract(db.Model):
    __tablename__ = "contracts"

    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(30), unique=True, nullable=False)
    titulo = db.Column(db.String(200), nullable=False)
    folder_id = db.Column(db.Integer, db.ForeignKey("client_folders.id"))
    country_id = db.Column(db.Integer, db.ForeignKey("countries.id"))
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"))
    responsable_id = db.Column(db.Integer, db.ForeignKey("admin_users.id"))
    estado = db.Column(db.String(20), nullable=False, default="borrador")
    fecha_inicio = db.Column(db.DateTime)
    fecha_fin = db.Column(db.DateTime)
    renovacion_auto = db.Column(db.Boolean, default=False)
    condiciones = db.Column(db.Text)
    notas = db.Column(db.Text)
    original_filename = db.Column(db.String(255))
    stored_filename = db.Column(db.String(255))
    content_type = db.Column(db.String(120))
    size_bytes = db.Column(db.Integer, default=0)
    created_by_id = db.Column(db.Integer, db.ForeignKey("admin_users.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    cliente = db.relationship("ClientFolder", backref="contratos")
    pais = db.relationship("Country", backref="contratos")
    producto = db.relationship("Product", backref="contratos")
    responsable = db.relationship("AdminUser", foreign_keys=[responsable_id], backref="contratos_responsable")
    created_by = db.relationship("AdminUser", foreign_keys=[created_by_id], backref="contratos_creados")

    @property
    def tiene_archivo(self):
        return bool(self.stored_filename)

    @property
    def dias_para_vencer(self):
        if not self.fecha_fin:
            return None
        return (self.fecha_fin - datetime.utcnow()).days

    @property
    def esta_vencido(self):
        if not self.fecha_fin or self.estado in ("cancelado", "renovado"):
            return False
        return self.fecha_fin < datetime.utcnow()


class DocumentTemplate(db.Model):
    __tablename__ = "document_templates"

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    tipo = db.Column(db.String(30), nullable=False, default="otro")
    descripcion = db.Column(db.Text)
    activo = db.Column(db.Boolean, default=True)
    original_filename = db.Column(db.String(255))
    stored_filename = db.Column(db.String(255))
    content_type = db.Column(db.String(120))
    size_bytes = db.Column(db.Integer, default=0)
    uploaded_by_id = db.Column(db.Integer, db.ForeignKey("admin_users.id"))
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    uploaded_by = db.relationship("AdminUser", backref="plantillas_subidas")

    @property
    def tiene_archivo(self):
        return bool(self.stored_filename)


class ActivityLog(db.Model):
    __tablename__ = "activity_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("admin_users.id"))
    accion = db.Column(db.String(30), nullable=False)
    entidad_tipo = db.Column(db.String(30), nullable=False)
    entidad_id = db.Column(db.Integer)
    entidad_ref = db.Column(db.String(120))
    detalle = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    usuario = db.relationship("AdminUser", backref="actividad")


class NotificationLog(db.Model):
    __tablename__ = "notification_logs"

    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(30), nullable=False, default="alerta")
    titulo = db.Column(db.String(200), nullable=False)
    mensaje = db.Column(db.Text)
    destinatario = db.Column(db.String(120), nullable=False)
    canal = db.Column(db.String(20), nullable=False, default="email")
    estado = db.Column(db.String(20), nullable=False, default="pendiente")
    error_detalle = db.Column(db.Text)
    folder_id = db.Column(db.Integer, db.ForeignKey("client_folders.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    cliente = db.relationship("ClientFolder", backref="notificaciones")
