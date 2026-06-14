import os
import re
import uuid
import shutil

from werkzeug.utils import secure_filename
from flask import current_app


def slugify(text):
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    return text[:120] or "carpeta"


def unique_slug(base_slug, existing_slugs):
    slug = base_slug
    n = 1
    while slug in existing_slugs:
        slug = f"{base_slug}-{n}"
        n += 1
    return slug


def allowed_file(filename):
    if not filename or "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[-1].lower()
    return ext in current_app.config["ALLOWED_EXTENSIONS"]


def folder_disk_path(slug):
    return os.path.join(current_app.config["UPLOAD_FOLDER"], slug)


def save_client_file(file_storage, folder_slug):
    original = secure_filename(file_storage.filename or "archivo")
    if not original:
        original = "archivo"
    ext = original.rsplit(".", 1)[-1].lower() if "." in original else ""
    stored = f"{uuid.uuid4().hex}.{ext}" if ext else uuid.uuid4().hex
    dest_dir = folder_disk_path(folder_slug)
    os.makedirs(dest_dir, exist_ok=True)
    path = os.path.join(dest_dir, stored)
    file_storage.save(path)
    size = os.path.getsize(path)
    content_type = file_storage.mimetype or "application/octet-stream"
    return original, stored, size, content_type


def delete_stored_file(folder_slug, stored_filename):
    path = os.path.join(folder_disk_path(folder_slug), stored_filename)
    if os.path.isfile(path):
        os.remove(path)


def delete_folder_directory(slug):
    path = folder_disk_path(slug)
    if os.path.isdir(path):
        shutil.rmtree(path, ignore_errors=True)


def format_file_size(size_bytes):
    if size_bytes < 1024:
        return f"{size_bytes} B"
    if size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    return f"{size_bytes / (1024 * 1024):.1f} MB"
