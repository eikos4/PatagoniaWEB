import os
import uuid

from werkzeug.utils import secure_filename
from flask import current_app


def templates_disk_path():
    return current_app.config["TEMPLATES_FOLDER"]


def save_template_file(file_storage):
    original = secure_filename(file_storage.filename or "plantilla")
    if not original:
        original = "plantilla"
    ext = original.rsplit(".", 1)[-1].lower() if "." in original else ""
    stored = f"{uuid.uuid4().hex}.{ext}" if ext else uuid.uuid4().hex
    dest_dir = templates_disk_path()
    os.makedirs(dest_dir, exist_ok=True)
    path = os.path.join(dest_dir, stored)
    file_storage.save(path)
    size = os.path.getsize(path)
    content_type = file_storage.mimetype or "application/octet-stream"
    return original, stored, size, content_type


def delete_template_file(stored_filename):
    if not stored_filename:
        return
    path = os.path.join(templates_disk_path(), stored_filename)
    if os.path.isfile(path):
        os.remove(path)


def template_file_path(stored_filename):
    return os.path.join(templates_disk_path(), stored_filename)
