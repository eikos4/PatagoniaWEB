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
MAX_CONTENT_LENGTH = 32 * 1024 * 1024  # 32 MB
ALLOWED_EXTENSIONS = {
    "pdf", "png", "jpg", "jpeg", "gif", "webp",
    "doc", "docx", "xls", "xlsx", "csv", "txt", "zip",
}
