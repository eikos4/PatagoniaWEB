import os
import uuid

from werkzeug.utils import secure_filename
from flask import current_app


def products_disk_path():
    return current_app.config["PRODUCTS_FOLDER"]


def save_product_file(file_storage, prefix="prod"):
    original = secure_filename(file_storage.filename or "archivo")
    if not original:
        original = "archivo"
    ext = original.rsplit(".", 1)[-1].lower() if "." in original else ""
    stored = f"{prefix}_{uuid.uuid4().hex}.{ext}" if ext else f"{prefix}_{uuid.uuid4().hex}"
    dest_dir = products_disk_path()
    os.makedirs(dest_dir, exist_ok=True)
    path = os.path.join(dest_dir, stored)
    file_storage.save(path)
    return original, stored


def delete_product_file(stored_filename):
    if not stored_filename:
        return
    path = os.path.join(products_disk_path(), stored_filename)
    if os.path.isfile(path):
        os.remove(path)


def product_file_path(stored_filename):
    return os.path.join(products_disk_path(), stored_filename)
