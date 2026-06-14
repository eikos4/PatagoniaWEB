from functools import wraps

from flask import flash, redirect, url_for, request
from flask_login import current_user


def role_required(*roles):
    """Permite acceso si el usuario tiene uno de los roles indicados. CEO siempre pasa."""
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for("admin.login"))
            if current_user.rol == "ceo" or current_user.rol in roles:
                return f(*args, **kwargs)
            flash("No tienes permiso para esta acción.", "danger")
            return redirect(url_for("admin.dashboard"))
        return wrapped
    return decorator


def edit_required(f):
    """Bloquea escritura a usuarios de solo lectura."""
    @wraps(f)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for("admin.login"))
        if not current_user.puede_editar:
            flash("Tu cuenta es de solo lectura.", "danger")
            return redirect(request.referrer or url_for("admin.dashboard"))
        return f(*args, **kwargs)
    return wrapped
