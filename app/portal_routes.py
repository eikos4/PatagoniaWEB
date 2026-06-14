from functools import wraps

from flask import Blueprint, render_template, redirect, url_for, flash, session, send_file

from app.models import ClientFolder, ExportDocument
from app.forms import PortalLoginForm
from app.constants import (
    EMBARQUE_ESTADOS,
    EMBARQUE_ESTADO_COLORS,
    EMBARQUE_ESTADO_ICONS,
    PEDIDO_ESTADOS,
    PEDIDO_ESTADO_COLORS,
    PEDIDO_ESTADO_ICONS,
    DOCUMENTO_TIPOS,
    LOGISTICA_ETAPAS,
    LOGISTICA_ETAPA_ICONS,
)

portal = Blueprint("portal", __name__, template_folder="templates")

ESTADOS_FINALIZADOS = ("entregado", "cerrado", "cancelado")
PRIORIDAD_DESTACADO = ("en_transito", "en_puerto", "en_destino", "programado", "en_preparacion")


def portal_login_required(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if not session.get("portal_cliente_id"):
            return redirect(url_for("portal.login"))
        return f(*args, **kwargs)
    return wrapped


def _cliente_actual():
    cid = session.get("portal_cliente_id")
    if not cid:
        return None
    return ClientFolder.query.get(cid)


def _embarques_activos(cliente):
    return [e for e in cliente.embarques if e.estado not in ESTADOS_FINALIZADOS]


def _embarques_entregados(cliente):
    return [e for e in cliente.embarques if e.estado in ("entregado", "cerrado")]


def _embarque_destacado(activos):
    for estado in PRIORIDAD_DESTACADO:
        for e in activos:
            if e.estado == estado:
                return e
    return activos[0] if activos else None


@portal.context_processor
def inject_portal():
    cliente = _cliente_actual()
    return {
        "portal_cliente": cliente,
        "embarque_estados": EMBARQUE_ESTADOS,
        "embarque_estado_colores": EMBARQUE_ESTADO_COLORS,
        "embarque_estado_iconos": EMBARQUE_ESTADO_ICONS,
        "pedido_estados": PEDIDO_ESTADOS,
        "pedido_estado_colores": PEDIDO_ESTADO_COLORS,
        "pedido_estado_iconos": PEDIDO_ESTADO_ICONS,
        "documento_tipos": DOCUMENTO_TIPOS,
        "logistica_etapas": LOGISTICA_ETAPAS,
        "logistica_etapa_iconos": LOGISTICA_ETAPA_ICONS,
    }


@portal.route("/login", methods=["GET", "POST"])
def login():
    if session.get("portal_cliente_id"):
        return redirect(url_for("portal.dashboard"))
    form = PortalLoginForm()
    if form.validate_on_submit():
        cliente = ClientFolder.query.filter_by(
            portal_email=form.email.data.strip().lower(),
            portal_activo=True,
        ).first()
        if cliente and cliente.check_portal_password(form.password.data):
            session["portal_cliente_id"] = cliente.id
            flash(f"Bienvenido, {cliente.nombre}", "success")
            return redirect(url_for("portal.dashboard"))
        flash("Credenciales incorrectas o portal no activo.", "danger")
    return render_template("portal_login.html", form=form)


@portal.route("/logout")
def logout():
    session.pop("portal_cliente_id", None)
    flash("Sesión cerrada", "info")
    return redirect(url_for("portal.login"))


@portal.route("/")
@portal_login_required
def dashboard():
    cliente = _cliente_actual()
    if not cliente:
        return redirect(url_for("portal.logout"))
    activos = _embarques_activos(cliente)
    entregados = _embarques_entregados(cliente)
    pedidos = [p for p in cliente.pedidos if p.estado != "cancelado"][:8]
    docs = ExportDocument.query.filter_by(folder_id=cliente.id, estado="aprobado").order_by(
        ExportDocument.uploaded_at.desc()
    ).limit(6).all()
    return render_template(
        "portal_dashboard.html",
        cliente=cliente,
        embarques_activos=activos,
        embarques_entregados=entregados,
        embarque_destacado=_embarque_destacado(activos),
        pedidos=pedidos,
        documentos=docs,
        ejecutivo=cliente.ejecutivo,
    )


@portal.route("/embarques")
@portal_login_required
def embarques():
    cliente = _cliente_actual()
    return render_template(
        "portal_embarques.html",
        cliente=cliente,
        embarques=cliente.embarques,
        embarques_activos=_embarques_activos(cliente),
        embarques_entregados=_embarques_entregados(cliente),
    )


@portal.route("/embarques/<int:id>")
@portal_login_required
def embarque_detalle(id):
    cliente = _cliente_actual()
    embarque = next((e for e in cliente.embarques if e.id == id), None)
    if not embarque:
        flash("Embarque no encontrado.", "danger")
        return redirect(url_for("portal.embarques"))
    docs = [d for d in embarque.documentos if d.estado == "aprobado"]
    if not docs:
        docs = ExportDocument.query.filter_by(
            folder_id=cliente.id, shipment_id=embarque.id, estado="aprobado"
        ).all()
    return render_template(
        "portal_embarque_detalle.html",
        cliente=cliente,
        embarque=embarque,
        documentos=docs,
    )


@portal.route("/pedidos")
@portal_login_required
def pedidos():
    cliente = _cliente_actual()
    lista = [p for p in cliente.pedidos if p.estado != "cancelado"]
    return render_template("portal_pedidos.html", cliente=cliente, pedidos=lista)


@portal.route("/documentos")
@portal_login_required
def documentos():
    cliente = _cliente_actual()
    docs = ExportDocument.query.filter_by(folder_id=cliente.id, estado="aprobado").order_by(
        ExportDocument.uploaded_at.desc()
    ).all()
    return render_template("portal_documentos.html", cliente=cliente, documentos=docs)


@portal.route("/documentos/<int:id>/descargar")
@portal_login_required
def documento_descargar(id):
    cliente = _cliente_actual()
    doc = ExportDocument.query.filter_by(id=id, folder_id=cliente.id, estado="aprobado").first_or_404()
    if not doc.tiene_archivo:
        flash("Archivo no disponible.", "danger")
        return redirect(url_for("portal.documentos"))
    from app.document_utils import document_file_path
    return send_file(
        document_file_path(doc.stored_filename),
        as_attachment=True,
        download_name=doc.original_filename or "documento.pdf",
    )
