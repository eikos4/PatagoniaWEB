from flask_login import current_user

from app import db
from app.models import ActivityLog


def log_activity(accion, entidad_tipo, entidad_id=None, entidad_ref=None, detalle=None):
    """Registra una acción en el historial de operaciones."""
    user_id = current_user.id if current_user.is_authenticated else None
    entry = ActivityLog(
        user_id=user_id,
        accion=accion,
        entidad_tipo=entidad_tipo,
        entidad_id=entidad_id,
        entidad_ref=entidad_ref,
        detalle=detalle,
    )
    db.session.add(entry)
