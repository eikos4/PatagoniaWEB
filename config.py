# config.py
import os

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


def _database_uri():
    url = os.environ.get("DATABASE_URL")
    if url:
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        return url
    return "sqlite:///" + os.path.join(BASE_DIR, "kodesk.db")


SQLALCHEMY_DATABASE_URI = _database_uri()
SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-in-production")
STORE_NAME = "Patagonia Sur SpA"
WHATSAPP_PHONE = os.environ.get("WHATSAPP_PHONE", "56920576206")
CONTACT_EMAIL = os.environ.get("CONTACT_EMAIL", "contacto@patagoniasur.cl")
COMPANY_ADDRESS = "Sur de Chile · Exportación a México --Perú--Colombia"
LOGO_FILENAME = "img/1.png"

UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads", "clientes")
DOCUMENTS_FOLDER = os.path.join(BASE_DIR, "uploads", "documentos")
TEMPLATES_FOLDER = os.path.join(BASE_DIR, "uploads", "plantillas")
CONTRACTS_FOLDER = os.path.join(BASE_DIR, "uploads", "contratos")
PRODUCTS_FOLDER = os.path.join(BASE_DIR, "uploads", "productos")

# SMTP para notificaciones (opcional)
SMTP_HOST = os.environ.get("SMTP_HOST", "")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USER = os.environ.get("SMTP_USER", "")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")
SMTP_FROM = os.environ.get("SMTP_FROM", CONTACT_EMAIL)
NOTIFY_EMAIL = os.environ.get("NOTIFY_EMAIL", CONTACT_EMAIL)
MAX_CONTENT_LENGTH = 32 * 1024 * 1024  # 32 MB
ALLOWED_EXTENSIONS = {
    "pdf", "png", "jpg", "jpeg", "gif", "webp",
    "doc", "docx", "xls", "xlsx", "csv", "txt", "zip",
}
