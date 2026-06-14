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

from app.models import AdminUser, ContactMessage, ClientFolder, ClientFile, Product, ClientAbono, Quotation, Order, Shipment
from app import db, login_manager
from app.forms import LoginForm, ClientFolderForm, ClientFileUploadForm, ClientAbonoForm, ProductForm, CotizacionForm, PedidoForm, EmbarqueForm
from app.upload_utils import (
    slugify,
    unique_slug,
    allowed_file,
    save_client_file,
    delete_stored_file,
    delete_folder_directory,
    folder_disk_path,
)
from app.admin_stats import get_dashboard_kpis
from app.constants import (
    CLIENTE_ESTADOS, CLIENTE_ESTADO_COLORS, CLIENTE_ESTADO_ICONS,
    PRODUCTO_CATEGORIAS, ABONO_TIPOS,
    COTIZACION_ESTADOS, COTIZACION_ESTADO_COLORS, COTIZACION_ESTADO_ICONS,
    PEDIDO_ESTADOS, PEDIDO_ESTADO_COLORS, PEDIDO_ESTADO_ICONS,
    EMBARQUE_ESTADOS, EMBARQUE_ESTADO_COLORS, EMBARQUE_ESTADO_ICONS, CARGA_TIPOS,
)
from app.cotizacion_utils import (
    next_cotizacion_numero, parse_lineas_from_form, apply_lineas, calc_fecha_vencimiento,
)
from app.pedido_utils import next_pedido_numero, apply_lineas as apply_pedido_lineas, pedido_from_cotizacion
from app.embarque_utils import next_embarque_numero, embarque_from_pedido, sync_pedido_estado
from app.pdf_cotizacion import generar_pdf_cotizacion
from app.seed import seed_default_products

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
            "embarques_count": Shipment.query.filter(Shipment.estado.notin_(["entregado", "cancelado"])).count(),
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
        }
    return {}


def _save_cliente_from_form(carpeta, form):
    carpeta.nombre = form.nombre.data.strip()
    carpeta.empresa = form.empresa.data.strip() if form.empresa.data else None
    carpeta.contacto = form.contacto.data.strip() if form.contacto.data else None
    carpeta.email = form.email.data.strip() if form.email.data else None
    carpeta.telefono = form.telefono.data.strip() if form.telefono.data else None
    carpeta.pais = form.pais.data.strip() if form.pais.data else None
    carpeta.estado = form.estado.data
    carpeta.producto_id = form.producto_id.data if form.producto_id.data else None
    carpeta.valor_estimado = form.valor_estimado.data
    carpeta.moneda_estimada = form.moneda_estimada.data
    carpeta.notas = form.notas.data.strip() if form.notas.data else None


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
    emb.puerto_origen = form.puerto_origen.data
    emb.puerto_destino = form.puerto_destino.data
    emb.naviera = form.naviera.data.strip() if form.naviera.data else None
    emb.numero_contenedor = form.numero_contenedor.data.strip() if form.numero_contenedor.data else None
    emb.numero_bl = form.numero_bl.data.strip() if form.numero_bl.data else None
    emb.tipo_carga = form.tipo_carga.data
    emb.temperatura = form.temperatura.data.strip() if form.temperatura.data else None
    emb.notas = form.notas.data.strip() if form.notas.data else None
    emb.etd = datetime.combine(form.etd.data, datetime.min.time()) if form.etd.data else None
    emb.eta = datetime.combine(form.eta.data, datetime.min.time()) if form.eta.data else None
    sync_pedido_estado(ped, emb.estado)
    return True


@admin.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = AdminUser.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
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
    return render_template(
        "admin_cartera_detalle.html",
        carpeta=carpeta,
        abono_form=abono_form,
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
def producto_nuevo():
    form = ProductForm()
    if form.validate_on_submit():
        db.session.add(Product(
            nombre=form.nombre.data.strip(),
            categoria=form.categoria.data,
            descripcion=form.descripcion.data.strip() if form.descripcion.data else None,
            orden=form.orden.data or 0,
            activo=True,
        ))
        db.session.commit()
        flash("Producto creado", "success")
        return redirect(url_for("admin.productos"))
    return render_template("admin_producto_form.html", form=form, editing=False, active_nav="productos")


@admin.route("/productos/<int:id>/editar", methods=["GET", "POST"])
@login_required
def producto_editar(id):
    producto = Product.query.get_or_404(id)
    form = ProductForm(obj=producto)
    if form.validate_on_submit():
        producto.nombre = form.nombre.data.strip()
        producto.categoria = form.categoria.data
        producto.descripcion = form.descripcion.data.strip() if form.descripcion.data else None
        producto.orden = form.orden.data or 0
        db.session.commit()
        flash("Producto actualizado", "success")
        return redirect(url_for("admin.productos"))
    return render_template("admin_producto_form.html", form=form, producto=producto, editing=True, active_nav="productos")


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
    return render_template("admin_embarque_detalle.html", emb=emb, active_nav="embarques")


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


@admin.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Sesión cerrada", "info")
    return redirect(url_for("admin.login"))
