import json
from datetime import datetime
from functools import wraps

from flask import Blueprint, render_template, redirect, url_for, flash, session, send_file, request

from app import db
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
    FIRMA_PARTES,
)
from app.portal_utils import (
    get_portal_alertas,
    get_documentos_comerciales,
    group_documentos_por_anio,
    documentos_portal_stats,
    alertas_portal_stats,
    pedidos_portal_stats,
    pedido_flujo_index,
    PEDIDO_FLUJO_ESTADOS,
)
from app.portal_tutorial_data import PORTAL_GUIA_IMPORTADOR, PORTAL_MODULE_TOURS
from app.signature_utils import register_document_signature, parse_geo_form, document_signing_status
from app.pdf_signature import apply_signatures_to_pdf

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
        "portal_guia": PORTAL_GUIA_IMPORTADOR,
        "portal_tours_json": json.dumps(PORTAL_MODULE_TOURS, ensure_ascii=False),
        "show_portal_welcome": session.pop("show_portal_welcome", False),
        "firma_partes": FIRMA_PARTES,
        "pedido_flujo_index": pedido_flujo_index,
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
            session["show_portal_welcome"] = True
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
    alertas = get_portal_alertas(cliente)
    return render_template(
        "portal_dashboard.html",
        cliente=cliente,
        embarques_activos=activos,
        embarques_entregados=entregados,
        embarque_destacado=_embarque_destacado(activos),
        pedidos=pedidos,
        documentos=docs,
        alertas=alertas,
        alertas_stats=alertas_portal_stats(alertas),
        ejecutivo=cliente.ejecutivo,
        active_nav="inicio",
    )


@portal.route("/embarques")
@portal_login_required
def embarques():
    cliente = _cliente_actual()
    activos = _embarques_activos(cliente)
    entregados = _embarques_entregados(cliente)
    embarques = sorted(
        cliente.embarques,
        key=lambda e: (
            e.estado in ESTADOS_FINALIZADOS,
            e.eta or datetime.max,
        ),
    )
    return render_template(
        "portal_embarques.html",
        cliente=cliente,
        embarques=embarques,
        embarques_activos=activos,
        embarques_entregados=entregados,
        active_nav="embarques",
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
        active_nav="embarques",
    )


@portal.route("/pedidos")
@portal_login_required
def pedidos():
    cliente = _cliente_actual()
    lista = sorted(
        [p for p in cliente.pedidos if p.estado != "cancelado"],
        key=lambda p: p.fecha_pedido or datetime.min,
        reverse=True,
    )
    return render_template(
        "portal_pedidos.html",
        cliente=cliente,
        pedidos=lista,
        pedidos_stats=pedidos_portal_stats(lista),
        active_nav="pedidos",
    )


@portal.route("/facturas")
@portal_login_required
def facturas():
    cliente = _cliente_actual()
    docs = get_documentos_comerciales(cliente)
    return render_template(
        "portal_facturas.html",
        cliente=cliente,
        documentos=docs,
        documentos_por_anio=group_documentos_por_anio(docs),
        docs_stats=documentos_portal_stats(docs),
        active_nav="facturas",
    )


@portal.route("/alertas")
@portal_login_required
def alertas():
    cliente = _cliente_actual()
    lista = get_portal_alertas(cliente)
    return render_template(
        "portal_alertas.html",
        cliente=cliente,
        alertas=lista,
        alertas_stats=alertas_portal_stats(lista),
        active_nav="alertas",
    )


@portal.route("/guia-importacion")
@portal_login_required
def guia_importacion():
    cliente = _cliente_actual()
    return render_template(
        "portal_guia_importacion.html",
        cliente=cliente,
        guia=PORTAL_GUIA_IMPORTADOR,
        active_nav="guia",
    )


@portal.route("/documentos")
@portal_login_required
def documentos():
    cliente = _cliente_actual()
    docs = ExportDocument.query.filter_by(folder_id=cliente.id, estado="aprobado").order_by(
        ExportDocument.uploaded_at.asc()
    ).all()
    return render_template(
        "portal_documentos.html",
        cliente=cliente,
        documentos=docs,
        documentos_por_anio=group_documentos_por_anio(docs),
        docs_stats=documentos_portal_stats(docs),
        active_nav="documentos",
    )


@portal.route("/documentos/<int:id>/firmar", methods=["GET", "POST"])
@portal_login_required
def documento_firmar(id):
    cliente = _cliente_actual()
    doc = ExportDocument.query.filter_by(id=id, folder_id=cliente.id, estado="aprobado").first_or_404()
    if doc.firma_importador:
        flash("Ya firmaste este documento.", "info")
        return redirect(url_for("portal.documentos"))

    if request.method == "POST":
        lat, lng, loc = parse_geo_form(request.form)
        firma, err = register_document_signature(
            doc,
            "importador",
            request.form.get("signer_name") or cliente.contacto or cliente.nombre,
            request.form.get("signer_email") or cliente.portal_email or cliente.email or "",
            request.form.get("signature_data"),
            client_folder_id=cliente.id,
            latitude=lat,
            longitude=lng,
            location_label=loc,
        )
        if err:
            flash(err, "danger")
            return render_template(
                "portal_documento_firmar.html",
                cliente=cliente,
                doc=doc,
                parte_label=FIRMA_PARTES["importador"],
                signer_name=cliente.contacto or cliente.nombre,
                signer_email=cliente.portal_email or cliente.email or "",
                active_nav="documentos",
            )
        db.session.flush()
        pdf_err = apply_signatures_to_pdf(doc)
        if pdf_err:
            db.session.rollback()
            flash(pdf_err, "danger")
            return render_template(
                "portal_documento_firmar.html",
                cliente=cliente,
                doc=doc,
                parte_label=FIRMA_PARTES["importador"],
                signer_name=cliente.contacto or cliente.nombre,
                signer_email=cliente.portal_email or cliente.email or "",
                active_nav="documentos",
            )
        db.session.commit()
        flash(f"Documento firmado correctamente. Guarda tu token de verificación: {firma.token}", "success")
        return redirect(url_for("portal.documentos"))

    return render_template(
        "portal_documento_firmar.html",
        cliente=cliente,
        doc=doc,
        parte_label=FIRMA_PARTES["importador"],
        signer_name=cliente.contacto or cliente.nombre,
        signer_email=cliente.portal_email or cliente.email or "",
        active_nav="documentos",
    )


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
