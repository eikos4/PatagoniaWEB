import os
import uuid

from datetime import datetime
from werkzeug.utils import secure_filename
from flask import current_app

from app.models import Contract


def next_contrato_numero():
    year = datetime.utcnow().year
    prefix = f"CTR-{year}-"
    last = (
        Contract.query.filter(Contract.numero.like(f"{prefix}%"))
        .order_by(Contract.id.desc())
        .first()
    )
    if last:
        try:
            n = int(last.numero.split("-")[-1]) + 1
        except ValueError:
            n = 1
    else:
        n = 1
    return f"{prefix}{n:04d}"


def contracts_disk_path():
    return current_app.config["CONTRACTS_FOLDER"]


def save_contract_file(file_storage):
    original = secure_filename(file_storage.filename or "contrato")
    if not original:
        original = "contrato"
    ext = original.rsplit(".", 1)[-1].lower() if "." in original else ""
    stored = f"{uuid.uuid4().hex}.{ext}" if ext else uuid.uuid4().hex
    dest_dir = contracts_disk_path()
    os.makedirs(dest_dir, exist_ok=True)
    path = os.path.join(dest_dir, stored)
    file_storage.save(path)
    size = os.path.getsize(path)
    content_type = file_storage.mimetype or "application/octet-stream"
    return original, stored, size, content_type


def delete_contract_file(stored_filename):
    if not stored_filename:
        return
    path = os.path.join(contracts_disk_path(), stored_filename)
    if os.path.isfile(path):
        os.remove(path)


def contract_file_path(stored_filename):
    return os.path.join(contracts_disk_path(), stored_filename)


def sync_contrato_estado(contrato):
    """Actualiza estado según fechas de vencimiento."""
    if contrato.estado in ("cancelado", "renovado", "borrador"):
        return
    if not contrato.fecha_fin:
        return
    dias = contrato.dias_para_vencer
    if dias is not None and dias < 0:
        contrato.estado = "vencido"
    elif dias is not None and dias <= 30:
        contrato.estado = "por_vencer"
    elif contrato.estado in ("por_vencer", "vencido"):
        contrato.estado = "vigente"
