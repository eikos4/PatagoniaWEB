import os
from datetime import datetime

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    send_from_directory,
    send_file,
)
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename

from app.models import AdminUser, ContactMessage, ClientFolder, ClientFile, Product, ClientAbono, Quotation, Order, Shipment, Country, CountryRequirement, ExportDocument, ShipmentMilestone, InternalTask, ShipmentCost, Contract, DocumentTemplate, ActivityLog, NotificationLog
from app import db, login_manager
from app.forms import LoginForm, ClientFolderForm, ClientFileUploadForm, ClientAbonoForm, ProductForm, CotizacionForm, PedidoForm, EmbarqueForm, CountryForm, CountryRequirementForm, DocumentoForm, PaisDocumentoUploadForm, TrackingUpdateForm, TareaForm, UsuarioForm, ContainerCalcForm, CostoForm, ContratoForm, PlantillaForm, PortalAccessForm
from app.upload_utils import (
    slugify,
    unique_slug,
    allowed_file,
    save_client_file,
    delete_stored_file,
    delete_folder_directory,
    folder_disk_path,
    format_file_size,
)
from app.document_utils import save_export_document, delete_export_document, document_file_path
from app.admin_stats import get_dashboard_kpis
from app.constants import (
    CLIENTE_ESTADOS, CLIENTE_ESTADO_COLORS, CLIENTE_ESTADO_ICONS,
    PRODUCTO_CATEGORIAS, ABONO_TIPOS,
    COTIZACION_ESTADOS, COTIZACION_ESTADO_COLORS, COTIZACION_ESTADO_ICONS,
    PEDIDO_ESTADOS, PEDIDO_ESTADO_COLORS, PEDIDO_ESTADO_ICONS,
    EMBARQUE_ESTADOS, EMBARQUE_ESTADO_COLORS, EMBARQUE_ESTADO_ICONS, CARGA_TIPOS,
    DOCUMENTO_TIPOS, DOCUMENTO_ESTADOS, DOCUMENTO_ESTADO_COLORS, DOCUMENTO_ESTADO_ICONS,
    REQUISITO_TIPOS, REQUISITO_A_DOCUMENTO_TIPO,
    LOGISTICA_ETAPAS, LOGISTICA_ETAPA_ICONS, USER_ROLES,
    TAREA_PRIORIDADES, TAREA_PRIORIDAD_COLORS, TAREA_ESTADOS, TAREA_ESTADO_COLORS,
    CONTENEDOR_TIPOS, COSTO_TIPOS, COSTO_TIPO_ICONS,
    CONTRATO_ESTADOS, CONTRATO_ESTADO_COLORS, PLANTILLA_TIPOS,
    AUDIT_ENTIDADES, AUDIT_ACCIONES, CLIENTE_TIPOS, PRODUCTO_FORMATOS,
)
from app.alertas import get_alertas
from app.permissions import role_required, edit_required
from app.container_utils import calcular_contenedor
from app.reports_stats import get_reportes_data
from app.audit import log_activity
from app.contract_utils import next_contrato_numero, save_contract_file, delete_contract_file, contract_file_path, sync_contrato_estado
from app.template_utils import save_template_file, delete_template_file, template_file_path
from app.product_utils import save_product_file, delete_product_file, product_file_path
from app.notifications import send_email, enviar_resumen_alertas
from app.cotizacion_utils import (
    next_cotizacion_numero, parse_lineas_from_form, apply_lineas, calc_fecha_vencimiento,
)
from app.pedido_utils import next_pedido_numero, apply_lineas as apply_pedido_lineas, pedido_from_cotizacion
from app.embarque_utils import next_embarque_numero, embarque_from_pedido, sync_pedido_estado, init_shipment_milestones, embarques_activos_filter
from app.pdf_cotizacion import generar_pdf_cotizacion
from app.seed import seed_default_products, seed_default_countries

admin = Blueprint("admin", __name__, template_folder="templates")


@login_manager.user_loader
def load_user(user_id):
    return AdminUser.query.get(int(user_id))


@admin.context_processor
def inject_admin_sidebar():
    if current_user.is_authenticated:
        return {
            "pendientes_count": ContactMessage.query.filter_by(leido=False).count(),
            "carteras_count": ClientFolder.query.count(),
            "cotizaciones_count": Quotation.query.count(),
            "pedidos_count": Order.query.filter(Order.estado.notin_(["entregado", "cancelado"])).count(),
            "embarques_count": Shipment.query.filter(embarques_activos_filter()).count(),
            "documentos_count": ExportDocument.query.filter_by(estado="pendiente").count(),
            "alertas_count": len(get_alertas()),
            "tareas_count": InternalTask.query.filter(
                InternalTask.estado.in_(["pendiente", "en_proceso"])
            ).count(),
            "puede_editar": current_user.puede_editar,
            "user_rol": current_user.rol,
            "user_roles": USER_ROLES,
            "cliente_estados": CLIENTE_ESTADOS,
            "estado_colors": CLIENTE_ESTADO_COLORS,
            "cliente_estado_icons": CLIENTE_ESTADO_ICONS,
            "producto_categorias": PRODUCTO_CATEGORIAS,
            "abono_tipos": ABONO_TIPOS,
            "cotizacion_estados": COTIZACION_ESTADOS,
            "cotizacion_estado_colors": COTIZACION_ESTADO_COLORS,
            "cotizacion_estado_icons": COTIZACION_ESTADO_ICONS,
            "pedido_estados": PEDIDO_ESTADOS,
            "pedido_estado_colors": PEDIDO_ESTADO_COLORS,
            "pedido_estado_icons": PEDIDO_ESTADO_ICONS,
            "embarque_estados": EMBARQUE_ESTADOS,
            "embarque_estado_colors": EMBARQUE_ESTADO_COLORS,
            "embarque_estado_icons": EMBARQUE_ESTADO_ICONS,
            "carga_tipos": CARGA_TIPOS,
            "documento_tipos": DOCUMENTO_TIPOS,
            "documento_estados": DOCUMENTO_ESTADOS,
            "documento_estado_colors": DOCUMENTO_ESTADO_COLORS,
            "documento_estado_icons": DOCUMENTO_ESTADO_ICONS,
            "requisito_tipos": REQUISITO_TIPOS,
            "requisito_a_documento_tipo": REQUISITO_A_DOCUMENTO_TIPO,
            "logistica_etapas": LOGISTICA_ETAPAS,
            "logistica_etapa_icons": LOGISTICA_ETAPA_ICONS,
            "tarea_prioridades": TAREA_PRIORIDADES,
            "tarea_prioridad_colors": TAREA_PRIORIDAD_COLORS,
            "tarea_estados": TAREA_ESTADOS,
            "tarea_estado_colors": TAREA_ESTADO_COLORS,
            "contenedor_tipos": CONTENEDOR_TIPOS,
            "costo_tipos": COSTO_TIPOS,
            "costo_tipo_icons": COSTO_TIPO_ICONS,
            "contrato_estados": CONTRATO_ESTADOS,
            "contrato_estado_colors": CONTRATO_ESTADO_COLORS,
            "plantilla_tipos": PLANTILLA_TIPOS,
            "audit_entidades": AUDIT_ENTIDADES,
            "audit_acciones": AUDIT_ACCIONES,
            "contratos_count": Contract.query.filter(
                Contract.estado.in_(["vigente", "por_vencer"])
            ).count(),
            "cliente_tipos": CLIENTE_TIPOS,
            "producto_formatos": PRODUCTO_FORMATOS,
        }
    return {}


def _save_cliente_from_form(carpeta, form):
    carpeta.nombre = form.nombre.data.strip()
    carpeta.empresa = form.empresa.data.strip() if form.empresa.data else None
    carpeta.contacto = form.contacto.data.strip() if form.contacto.data else None
    carpeta.email = form.email.data.strip() if form.email.data else None
    carpeta.telefono = form.telefono.data.strip() if form.telefono.data else None
    carpeta.pais = form.pais.data.strip() if form.pais.data else None
    carpeta.ciudad = form.ciudad.data.strip() if form.ciudad.data else None
    carpeta.tipo_cliente = form.tipo_cliente.data
    carpeta.estado = form.estado.data
    carpeta.producto_id = form.producto_id.data or None
    carpeta.ejecutivo_id = form.ejecutivo_id.data or None
    carpeta.valor_estimado = form.valor_estimado.data
    carpeta.moneda_estimada = form.moneda_estimada.data
    carpeta.condiciones_comerciales = form.condiciones_comerciales.data.strip() if form.condiciones_comerciales.data else None
    carpeta.notas = form.notas.data.strip() if form.notas.data else None


def _fill_product_from_form(producto, form):
    producto.nombre = form.nombre.data.strip()
    producto.categoria = form.categoria.data
    producto.formato_venta = form.formato_venta.data
    producto.descripcion = form.descripcion.data.strip() if form.descripcion.data else None
    producto.peso_caja_kg = form.peso_caja_kg.data
    producto.caja_largo_cm = form.caja_largo_cm.data
    producto.caja_ancho_cm = form.caja_ancho_cm.data
    producto.caja_alto_cm = form.caja_alto_cm.data
    producto.temperatura = form.temperatura.data.strip() if form.temperatura.data else None
    producto.vida_util_dias = form.vida_util_dias.data
    producto.paises_permitidos = form.paises_permitidos.data.strip() if form.paises_permitidos.data else None
    producto.certificaciones = form.certificaciones.data.strip() if form.certificaciones.data else None
    producto.orden = form.orden.data or 0
    if form.imagen.data:
        delete_product_file(producto.imagen_filename)
        _, stored = save_product_file(form.imagen.data, "img")
        producto.imagen_filename = stored
    if form.ficha.data:
        delete_product_file(producto.ficha_stored)
        orig, stored = save_product_file(form.ficha.data, "ficha")
        producto.ficha_stored = stored
        producto.ficha_original = orig


def _fill_cotizacion_from_form(cot, form):
    cot.cliente_nombre = form.cliente_nombre.data.strip()
    cot.cliente_empresa = form.cliente_empresa.data.strip() if form.cliente_empresa.data else None
    cot.cliente_email = form.cliente_email.data.strip() if form.cliente_email.data else None
    cot.cliente_telefono = form.cliente_telefono.data.strip() if form.cliente_telefono.data else None
    cot.cliente_pais = form.cliente_pais.data.strip() if form.cliente_pais.data else None
    cot.folder_id = form.folder_id.data if form.folder_id.data else None
    cot.estado = form.estado.data
    cot.moneda = form.moneda.data
    cot.incoterm = form.incoterm.data
    cot.validez_dias = form.validez_dias.data or 15
    cot.descuento_pct = form.descuento_pct.data or 0
    cot.condiciones = form.condiciones.data.strip() if form.condiciones.data else None
    cot.notas = form.notas.data.strip() if form.notas.data else None
    cot.fecha_vencimiento = calc_fecha_vencimiento(cot.fecha_emision, cot.validez_dias)


def _fill_pedido_from_form(ped, form):
    ped.cliente_nombre = form.cliente_nombre.data.strip()
    ped.cliente_empresa = form.cliente_empresa.data.strip() if form.cliente_empresa.data else None
    ped.cliente_email = form.cliente_email.data.strip() if form.cliente_email.data else None
    ped.cliente_telefono = form.cliente_telefono.data.strip() if form.cliente_telefono.data else None
    ped.cliente_pais = form.cliente_pais.data.strip() if form.cliente_pais.data else None
    ped.folder_id = form.folder_id.data if form.folder_id.data else None
    ped.estado = form.estado.data
    ped.moneda = form.moneda.data
    ped.incoterm = form.incoterm.data
    ped.descuento_pct = form.descuento_pct.data or 0
    ped.anticipo_monto = form.anticipo_monto.data or 0
    ped.condiciones = form.condiciones.data.strip() if form.condiciones.data else None
    ped.notas = form.notas.data.strip() if form.notas.data else None
    if form.fecha_entrega_estimada.data:
        ped.fecha_entrega_estimada = datetime.combine(
            form.fecha_entrega_estimada.data, datetime.min.time()
        )
    else:
        ped.fecha_entrega_estimada = None


def _fill_embarque_from_form(emb, form):
    ped = Order.query.get(form.order_id.data)
    if not ped:
        return False
    emb.order_id = ped.id
    emb.folder_id = ped.folder_id
    emb.cliente_nombre = ped.cliente_nombre
    emb.cliente_empresa = ped.cliente_empresa
    emb.estado = form.estado.data
    emb.responsable_id = form.responsable_id.data or None
    emb.puerto_origen = form.puerto_origen.data
    emb.puerto_destino = form.puerto_destino.data
    emb.naviera = form.naviera.data.strip() if form.naviera.data else None
    emb.numero_contenedor = form.numero_contenedor.data.strip() if form.numero_contenedor.data else None
    emb.numero_bl = form.numero_bl.data.strip() if form.numero_bl.data else None
    emb.numero_booking = form.numero_booking.data.strip() if form.numero_booking.data else None
    emb.tipo_contenedor = form.tipo_contenedor.data
    emb.tipo_carga = form.tipo_carga.data
    emb.temperatura = form.temperatura.data.strip() if form.temperatura.data else None
    emb.transporte_terrestre = form.transporte_terrestre.data.strip() if form.transporte_terrestre.data else None
    emb.agente_aduana = form.agente_aduana.data.strip() if form.agente_aduana.data else None
    emb.ultima_ubicacion = form.ultima_ubicacion.data.strip() if form.ultima_ubicacion.data else None
    emb.tracking_notas = form.tracking_notas.data.strip() if form.tracking_notas.data else None
    emb.notas = form.notas.data.strip() if form.notas.data else None
    emb.etd = datetime.combine(form.etd.data, datetime.min.time()) if form.etd.data else None
    emb.eta = datetime.combine(form.eta.data, datetime.min.time()) if form.eta.data else None
    emb.fecha_zarpe = datetime.combine(form.fecha_zarpe.data, datetime.min.time()) if form.fecha_zarpe.data else None
    sync_pedido_estado(ped, emb.estado)
    return True


@admin.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = AdminUser.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            if not user.activo:
                flash("Tu cuenta está desactivada. Contacta al administrador.", "danger")
            else:
                login_user(user)
                flash("Bienvenido al panel de Patagonia Sur", "success")
                return redirect(url_for("admin.dashboard"))
        flash("Usuario o contraseña incorrectos", "danger")
    return render_template("login.html", form=form)


# ── Resumen KPIs ──────────────────────────────────────────────────

@admin.route("/dashboard")
@login_required
def dashboard():
    seed_default_products()
    seed_default_countries()
    kpis = get_dashboard_kpis()
    return render_template("admin_dashboard.html", kpis=kpis, active_nav="resumen")


# ── Mensajes ──────────────────────────────────────────────────────

@admin.route("/mensajes")
@login_required
def mensajes():
    msgs = ContactMessage.query.order_by(ContactMessage.fecha.desc()).all()
    return render_template("admin_mensajes.html", mensajes=msgs, active_nav="mensajes")


@admin.route("/mensaje/<int:id>/toggle", methods=["POST"])
@login_required
def toggle_mensaje(id):
    mensaje = ContactMessage.query.get_or_404(id)
    mensaje.leido = not mensaje.leido
    db.session.commit()
    flash("Estado de mensaje actualizado", "success")
    return redirect(url_for("admin.mensajes"))


@admin.route("/mensaje/<int:id>/delete", methods=["POST"])
@login_required
def delete_mensaje(id):
    mensaje = ContactMessage.query.get_or_404(id)
    db.session.delete(mensaje)
    db.session.commit()
    flash("Mensaje eliminado", "info")
    return redirect(url_for("admin.mensajes"))


# ── Clientes ──────────────────────────────────────────────────────

@admin.route("/clientes")
@login_required
def clientes():
    seed_default_products()
    q = ClientFolder.query
    estado = request.args.get("estado", "")
    producto = request.args.get("producto", "")
    con_abono = request.args.get("con_abono", "")

    if estado and estado in CLIENTE_ESTADOS:
        q = q.filter_by(estado=estado)
    if producto:
        q = q.filter_by(producto_id=int(producto))
    if con_abono == "1":
        q = q.filter(ClientFolder.id.in_(
            db.session.query(ClientAbono.folder_id).distinct()
        ))

    carpetas = q.order_by(ClientFolder.updated_at.desc()).all()
    productos = Product.query.filter_by(activo=True).order_by(Product.orden).all()
    return render_template(
        "admin_clientes.html",
        carpetas=carpetas,
        productos=productos,
        filtro_estado=estado,
        filtro_producto=producto,
        filtro_abono=con_abono,
        active_nav="clientes",
    )


@admin.route("/carteras")
@login_required
def carteras():
    return redirect(url_for("admin.clientes"))


@admin.route("/clientes/nuevo", methods=["GET", "POST"])
@admin.route("/carteras/nueva", methods=["GET", "POST"])
@login_required
def cartera_nueva():
    seed_default_products()
    form = ClientFolderForm()
    if form.validate_on_submit():
        base_slug = slugify(form.nombre.data)
        existing = {c.slug for c in ClientFolder.query.with_entities(ClientFolder.slug).all()}
        slug = unique_slug(base_slug, existing)
        carpeta = ClientFolder(slug=slug, created_by_id=current_user.id)
        _save_cliente_from_form(carpeta, form)
        db.session.add(carpeta)
        db.session.commit()
        os.makedirs(folder_disk_path(slug), exist_ok=True)
        flash("Cliente registrado correctamente", "success")
        return redirect(url_for("admin.cartera_detalle", id=carpeta.id))
    return render_template("admin_cartera_form.html", form=form, active_nav="clientes", editing=False)


@admin.route("/clientes/<int:id>")
@admin.route("/carteras/<int:id>")
@login_required
def cartera_detalle(id):
    carpeta = ClientFolder.query.get_or_404(id)
    abono_form = ClientAbonoForm()
    if not abono_form.fecha.data:
        abono_form.fecha.data = datetime.utcnow().date()
    portal_form = PortalAccessForm()
    portal_form.portal_email.data = carpeta.portal_email or carpeta.email or ""
    portal_form.activo.data = "1" if carpeta.portal_activo else "0"
    pedidos_hist = [p for p in carpeta.pedidos if p.estado != "cancelado"]
    contratos_vigentes = [c for c in carpeta.contratos if c.estado in ("vigente", "por_vencer")]
    return render_template(
        "admin_cartera_detalle.html",
        carpeta=carpeta,
        abono_form=abono_form,
        portal_form=portal_form,
        pedidos_hist=pedidos_hist,
        contratos_vigentes=contratos_vigentes,
        active_nav="clientes",
    )


@admin.route("/clientes/<int:id>/editar", methods=["GET", "POST"])
@admin.route("/carteras/<int:id>/editar", methods=["GET", "POST"])
@login_required
def cartera_editar(id):
    seed_default_products()
    carpeta = ClientFolder.query.get_or_404(id)
    form = ClientFolderForm(obj=carpeta)
    if carpeta.producto_id is None:
        form.producto_id.data = 0
    if carpeta.ejecutivo_id is None:
        form.ejecutivo_id.data = 0
    if form.validate_on_submit():
        _save_cliente_from_form(carpeta, form)
        db.session.commit()
        flash("Cliente actualizado", "success")
        return redirect(url_for("admin.cartera_detalle", id=carpeta.id))
    return render_template(
        "admin_cartera_form.html",
        form=form,
        carpeta=carpeta,
        active_nav="clientes",
        editing=True,
    )


@admin.route("/clientes/<int:id>/abono", methods=["POST"])
@login_required
def cartera_abono(id):
    carpeta = ClientFolder.query.get_or_404(id)
    form = ClientAbonoForm()
    if form.validate_on_submit():
        abono = ClientAbono(
            folder_id=carpeta.id,
            monto=form.monto.data,
            moneda=form.moneda.data,
            tipo=form.tipo.data,
            product_id=form.product_id.data if form.product_id.data else None,
            fecha=datetime.combine(form.fecha.data, datetime.min.time()),
            referencia=form.referencia.data.strip() if form.referencia.data else None,
            notas=form.notas.data.strip() if form.notas.data else None,
            created_by_id=current_user.id,
        )
        db.session.add(abono)
        if carpeta.estado in ("prospecto", "negociacion"):
            carpeta.estado = "con_abono"
        carpeta.updated_at = datetime.utcnow()
        db.session.commit()
        flash(f"Abono de {form.monto.data:,.0f} {form.moneda.data} registrado", "success")
    else:
        flash("Revisa los datos del abono", "danger")
    return redirect(url_for("admin.cartera_detalle", id=id))


@admin.route("/clientes/<int:id>/abono/<int:abono_id>/eliminar", methods=["POST"])
@login_required
def cartera_abono_eliminar(id, abono_id):
    carpeta = ClientFolder.query.get_or_404(id)
    abono = ClientAbono.query.filter_by(id=abono_id, folder_id=carpeta.id).first_or_404()
    db.session.delete(abono)
    db.session.commit()
    flash("Abono eliminado", "info")
    return redirect(url_for("admin.cartera_detalle", id=id))


@admin.route("/clientes/<int:id>/portal", methods=["POST"])
@login_required
@edit_required
def cartera_portal(id):
    carpeta = ClientFolder.query.get_or_404(id)
    form = PortalAccessForm()
    if form.validate_on_submit():
        carpeta.portal_email = form.portal_email.data.strip().lower()
        carpeta.set_portal_password(form.password.data)
        carpeta.portal_activo = form.activo.data == "1"
        log_activity("editar", "cliente", carpeta.id, carpeta.nombre, "Acceso portal configurado")
        db.session.commit()
        flash("Acceso al portal configurado", "success")
    else:
        _flash_form_errors(form)
    return redirect(url_for("admin.cartera_detalle", id=id))


# ── Archivos ──────────────────────────────────────────────────────

@admin.route("/clientes/<int:id>/upload-multiple", methods=["POST"])
@admin.route("/carteras/<int:id>/upload-multiple", methods=["POST"])
@login_required
def cartera_upload_multiple(id):
    carpeta = ClientFolder.query.get_or_404(id)
    files = request.files.getlist("archivos")
    if not files or all(not f.filename for f in files):
        flash("Selecciona al menos un archivo.", "danger")
        return redirect(url_for("admin.cartera_detalle", id=id))

    subidos = 0
    for file_storage in files:
        if not file_storage or not file_storage.filename:
            continue
        if not allowed_file(file_storage.filename):
            flash(f"Omitido: {secure_filename(file_storage.filename)}", "info")
            continue
        original, stored, size, content_type = save_client_file(file_storage, carpeta.slug)
        db.session.add(ClientFile(
            folder_id=carpeta.id,
            original_filename=original,
            stored_filename=stored,
            content_type=content_type,
            size_bytes=size,
            uploaded_by_id=current_user.id,
        ))
        subidos += 1

    if subidos:
        carpeta.updated_at = datetime.utcnow()
        db.session.commit()
        flash(f"{subidos} archivo(s) subido(s)", "success")
    else:
        flash("No se subió ningún archivo válido.", "danger")
    return redirect(url_for("admin.cartera_detalle", id=id))


@admin.route("/clientes/<int:id>/archivo/<int:file_id>/descargar")
@admin.route("/carteras/<int:id>/archivo/<int:file_id>/descargar")
@login_required
def cartera_descargar(id, file_id):
    carpeta = ClientFolder.query.get_or_404(id)
    client_file = ClientFile.query.filter_by(id=file_id, folder_id=carpeta.id).first_or_404()
    return send_from_directory(
        folder_disk_path(carpeta.slug),
        client_file.stored_filename,
        as_attachment=True,
        download_name=client_file.original_filename,
    )


@admin.route("/clientes/<int:id>/archivo/<int:file_id>/eliminar", methods=["POST"])
@admin.route("/carteras/<int:id>/archivo/<int:file_id>/eliminar", methods=["POST"])
@login_required
def cartera_eliminar_archivo(id, file_id):
    carpeta = ClientFolder.query.get_or_404(id)
    client_file = ClientFile.query.filter_by(id=file_id, folder_id=carpeta.id).first_or_404()
    delete_stored_file(carpeta.slug, client_file.stored_filename)
    db.session.delete(client_file)
    db.session.commit()
    flash("Archivo eliminado", "info")
    return redirect(url_for("admin.cartera_detalle", id=id))


@admin.route("/clientes/<int:id>/eliminar", methods=["POST"])
@admin.route("/carteras/<int:id>/eliminar", methods=["POST"])
@login_required
def cartera_eliminar(id):
    carpeta = ClientFolder.query.get_or_404(id)
    slug = carpeta.slug
    db.session.delete(carpeta)
    db.session.commit()
    delete_folder_directory(slug)
    flash("Cliente eliminado", "info")
    return redirect(url_for("admin.clientes"))


# ── Productos ─────────────────────────────────────────────────────

@admin.route("/productos")
@login_required
def productos():
    seed_default_products()
    lista = Product.query.order_by(Product.orden, Product.nombre).all()
    return render_template("admin_productos.html", productos=lista, active_nav="productos")


@admin.route("/productos/nuevo", methods=["GET", "POST"])
@login_required
@edit_required
def producto_nuevo():
    form = ProductForm()
    if form.validate_on_submit():
        producto = Product(activo=True)
        _fill_product_from_form(producto, form)
        db.session.add(producto)
        db.session.flush()
        log_activity("crear", "producto", producto.id, producto.nombre)
        db.session.commit()
        flash("Producto creado", "success")
        return redirect(url_for("admin.producto_detalle", id=producto.id))
    return render_template("admin_producto_form.html", form=form, editing=False, active_nav="productos")


@admin.route("/productos/<int:id>")
@login_required
def producto_detalle(id):
    producto = Product.query.get_or_404(id)
    return render_template("admin_producto_detalle.html", producto=producto, active_nav="productos")


@admin.route("/productos/<int:id>/editar", methods=["GET", "POST"])
@login_required
@edit_required
def producto_editar(id):
    producto = Product.query.get_or_404(id)
    form = ProductForm(obj=producto)
    if form.validate_on_submit():
        _fill_product_from_form(producto, form)
        log_activity("editar", "producto", producto.id, producto.nombre)
        db.session.commit()
        flash("Producto actualizado", "success")
        return redirect(url_for("admin.producto_detalle", id=producto.id))
    return render_template("admin_producto_form.html", form=form, producto=producto, editing=True, active_nav="productos")


@admin.route("/productos/<int:id>/imagen")
@login_required
def producto_imagen(id):
    producto = Product.query.get_or_404(id)
    if not producto.imagen_filename:
        return redirect(url_for("admin.producto_detalle", id=id))
    return send_file(product_file_path(producto.imagen_filename))


@admin.route("/productos/<int:id>/ficha")
@login_required
def producto_ficha(id):
    producto = Product.query.get_or_404(id)
    if not producto.tiene_ficha:
        flash("Sin ficha técnica.", "danger")
        return redirect(url_for("admin.producto_detalle", id=id))
    return send_file(
        product_file_path(producto.ficha_stored),
        as_attachment=True,
        download_name=producto.ficha_original or "ficha.pdf",
    )


@admin.route("/productos/<int:id>/toggle", methods=["POST"])
@login_required
def producto_toggle(id):
    producto = Product.query.get_or_404(id)
    producto.activo = not producto.activo
    db.session.commit()
    flash("Estado del producto actualizado", "success")
    return redirect(url_for("admin.productos"))


# ── Cotizaciones ──────────────────────────────────────────────────

CONDICIONES_DEFAULT = (
    "Pago: 50% anticipo / 50% contra documentos de embarque.\n"
    "Plazo de entrega: según calendario de cosecha y disponibilidad logística.\n"
    "Embarque: puertos chilenos · Destino: México."
)


@admin.route("/cotizaciones")
@login_required
def cotizaciones():
    seed_default_products()
    estado = request.args.get("estado", "")
    q = Quotation.query
    if estado and estado in COTIZACION_ESTADOS:
        q = q.filter_by(estado=estado)
    lista = q.order_by(Quotation.created_at.desc()).all()
    return render_template(
        "admin_cotizaciones.html",
        cotizaciones=lista,
        filtro_estado=estado,
        active_nav="cotizaciones",
    )


@admin.route("/cotizaciones/nueva", methods=["GET", "POST"])
@login_required
def cotizacion_nueva():
    seed_default_products()
    form = CotizacionForm()
    productos = Product.query.filter_by(activo=True).order_by(Product.orden).all()

    cliente_id = request.args.get("cliente_id", type=int)
    mensaje_id = request.args.get("mensaje_id", type=int) or request.form.get("mensaje_id", type=int)

    if request.method == "GET":
        if cliente_id:
            c = ClientFolder.query.get(cliente_id)
            if c:
                form.folder_id.data = c.id
                form.cliente_nombre.data = c.nombre
                form.cliente_empresa.data = c.empresa
                form.cliente_email.data = c.email
                form.cliente_telefono.data = c.telefono
                form.cliente_pais.data = c.pais
        if mensaje_id:
            m = ContactMessage.query.get(mensaje_id)
            if m:
                form.cliente_nombre.data = m.nombre
                form.cliente_empresa.data = m.empresa
                form.cliente_email.data = m.email
                form.cliente_telefono.data = m.telefono
                form.cliente_pais.data = "México"
        if not form.condiciones.data:
            form.condiciones.data = CONDICIONES_DEFAULT

    if form.validate_on_submit():
        lineas = parse_lineas_from_form(request.form)
        if not lineas:
            flash("Agrega al menos una línea de producto.", "danger")
        else:
            cot = Quotation(
                numero=next_cotizacion_numero(),
                mensaje_id=mensaje_id if mensaje_id else None,
                fecha_emision=datetime.utcnow(),
                created_by_id=current_user.id,
            )
            _fill_cotizacion_from_form(cot, form)
            apply_lineas(cot, lineas)
            db.session.add(cot)
            if cot.folder_id:
                cliente = ClientFolder.query.get(cot.folder_id)
                if cliente and cliente.estado == "prospecto":
                    cliente.estado = "negociacion"
            db.session.commit()
            flash(f"Cotización {cot.numero} creada", "success")
            return redirect(url_for("admin.cotizacion_detalle", id=cot.id))

    return render_template(
        "admin_cotizacion_form.html",
        form=form,
        productos=productos,
        lineas=[],
        editing=False,
        mensaje_id=mensaje_id,
        active_nav="cotizaciones",
    )


@admin.route("/cotizaciones/<int:id>")
@login_required
def cotizacion_detalle(id):
    cot = Quotation.query.get_or_404(id)
    return render_template("admin_cotizacion_detalle.html", cot=cot, active_nav="cotizaciones")


@admin.route("/cotizaciones/<int:id>/editar", methods=["GET", "POST"])
@login_required
def cotizacion_editar(id):
    seed_default_products()
    cot = Quotation.query.get_or_404(id)
    form = CotizacionForm(obj=cot)
    productos = Product.query.filter_by(activo=True).order_by(Product.orden).all()
    if cot.folder_id is None:
        form.folder_id.data = 0

    if form.validate_on_submit():
        lineas = parse_lineas_from_form(request.form)
        if not lineas:
            flash("Agrega al menos una línea de producto.", "danger")
        else:
            _fill_cotizacion_from_form(cot, form)
            apply_lineas(cot, lineas)
            cot.updated_at = datetime.utcnow()
            db.session.commit()
            flash("Cotización actualizada", "success")
            return redirect(url_for("admin.cotizacion_detalle", id=cot.id))

    lineas_data = [
        {
            "descripcion": l.descripcion,
            "cantidad": l.cantidad,
            "unidad": l.unidad,
            "precio_unitario": l.precio_unitario,
            "product_id": l.product_id or 0,
        }
        for l in cot.lineas
    ]
    return render_template(
        "admin_cotizacion_form.html",
        form=form,
        productos=productos,
        lineas=lineas_data,
        cot=cot,
        editing=True,
        active_nav="cotizaciones",
    )


@admin.route("/cotizaciones/<int:id>/pdf")
@login_required
def cotizacion_pdf(id):
    cot = Quotation.query.get_or_404(id)
    buffer = generar_pdf_cotizacion(cot)
    filename = f"{cot.numero}.pdf"
    return send_file(
        buffer,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=filename,
    )


@admin.route("/cotizaciones/<int:id>/eliminar", methods=["POST"])
@login_required
def cotizacion_eliminar(id):
    cot = Quotation.query.get_or_404(id)
    db.session.delete(cot)
    db.session.commit()
    flash("Cotización eliminada", "info")
    return redirect(url_for("admin.cotizaciones"))


@admin.route("/mensaje/<int:id>/cotizar")
@login_required
def mensaje_cotizar(id):
    return redirect(url_for("admin.cotizacion_nueva", mensaje_id=id))


PEDIDO_CONDICIONES_DEFAULT = (
    "Pago: 50% anticipo / 50% contra documentos de embarque.\n"
    "Plazo de entrega: según calendario de cosecha y disponibilidad logística.\n"
    "Embarque: puertos chilenos · Destino: México."
)


@admin.route("/pedidos")
@login_required
def pedidos():
    seed_default_products()
    estado = request.args.get("estado", "")
    q = Order.query
    if estado and estado in PEDIDO_ESTADOS:
        q = q.filter_by(estado=estado)
    lista = q.order_by(Order.created_at.desc()).all()
    return render_template(
        "admin_pedidos.html",
        pedidos=lista,
        filtro_estado=estado,
        active_nav="pedidos",
    )


@admin.route("/pedidos/nueva", methods=["GET", "POST"])
@login_required
def pedido_nueva():
    seed_default_products()
    form = PedidoForm()
    productos = Product.query.filter_by(activo=True).order_by(Product.orden).all()

    cliente_id = request.args.get("cliente_id", type=int)
    cotizacion_id = request.args.get("cotizacion_id", type=int) or request.form.get("cotizacion_id", type=int)
    lineas = []

    if request.method == "GET":
        if cotizacion_id:
            cot = Quotation.query.get(cotizacion_id)
            if cot:
                data = pedido_from_cotizacion(cot)
                form.folder_id.data = data["folder_id"] or 0
                form.cliente_nombre.data = data["cliente_nombre"]
                form.cliente_empresa.data = data["cliente_empresa"]
                form.cliente_email.data = data["cliente_email"]
                form.cliente_telefono.data = data["cliente_telefono"]
                form.cliente_pais.data = data["cliente_pais"]
                form.moneda.data = data["moneda"]
                form.incoterm.data = data["incoterm"]
                form.descuento_pct.data = data["descuento_pct"]
                form.condiciones.data = data["condiciones"] or PEDIDO_CONDICIONES_DEFAULT
                form.notas.data = data["notas"]
                lineas = [
                    {
                        "descripcion": l["descripcion"],
                        "cantidad": l["cantidad"],
                        "unidad": l["unidad"],
                        "precio_unitario": l["precio_unitario"],
                        "product_id": l["product_id"] or 0,
                    }
                    for l in data["lineas"]
                ]
        elif cliente_id:
            c = ClientFolder.query.get(cliente_id)
            if c:
                form.folder_id.data = c.id
                form.cliente_nombre.data = c.nombre
                form.cliente_empresa.data = c.empresa
                form.cliente_email.data = c.email
                form.cliente_telefono.data = c.telefono
                form.cliente_pais.data = c.pais
        if not form.condiciones.data:
            form.condiciones.data = PEDIDO_CONDICIONES_DEFAULT

    if form.validate_on_submit():
        lineas_data = parse_lineas_from_form(request.form)
        if not lineas_data:
            flash("Agrega al menos una línea de producto.", "danger")
        else:
            ped = Order(
                numero=next_pedido_numero(),
                quotation_id=cotizacion_id if cotizacion_id else None,
                fecha_pedido=datetime.utcnow(),
                created_by_id=current_user.id,
            )
            _fill_pedido_from_form(ped, form)
            apply_pedido_lineas(ped, lineas_data)
            db.session.add(ped)

            if cotizacion_id:
                cot = Quotation.query.get(cotizacion_id)
                if cot and cot.estado not in ("rechazada", "cancelada"):
                    cot.estado = "aceptada"

            if ped.folder_id:
                cliente = ClientFolder.query.get(ped.folder_id)
                if cliente and cliente.estado in ("prospecto", "negociacion"):
                    cliente.estado = "cliente_activo"

            db.session.commit()
            flash(f"Pedido {ped.numero} creado", "success")
            return redirect(url_for("admin.pedido_detalle", id=ped.id))

    return render_template(
        "admin_pedido_form.html",
        form=form,
        productos=productos,
        lineas=lineas,
        editing=False,
        cotizacion_id=cotizacion_id,
        active_nav="pedidos",
    )


@admin.route("/pedidos/<int:id>")
@login_required
def pedido_detalle(id):
    ped = Order.query.get_or_404(id)
    return render_template("admin_pedido_detalle.html", ped=ped, active_nav="pedidos")


@admin.route("/pedidos/<int:id>/editar", methods=["GET", "POST"])
@login_required
def pedido_editar(id):
    seed_default_products()
    ped = Order.query.get_or_404(id)
    form = PedidoForm(obj=ped)
    productos = Product.query.filter_by(activo=True).order_by(Product.orden).all()
    if ped.folder_id is None:
        form.folder_id.data = 0
    if ped.fecha_entrega_estimada:
        form.fecha_entrega_estimada.data = ped.fecha_entrega_estimada.date()

    if form.validate_on_submit():
        lineas_data = parse_lineas_from_form(request.form)
        if not lineas_data:
            flash("Agrega al menos una línea de producto.", "danger")
        else:
            _fill_pedido_from_form(ped, form)
            apply_pedido_lineas(ped, lineas_data)
            ped.updated_at = datetime.utcnow()
            db.session.commit()
            flash("Pedido actualizado", "success")
            return redirect(url_for("admin.pedido_detalle", id=ped.id))

    lineas_data = [
        {
            "descripcion": l.descripcion,
            "cantidad": l.cantidad,
            "unidad": l.unidad,
            "precio_unitario": l.precio_unitario,
            "product_id": l.product_id or 0,
        }
        for l in ped.lineas
    ]
    return render_template(
        "admin_pedido_form.html",
        form=form,
        productos=productos,
        lineas=lineas_data,
        ped=ped,
        editing=True,
        cotizacion_id=ped.quotation_id,
        active_nav="pedidos",
    )


@admin.route("/pedidos/<int:id>/eliminar", methods=["POST"])
@login_required
def pedido_eliminar(id):
    ped = Order.query.get_or_404(id)
    db.session.delete(ped)
    db.session.commit()
    flash("Pedido eliminado", "info")
    return redirect(url_for("admin.pedidos"))


@admin.route("/cotizaciones/<int:id>/pedido")
@login_required
def cotizacion_a_pedido(id):
    return redirect(url_for("admin.pedido_nueva", cotizacion_id=id))


@admin.route("/embarques")
@login_required
def embarques():
    estado = request.args.get("estado", "")
    q = Shipment.query
    if estado and estado in EMBARQUE_ESTADOS:
        q = q.filter_by(estado=estado)
    lista = q.order_by(Shipment.created_at.desc()).all()
    return render_template(
        "admin_embarques.html",
        embarques=lista,
        filtro_estado=estado,
        active_nav="embarques",
    )


@admin.route("/embarques/nuevo", methods=["GET", "POST"])
@login_required
def embarque_nuevo():
    form = EmbarqueForm()
    pedido_id = request.args.get("pedido_id", type=int) or request.form.get("pedido_id", type=int)

    if request.method == "GET" and pedido_id:
        ped = Order.query.get(pedido_id)
        if ped:
            data = embarque_from_pedido(ped)
            form.order_id.data = data["order_id"]
            form.puerto_origen.data = data["puerto_origen"]
            form.puerto_destino.data = data["puerto_destino"]
            form.tipo_carga.data = data["tipo_carga"]
            form.temperatura.data = data["temperatura"]
            form.tipo_contenedor.data = data.get("tipo_contenedor", "40")

    if form.validate_on_submit():
        if form.order_id.data == 0:
            flash("Selecciona un pedido válido.", "danger")
        else:
            emb = Shipment(
                numero=next_embarque_numero(),
                fecha_embarque=datetime.utcnow(),
                created_by_id=current_user.id,
            )
            if _fill_embarque_from_form(emb, form):
                db.session.add(emb)
                db.session.flush()
                init_shipment_milestones(emb)
                log_activity("crear", "embarque", emb.id, emb.numero, f"Estado: {emb.estado}")
                db.session.commit()
                flash(f"Embarque {emb.numero} creado", "success")
                return redirect(url_for("admin.embarque_detalle", id=emb.id))
            flash("Pedido no encontrado.", "danger")

    return render_template(
        "admin_embarque_form.html",
        form=form,
        editing=False,
        pedido_id=pedido_id,
        active_nav="embarques",
    )


@admin.route("/embarques/<int:id>")
@login_required
def embarque_detalle(id):
    emb = Shipment.query.get_or_404(id)
    init_shipment_milestones(emb)
    db.session.commit()
    tracking_form = TrackingUpdateForm()
    tracking_form.estado.data = emb.estado
    tracking_form.ultima_ubicacion.data = emb.ultima_ubicacion or ""
    tareas_emb = InternalTask.query.filter_by(shipment_id=emb.id).order_by(InternalTask.fecha_limite).all()
    costo_form = CostoForm()
    return render_template(
        "admin_embarque_detalle.html",
        emb=emb,
        tracking_form=tracking_form,
        costo_form=costo_form,
        tareas_emb=tareas_emb,
        active_nav="embarques",
    )


@admin.route("/embarques/<int:id>/tracking", methods=["POST"])
@login_required
@edit_required
def embarque_tracking(id):
    emb = Shipment.query.get_or_404(id)
    form = TrackingUpdateForm()
    if form.validate_on_submit():
        emb.ultima_ubicacion = form.ultima_ubicacion.data.strip()
        emb.tracking_notas = form.tracking_notas.data.strip() if form.tracking_notas.data else emb.tracking_notas
        emb.estado = form.estado.data
        emb.updated_at = datetime.utcnow()
        if emb.pedido:
            sync_pedido_estado(emb.pedido, emb.estado)
        log_activity("tracking", "embarque", emb.id, emb.numero, form.ultima_ubicacion.data)
        db.session.commit()
        flash("Seguimiento actualizado", "success")
    else:
        _flash_form_errors(form)
    return redirect(url_for("admin.embarque_detalle", id=emb.id))


@admin.route("/embarques/<int:id>/hito/<int:hito_id>/toggle", methods=["POST"])
@login_required
@edit_required
def embarque_hito_toggle(id, hito_id):
    emb = Shipment.query.get_or_404(id)
    hito = ShipmentMilestone.query.filter_by(id=hito_id, shipment_id=emb.id).first_or_404()
    hito.completado = not hito.completado
    hito.fecha = datetime.utcnow() if hito.completado else None
    hito.updated_by_id = current_user.id
    db.session.commit()
    flash("Hito logístico actualizado", "success")
    return redirect(url_for("admin.embarque_detalle", id=emb.id))


@admin.route("/embarques/<int:id>/editar", methods=["GET", "POST"])
@login_required
def embarque_editar(id):
    emb = Shipment.query.get_or_404(id)
    form = EmbarqueForm(obj=emb)
    form.order_id.data = emb.order_id
    if emb.etd:
        form.etd.data = emb.etd.date()
    if emb.eta:
        form.eta.data = emb.eta.date()
    if emb.fecha_zarpe:
        form.fecha_zarpe.data = emb.fecha_zarpe.date()
    if emb.responsable_id:
        form.responsable_id.data = emb.responsable_id

    if form.validate_on_submit():
        if _fill_embarque_from_form(emb, form):
            emb.updated_at = datetime.utcnow()
            db.session.commit()
            flash("Embarque actualizado", "success")
            return redirect(url_for("admin.embarque_detalle", id=emb.id))
        flash("Pedido no encontrado.", "danger")

    return render_template(
        "admin_embarque_form.html",
        form=form,
        emb=emb,
        editing=True,
        pedido_id=emb.order_id,
        active_nav="embarques",
    )


@admin.route("/embarques/<int:id>/eliminar", methods=["POST"])
@login_required
def embarque_eliminar(id):
    emb = Shipment.query.get_or_404(id)
    db.session.delete(emb)
    db.session.commit()
    flash("Embarque eliminado", "info")
    return redirect(url_for("admin.embarques"))


@admin.route("/pedidos/<int:id>/embarque")
@login_required
def pedido_a_embarque(id):
    return redirect(url_for("admin.embarque_nuevo", pedido_id=id))


# ── Países y requisitos ───────────────────────────────────────────

def _fill_pais_from_form(pais, form):
    pais.nombre = form.nombre.data.strip()
    pais.codigo = form.codigo.data.strip().upper()
    pais.notas = form.notas.data.strip() if form.notas.data else None
    pais.activo = form.activo.data == "1"


def _fill_documento_from_form(doc, form):
    doc.titulo = form.titulo.data.strip()
    doc.tipo = form.tipo.data
    doc.estado = form.estado.data
    doc.folder_id = form.folder_id.data or None
    doc.shipment_id = form.shipment_id.data or None
    doc.country_id = form.country_id.data or None
    doc.product_id = form.product_id.data or None
    doc.comentarios = form.comentarios.data.strip() if form.comentarios.data else None
    if form.fecha_vencimiento.data:
        doc.fecha_vencimiento = datetime.combine(form.fecha_vencimiento.data, datetime.min.time())
    else:
        doc.fecha_vencimiento = None
    if doc.esta_vencido and doc.estado == "pendiente":
        doc.estado = "vencido"


def _attach_archivo_a_documento(doc, file_storage):
    if not file_storage or not file_storage.filename:
        return False
    if not allowed_file(file_storage.filename):
        return False
    original, stored, size, ctype = save_export_document(file_storage)
    doc.original_filename = original
    doc.stored_filename = stored
    doc.size_bytes = size
    doc.content_type = ctype
    return True


def _flash_form_errors(form):
    for field, errors in form.errors.items():
        for err in errors:
            flash(f"{err}", "danger")


@admin.route("/paises")
@login_required
def paises():
    seed_default_countries()
    lista = Country.query.order_by(Country.nombre).all()
    return render_template("admin_paises.html", paises=lista, active_nav="paises")


@admin.route("/paises/nuevo", methods=["GET", "POST"])
@login_required
def pais_nuevo():
    form = CountryForm()
    if form.validate_on_submit():
        if Country.query.filter((Country.nombre == form.nombre.data.strip()) | (Country.codigo == form.codigo.data.strip().upper())).first():
            flash("Ya existe un país con ese nombre o código.", "danger")
        else:
            pais = Country()
            _fill_pais_from_form(pais, form)
            db.session.add(pais)
            db.session.commit()
            flash("País creado", "success")
            return redirect(url_for("admin.pais_detalle", id=pais.id))
    return render_template("admin_pais_form.html", form=form, editing=False, active_nav="paises")


@admin.route("/paises/<int:id>")
@login_required
def pais_detalle(id):
    pais = Country.query.get_or_404(id)
    req_form = CountryRequirementForm()
    doc_form = PaisDocumentoUploadForm()
    titulo_prefill = request.args.get("titulo", "")
    tipo_prefill = request.args.get("tipo_doc", "")
    if titulo_prefill:
        doc_form.titulo.data = titulo_prefill
    if tipo_prefill and tipo_prefill in DOCUMENTO_TIPOS:
        doc_form.tipo.data = tipo_prefill
    documentos_pais = (
        ExportDocument.query.filter_by(country_id=pais.id)
        .order_by(ExportDocument.uploaded_at.desc())
        .all()
    )
    return render_template(
        "admin_pais_detalle.html",
        pais=pais,
        req_form=req_form,
        doc_form=doc_form,
        documentos_pais=documentos_pais,
        active_nav="paises",
    )


@admin.route("/paises/<int:id>/documento", methods=["POST"])
@login_required
def pais_documento_subir(id):
    pais = Country.query.get_or_404(id)
    doc_form = PaisDocumentoUploadForm()
    if doc_form.validate_on_submit():
        doc = ExportDocument(
            country_id=pais.id,
            uploaded_by_id=current_user.id,
            estado="pendiente",
            titulo=doc_form.titulo.data.strip(),
            tipo=doc_form.tipo.data,
            comentarios=doc_form.comentarios.data.strip() if doc_form.comentarios.data else None,
        )
        if doc_form.fecha_vencimiento.data:
            doc.fecha_vencimiento = datetime.combine(doc_form.fecha_vencimiento.data, datetime.min.time())
        if _attach_archivo_a_documento(doc, doc_form.archivo.data):
            db.session.add(doc)
            db.session.commit()
            flash(f"PDF «{doc.titulo}» subido para {pais.nombre}", "success")
            return redirect(url_for("admin.documento_detalle", id=doc.id))
        flash("No se pudo guardar el archivo PDF.", "danger")
    else:
        _flash_form_errors(doc_form)
    return redirect(url_for("admin.pais_detalle", id=pais.id))


@admin.route("/paises/<int:id>/editar", methods=["GET", "POST"])
@login_required
def pais_editar(id):
    pais = Country.query.get_or_404(id)
    form = CountryForm(obj=pais)
    form.activo.data = "1" if pais.activo else "0"
    if form.validate_on_submit():
        _fill_pais_from_form(pais, form)
        db.session.commit()
        flash("País actualizado", "success")
        return redirect(url_for("admin.pais_detalle", id=pais.id))
    return render_template("admin_pais_form.html", form=form, pais=pais, editing=True, active_nav="paises")


@admin.route("/paises/<int:id>/requisito", methods=["POST"])
@login_required
def pais_requisito_nuevo(id):
    pais = Country.query.get_or_404(id)
    form = CountryRequirementForm()
    if form.validate_on_submit():
        req = CountryRequirement(
            country_id=pais.id,
            tipo=form.tipo.data,
            titulo=form.titulo.data.strip(),
            descripcion=form.descripcion.data.strip() if form.descripcion.data else None,
            product_id=form.product_id.data or None,
            obligatorio=form.obligatorio.data == "1",
            orden=form.orden.data or 0,
        )
        db.session.add(req)
        db.session.commit()
        flash("Requisito agregado", "success")
    else:
        flash("Revisa los datos del requisito.", "danger")
    return redirect(url_for("admin.pais_detalle", id=pais.id))


@admin.route("/paises/<int:pais_id>/requisito/<int:req_id>/eliminar", methods=["POST"])
@login_required
def pais_requisito_eliminar(pais_id, req_id):
    req = CountryRequirement.query.filter_by(id=req_id, country_id=pais_id).first_or_404()
    db.session.delete(req)
    db.session.commit()
    flash("Requisito eliminado", "info")
    return redirect(url_for("admin.pais_detalle", id=pais_id))


# ── Gestión documental ────────────────────────────────────────────

@admin.route("/documentos")
@login_required
def documentos():
    estado = request.args.get("estado", "")
    tipo = request.args.get("tipo", "")
    q = ExportDocument.query
    if estado:
        q = q.filter_by(estado=estado)
    if tipo:
        q = q.filter_by(tipo=tipo)
    docs = q.order_by(ExportDocument.uploaded_at.desc()).all()
    for d in docs:
        if d.esta_vencido and d.estado not in ("aprobado", "vencido"):
            d.estado = "vencido"
    db.session.commit()
    return render_template(
        "admin_documentos.html",
        documentos=docs,
        filtro_estado=estado,
        filtro_tipo=tipo,
        active_nav="documentos",
    )


@admin.route("/documentos/nuevo", methods=["GET", "POST"])
@login_required
def documento_nuevo():
    form = DocumentoForm()
    pais = None
    prefill = {
        "folder_id": request.args.get("cliente_id", type=int),
        "shipment_id": request.args.get("embarque_id", type=int),
        "country_id": request.args.get("pais_id", type=int),
    }
    for field, val in prefill.items():
        if val:
            getattr(form, field).data = val
    if prefill["country_id"]:
        pais = Country.query.get(prefill["country_id"])
    if request.args.get("titulo"):
        form.titulo.data = request.args.get("titulo")
    tipo_doc = request.args.get("tipo_doc", "")
    if tipo_doc in DOCUMENTO_TIPOS:
        form.tipo.data = tipo_doc

    if request.method == "POST":
        if form.validate_on_submit():
            doc = ExportDocument(uploaded_by_id=current_user.id)
            _fill_documento_from_form(doc, form)
            if form.archivo.data and form.archivo.data.filename:
                if not _attach_archivo_a_documento(doc, form.archivo.data):
                    flash("El archivo debe ser un PDF válido.", "danger")
                    return render_template(
                        "admin_documento_form.html",
                        form=form,
                        pais=pais,
                        editing=False,
                        desde_pais=bool(pais),
                        active_nav="documentos",
                    )
            db.session.add(doc)
            db.session.commit()
            flash("Documento registrado", "success")
            if pais:
                return redirect(url_for("admin.pais_detalle", id=pais.id))
            return redirect(url_for("admin.documento_detalle", id=doc.id))
        _flash_form_errors(form)
    return render_template(
        "admin_documento_form.html",
        form=form,
        pais=pais,
        editing=False,
        desde_pais=bool(pais),
        active_nav="documentos",
    )


@admin.route("/documentos/<int:id>")
@login_required
def documento_detalle(id):
    doc = ExportDocument.query.get_or_404(id)
    if doc.esta_vencido and doc.estado not in ("aprobado", "vencido"):
        doc.estado = "vencido"
        db.session.commit()
    return render_template("admin_documento_detalle.html", doc=doc, active_nav="documentos")


@admin.route("/documentos/<int:id>/editar", methods=["GET", "POST"])
@login_required
def documento_editar(id):
    doc = ExportDocument.query.get_or_404(id)
    form = DocumentoForm(obj=doc)
    if doc.fecha_vencimiento:
        form.fecha_vencimiento.data = doc.fecha_vencimiento.date()

    if request.method == "POST":
        if form.validate_on_submit():
            _fill_documento_from_form(doc, form)
            if form.archivo.data and form.archivo.data.filename:
                if doc.stored_filename:
                    delete_export_document(doc.stored_filename)
                if not _attach_archivo_a_documento(doc, form.archivo.data):
                    flash("El archivo debe ser un PDF válido.", "danger")
                    return render_template("admin_documento_form.html", form=form, doc=doc, editing=True, active_nav="documentos")
            db.session.commit()
            flash("Documento actualizado", "success")
            return redirect(url_for("admin.documento_detalle", id=doc.id))
        _flash_form_errors(form)
    return render_template("admin_documento_form.html", form=form, doc=doc, editing=True, active_nav="documentos")


@admin.route("/documentos/<int:id>/estado/<estado>", methods=["POST"])
@login_required
def documento_cambiar_estado(id, estado):
    if estado not in DOCUMENTO_ESTADOS:
        flash("Estado inválido", "danger")
        return redirect(request.referrer or url_for("admin.documentos"))
    doc = ExportDocument.query.get_or_404(id)
    doc.estado = estado
    db.session.commit()
    flash(f"Estado actualizado a {DOCUMENTO_ESTADOS[estado]}", "success")
    return redirect(url_for("admin.documento_detalle", id=doc.id))


@admin.route("/documentos/<int:id>/descargar")
@login_required
def documento_descargar(id):
    doc = ExportDocument.query.get_or_404(id)
    if not doc.stored_filename:
        flash("Este documento no tiene archivo adjunto.", "danger")
        return redirect(url_for("admin.documento_detalle", id=doc.id))
    path = document_file_path(doc.stored_filename)
    if not os.path.isfile(path):
        flash("Archivo no encontrado en el servidor.", "danger")
        return redirect(url_for("admin.documento_detalle", id=doc.id))
    return send_file(path, as_attachment=True, download_name=doc.original_filename or doc.titulo)


@admin.route("/documentos/<int:id>/eliminar", methods=["POST"])
@login_required
def documento_eliminar(id):
    doc = ExportDocument.query.get_or_404(id)
    if doc.stored_filename:
        delete_export_document(doc.stored_filename)
    db.session.delete(doc)
    db.session.commit()
    flash("Documento eliminado", "info")
    return redirect(url_for("admin.documentos"))


@admin.route("/alertas")
@login_required
def alertas():
    items = get_alertas()
    return render_template("admin_alertas.html", alertas=items, active_nav="alertas")


# ── Tareas internas ───────────────────────────────────────────────

def _fill_tarea_from_form(tarea, form):
    tarea.titulo = form.titulo.data.strip()
    tarea.descripcion = form.descripcion.data.strip() if form.descripcion.data else None
    tarea.responsable_id = form.responsable_id.data or None
    tarea.shipment_id = form.shipment_id.data or None
    tarea.folder_id = form.folder_id.data or None
    tarea.prioridad = form.prioridad.data
    tarea.estado = form.estado.data
    tarea.comentarios = form.comentarios.data.strip() if form.comentarios.data else None
    if form.fecha_limite.data:
        tarea.fecha_limite = datetime.combine(form.fecha_limite.data, datetime.min.time())
    else:
        tarea.fecha_limite = None


@admin.route("/tareas")
@login_required
def tareas():
    estado = request.args.get("estado", "")
    q = InternalTask.query
    if estado and estado in TAREA_ESTADOS:
        q = q.filter_by(estado=estado)
    lista = q.order_by(InternalTask.fecha_limite, InternalTask.created_at.desc()).all()
    return render_template("admin_tareas.html", tareas=lista, filtro_estado=estado, active_nav="tareas")


@admin.route("/tareas/nueva", methods=["GET", "POST"])
@login_required
@edit_required
def tarea_nueva():
    form = TareaForm()
    if request.args.get("embarque_id"):
        form.shipment_id.data = request.args.get("embarque_id", type=int)
    if request.args.get("cliente_id"):
        form.folder_id.data = request.args.get("cliente_id", type=int)
    if form.validate_on_submit():
        tarea = InternalTask(created_by_id=current_user.id)
        _fill_tarea_from_form(tarea, form)
        db.session.add(tarea)
        db.session.commit()
        flash("Tarea creada", "success")
        return redirect(url_for("admin.tareas"))
    return render_template("admin_tarea_form.html", form=form, editing=False, active_nav="tareas")


@admin.route("/tareas/<int:id>/editar", methods=["GET", "POST"])
@login_required
@edit_required
def tarea_editar(id):
    tarea = InternalTask.query.get_or_404(id)
    form = TareaForm(obj=tarea)
    if tarea.fecha_limite:
        form.fecha_limite.data = tarea.fecha_limite.date()
    if form.validate_on_submit():
        _fill_tarea_from_form(tarea, form)
        tarea.updated_at = datetime.utcnow()
        db.session.commit()
        flash("Tarea actualizada", "success")
        return redirect(url_for("admin.tareas"))
    return render_template("admin_tarea_form.html", form=form, tarea=tarea, editing=True, active_nav="tareas")


@admin.route("/tareas/<int:id>/estado/<estado>", methods=["POST"])
@login_required
@edit_required
def tarea_cambiar_estado(id, estado):
    if estado not in TAREA_ESTADOS:
        flash("Estado inválido", "danger")
        return redirect(url_for("admin.tareas"))
    tarea = InternalTask.query.get_or_404(id)
    tarea.estado = estado
    db.session.commit()
    flash("Estado de tarea actualizado", "success")
    return redirect(request.referrer or url_for("admin.tareas"))


@admin.route("/tareas/<int:id>/eliminar", methods=["POST"])
@login_required
@edit_required
def tarea_eliminar(id):
    tarea = InternalTask.query.get_or_404(id)
    db.session.delete(tarea)
    db.session.commit()
    flash("Tarea eliminada", "info")
    return redirect(url_for("admin.tareas"))


# ── Calculadora de contenedores ───────────────────────────────────

@admin.route("/calculadora-contenedores", methods=["GET", "POST"])
@login_required
def calculadora_contenedores():
    form = ContainerCalcForm()
    resultado = None
    if form.validate_on_submit():
        resultado = calcular_contenedor(
            form.tipo_contenedor.data,
            form.cajas_largo.data,
            form.cajas_ancho.data,
            form.cajas_alto.data,
            form.peso_caja.data,
            form.cantidad_cajas.data,
        )
    return render_template(
        "admin_calculadora.html",
        form=form,
        resultado=resultado,
        active_nav="calculadora",
    )


# ── Usuarios y roles ──────────────────────────────────────────────

@admin.route("/usuarios")
@login_required
@role_required("ceo")
def usuarios():
    lista = AdminUser.query.order_by(AdminUser.username).all()
    return render_template("admin_usuarios.html", usuarios=lista, active_nav="usuarios")


@admin.route("/usuarios/nuevo", methods=["GET", "POST"])
@login_required
@role_required("ceo")
def usuario_nuevo():
    form = UsuarioForm()
    if form.validate_on_submit():
        if AdminUser.query.filter_by(username=form.username.data.strip()).first():
            flash("Ese usuario ya existe.", "danger")
        elif not form.password.data:
            flash("La contraseña es obligatoria para usuarios nuevos.", "danger")
        else:
            user = AdminUser(
                username=form.username.data.strip(),
                nombre=form.nombre.data.strip() if form.nombre.data else None,
                rol=form.rol.data,
                activo=form.activo.data == "1",
            )
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash("Usuario creado", "success")
            return redirect(url_for("admin.usuarios"))
    return render_template("admin_usuario_form.html", form=form, editing=False, active_nav="usuarios")


@admin.route("/usuarios/<int:id>/editar", methods=["GET", "POST"])
@login_required
@role_required("ceo")
def usuario_editar(id):
    user = AdminUser.query.get_or_404(id)
    form = UsuarioForm(obj=user)
    form.activo.data = "1" if user.activo else "0"
    if form.validate_on_submit():
        user.username = form.username.data.strip()
        user.nombre = form.nombre.data.strip() if form.nombre.data else None
        user.rol = form.rol.data
        user.activo = form.activo.data == "1"
        if form.password.data:
            user.set_password(form.password.data)
        db.session.commit()
        flash("Usuario actualizado", "success")
        return redirect(url_for("admin.usuarios"))
    return render_template("admin_usuario_form.html", form=form, user=user, editing=True, active_nav="usuarios")


# ── Reportes e indicadores ────────────────────────────────────────

@admin.route("/reportes")
@login_required
def reportes():
    data = get_reportes_data()
    return render_template("admin_reportes.html", reportes=data, active_nav="reportes")


# ── Costos de embarque ────────────────────────────────────────────

@admin.route("/embarques/<int:id>/costos", methods=["POST"])
@login_required
@edit_required
def embarque_costo_nuevo(id):
    emb = Shipment.query.get_or_404(id)
    form = CostoForm()
    if form.validate_on_submit():
        costo = ShipmentCost(
            shipment_id=emb.id,
            tipo=form.tipo.data,
            concepto=form.concepto.data.strip(),
            monto=form.monto.data,
            moneda=form.moneda.data,
            notas=form.notas.data.strip() if form.notas.data else None,
            created_by_id=current_user.id,
        )
        db.session.add(costo)
        log_activity("crear", "costo", emb.id, emb.numero, f"{form.concepto.data}: {form.monto.data} {form.moneda.data}")
        db.session.commit()
        flash("Costo registrado", "success")
    else:
        _flash_form_errors(form)
    return redirect(url_for("admin.embarque_detalle", id=emb.id))


@admin.route("/embarques/<int:id>/costos/<int:costo_id>/eliminar", methods=["POST"])
@login_required
@edit_required
def embarque_costo_eliminar(id, costo_id):
    emb = Shipment.query.get_or_404(id)
    costo = ShipmentCost.query.filter_by(id=costo_id, shipment_id=emb.id).first_or_404()
    log_activity("eliminar", "costo", emb.id, emb.numero, costo.concepto)
    db.session.delete(costo)
    db.session.commit()
    flash("Costo eliminado", "info")
    return redirect(url_for("admin.embarque_detalle", id=emb.id))


# ── Contratos ─────────────────────────────────────────────────────

def _fill_contrato_from_form(contrato, form):
    contrato.titulo = form.titulo.data.strip()
    contrato.folder_id = form.folder_id.data or None
    contrato.country_id = form.country_id.data or None
    contrato.product_id = form.product_id.data or None
    contrato.responsable_id = form.responsable_id.data or None
    contrato.estado = form.estado.data
    contrato.renovacion_auto = form.renovacion_auto.data == "1"
    contrato.condiciones = form.condiciones.data.strip() if form.condiciones.data else None
    contrato.notas = form.notas.data.strip() if form.notas.data else None
    if form.fecha_inicio.data:
        contrato.fecha_inicio = datetime.combine(form.fecha_inicio.data, datetime.min.time())
    if form.fecha_fin.data:
        contrato.fecha_fin = datetime.combine(form.fecha_fin.data, datetime.min.time())
    sync_contrato_estado(contrato)


@admin.route("/contratos")
@login_required
def contratos():
    estado = request.args.get("estado", "")
    q = Contract.query
    if estado and estado in CONTRATO_ESTADOS:
        q = q.filter_by(estado=estado)
    lista = q.order_by(Contract.fecha_fin, Contract.created_at.desc()).all()
    for c in lista:
        sync_contrato_estado(c)
    db.session.commit()
    return render_template("admin_contratos.html", contratos=lista, filtro_estado=estado, active_nav="contratos")


@admin.route("/contratos/nuevo", methods=["GET", "POST"])
@login_required
@edit_required
def contrato_nuevo():
    form = ContratoForm()
    if request.args.get("cliente_id"):
        form.folder_id.data = request.args.get("cliente_id", type=int)
    if form.validate_on_submit():
        contrato = Contract(
            numero=next_contrato_numero(),
            created_by_id=current_user.id,
        )
        _fill_contrato_from_form(contrato, form)
        if form.archivo.data:
            orig, stored, size, ctype = save_contract_file(form.archivo.data)
            contrato.original_filename = orig
            contrato.stored_filename = stored
            contrato.size_bytes = size
            contrato.content_type = ctype
        db.session.add(contrato)
        db.session.flush()
        log_activity("crear", "contrato", contrato.id, contrato.numero, contrato.titulo)
        db.session.commit()
        flash(f"Contrato {contrato.numero} creado", "success")
        return redirect(url_for("admin.contrato_detalle", id=contrato.id))
    return render_template("admin_contrato_form.html", form=form, editing=False, active_nav="contratos")


@admin.route("/contratos/<int:id>")
@login_required
def contrato_detalle(id):
    contrato = Contract.query.get_or_404(id)
    sync_contrato_estado(contrato)
    db.session.commit()
    return render_template("admin_contrato_detalle.html", contrato=contrato, active_nav="contratos")


@admin.route("/contratos/<int:id>/editar", methods=["GET", "POST"])
@login_required
@edit_required
def contrato_editar(id):
    contrato = Contract.query.get_or_404(id)
    form = ContratoForm(obj=contrato)
    form.renovacion_auto.data = "1" if contrato.renovacion_auto else "0"
    if contrato.fecha_inicio:
        form.fecha_inicio.data = contrato.fecha_inicio.date()
    if contrato.fecha_fin:
        form.fecha_fin.data = contrato.fecha_fin.date()
    if form.validate_on_submit():
        _fill_contrato_from_form(contrato, form)
        if form.archivo.data:
            delete_contract_file(contrato.stored_filename)
            orig, stored, size, ctype = save_contract_file(form.archivo.data)
            contrato.original_filename = orig
            contrato.stored_filename = stored
            contrato.size_bytes = size
            contrato.content_type = ctype
        contrato.updated_at = datetime.utcnow()
        log_activity("editar", "contrato", contrato.id, contrato.numero)
        db.session.commit()
        flash("Contrato actualizado", "success")
        return redirect(url_for("admin.contrato_detalle", id=contrato.id))
    return render_template("admin_contrato_form.html", form=form, contrato=contrato, editing=True, active_nav="contratos")


@admin.route("/contratos/<int:id>/descargar")
@login_required
def contrato_descargar(id):
    contrato = Contract.query.get_or_404(id)
    if not contrato.tiene_archivo:
        flash("Este contrato no tiene archivo.", "danger")
        return redirect(url_for("admin.contrato_detalle", id=id))
    return send_file(
        contract_file_path(contrato.stored_filename),
        as_attachment=True,
        download_name=contrato.original_filename or "contrato.pdf",
    )


@admin.route("/contratos/<int:id>/eliminar", methods=["POST"])
@login_required
@edit_required
def contrato_eliminar(id):
    contrato = Contract.query.get_or_404(id)
    log_activity("eliminar", "contrato", contrato.id, contrato.numero)
    delete_contract_file(contrato.stored_filename)
    db.session.delete(contrato)
    db.session.commit()
    flash("Contrato eliminado", "info")
    return redirect(url_for("admin.contratos"))


# ── Biblioteca de plantillas ──────────────────────────────────────

@admin.route("/plantillas")
@login_required
def plantillas():
    tipo = request.args.get("tipo", "")
    q = DocumentTemplate.query
    if tipo and tipo in PLANTILLA_TIPOS:
        q = q.filter_by(tipo=tipo)
    lista = q.order_by(DocumentTemplate.tipo, DocumentTemplate.titulo).all()
    return render_template("admin_plantillas.html", plantillas=lista, filtro_tipo=tipo, active_nav="plantillas")


@admin.route("/plantillas/nueva", methods=["GET", "POST"])
@login_required
@edit_required
def plantilla_nueva():
    form = PlantillaForm()
    if form.validate_on_submit():
        if not form.archivo.data:
            flash("Debes subir un archivo.", "danger")
        else:
            plantilla = DocumentTemplate(uploaded_by_id=current_user.id)
            plantilla.titulo = form.titulo.data.strip()
            plantilla.tipo = form.tipo.data
            plantilla.descripcion = form.descripcion.data.strip() if form.descripcion.data else None
            plantilla.activo = form.activo.data == "1"
            orig, stored, size, ctype = save_template_file(form.archivo.data)
            plantilla.original_filename = orig
            plantilla.stored_filename = stored
            plantilla.size_bytes = size
            plantilla.content_type = ctype
            db.session.add(plantilla)
            db.session.flush()
            log_activity("subir", "plantilla", plantilla.id, plantilla.titulo)
            db.session.commit()
            flash("Plantilla agregada", "success")
            return redirect(url_for("admin.plantillas"))
    return render_template("admin_plantilla_form.html", form=form, editing=False, active_nav="plantillas")


@admin.route("/plantillas/<int:id>/editar", methods=["GET", "POST"])
@login_required
@edit_required
def plantilla_editar(id):
    plantilla = DocumentTemplate.query.get_or_404(id)
    form = PlantillaForm(obj=plantilla)
    form.activo.data = "1" if plantilla.activo else "0"
    if form.validate_on_submit():
        plantilla.titulo = form.titulo.data.strip()
        plantilla.tipo = form.tipo.data
        plantilla.descripcion = form.descripcion.data.strip() if form.descripcion.data else None
        plantilla.activo = form.activo.data == "1"
        if form.archivo.data:
            delete_template_file(plantilla.stored_filename)
            orig, stored, size, ctype = save_template_file(form.archivo.data)
            plantilla.original_filename = orig
            plantilla.stored_filename = stored
            plantilla.size_bytes = size
            plantilla.content_type = ctype
        log_activity("editar", "plantilla", plantilla.id, plantilla.titulo)
        db.session.commit()
        flash("Plantilla actualizada", "success")
        return redirect(url_for("admin.plantillas"))
    return render_template("admin_plantilla_form.html", form=form, plantilla=plantilla, editing=True, active_nav="plantillas")


@admin.route("/plantillas/<int:id>/descargar")
@login_required
def plantilla_descargar(id):
    plantilla = DocumentTemplate.query.get_or_404(id)
    if not plantilla.tiene_archivo:
        flash("Sin archivo.", "danger")
        return redirect(url_for("admin.plantillas"))
    return send_file(
        template_file_path(plantilla.stored_filename),
        as_attachment=True,
        download_name=plantilla.original_filename or "plantilla",
    )


@admin.route("/plantillas/<int:id>/eliminar", methods=["POST"])
@login_required
@edit_required
def plantilla_eliminar(id):
    plantilla = DocumentTemplate.query.get_or_404(id)
    log_activity("eliminar", "plantilla", plantilla.id, plantilla.titulo)
    delete_template_file(plantilla.stored_filename)
    db.session.delete(plantilla)
    db.session.commit()
    flash("Plantilla eliminada", "info")
    return redirect(url_for("admin.plantillas"))


# ── Historial de operaciones ──────────────────────────────────────

@admin.route("/notificaciones")
@login_required
def notificaciones():
    logs = NotificationLog.query.order_by(NotificationLog.created_at.desc()).limit(100).all()
    from flask import current_app
    smtp_configurado = bool(current_app.config.get("SMTP_HOST"))
    return render_template(
        "admin_notificaciones.html",
        logs=logs,
        smtp_configurado=smtp_configurado,
        notify_email=current_app.config.get("NOTIFY_EMAIL"),
        active_nav="notificaciones",
    )


@admin.route("/notificaciones/enviar-resumen", methods=["POST"])
@login_required
@role_required("ceo", "comercial")
def notificaciones_enviar_resumen():
    from app.alertas import get_alertas
    alertas = get_alertas()
    ok, log = enviar_resumen_alertas(alertas)
    db.session.commit()
    if ok:
        flash("Resumen de alertas enviado por email", "success")
    elif log and log.error_detalle:
        flash(f"No se pudo enviar: {log.error_detalle}", "danger")
    else:
        flash("No hay alertas críticas/advertencias para enviar.", "info")
    return redirect(url_for("admin.notificaciones"))


@admin.route("/historial")
@login_required
def historial():
    entidad = request.args.get("entidad", "")
    q = ActivityLog.query
    if entidad and entidad in AUDIT_ENTIDADES:
        q = q.filter_by(entidad_tipo=entidad)
    logs = q.order_by(ActivityLog.created_at.desc()).limit(200).all()
    return render_template("admin_historial.html", logs=logs, filtro_entidad=entidad, active_nav="historial")


@admin.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Sesión cerrada", "info")
    return redirect(url_for("admin.login"))
