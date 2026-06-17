"""Firmas digitales de documentos: token, trazabilidad y verificación."""

import re
import secrets
from datetime import datetime

from flask import request

from app import db
from app.models import DocumentSignature
from app.constants import FIRMA_PARTES

MAX_SIGNATURE_BYTES = 120_000


def _client_ip():
    forwarded = request.headers.get("X-Forwarded-For", "")
    if forwarded:
        return forwarded.split(",")[0].strip()[:64]
    return (request.remote_addr or "")[:64]


def generate_verification_token(document_id):
    return f"PS-{document_id:05d}-{secrets.token_hex(16).upper()}"


def get_firma(doc, parte):
    return DocumentSignature.query.filter_by(document_id=doc.id, parte=parte).first()


def document_signing_status(doc):
    exp = get_firma(doc, "exportador")
    imp = get_firma(doc, "importador")
    return {
        "exportador": exp,
        "importador": imp,
        "completo": bool(exp and imp),
        "pendiente_exportador": exp is None,
        "pendiente_importador": imp is None,
    }


def _validate_signature_image(data):
    if not data or not data.startswith("data:image/png;base64,"):
        return False, "Dibuja tu firma en el recuadro."
    raw = data.split(",", 1)[-1]
    if len(raw) > MAX_SIGNATURE_BYTES:
        return False, "La imagen de firma es demasiado grande."
    if len(raw) < 80:
        return False, "La firma está vacía o es inválida."
    return True, None


def register_document_signature(
    document,
    parte,
    signer_name,
    signer_email,
    signature_data,
    *,
    admin_user_id=None,
    client_folder_id=None,
    latitude=None,
    longitude=None,
    location_label=None,
):
    """Registra firma si no existe para esa parte. Retorna (firma, error)."""
    if parte not in FIRMA_PARTES:
        return None, "Parte de firma inválida."
    if get_firma(document, parte):
        return None, f"Este documento ya fue firmado por {FIRMA_PARTES[parte]}."

    ok, err = _validate_signature_image(signature_data)
    if not ok:
        return None, err

    name = (signer_name or "").strip()
    email = (signer_email or "").strip().lower()
    if not name or not email:
        return None, "Nombre y email del firmante son obligatorios."

    signed_at = datetime.utcnow()
    token = generate_verification_token(document.id)
    while DocumentSignature.query.filter_by(token=token).first():
        token = generate_verification_token(document.id)

    loc = (location_label or "").strip()[:300] or None
    if latitude is not None and longitude is not None and not loc:
        loc = f"{latitude:.5f}, {longitude:.5f}"

    firma = DocumentSignature(
        document_id=document.id,
        parte=parte,
        signer_name=name,
        signer_email=email,
        signature_data=signature_data,
        signed_at=signed_at,
        token=token,
        ip_address=_client_ip(),
        user_agent=(request.headers.get("User-Agent") or "")[:500],
        latitude=latitude,
        longitude=longitude,
        location_label=loc,
        admin_user_id=admin_user_id,
        client_folder_id=client_folder_id,
    )
    db.session.add(firma)
    return firma, None


def parse_geo_form(form):
    lat = form.get("latitude", type=float)
    lng = form.get("longitude", type=float)
    loc = (form.get("location_label") or "").strip()[:300]
    return lat, lng, loc or None


def firma_by_token(token):
    token = (token or "").strip().upper()
    if not re.match(r"^PS-\d{5}-[A-F0-9]{32}$", token):
        return None
    return DocumentSignature.query.filter_by(token=token).first()
