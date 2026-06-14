import os
import sys

from app import create_app, db
from app.models import AdminUser

email = os.environ.get("ADMIN_EMAIL", "carlos@patagoniasur.cl")
password = os.environ.get("ADMIN_PASSWORD")
if not password:
    print("Define ADMIN_PASSWORD en las variables de entorno antes de ejecutar este script.")
    sys.exit(1)

ADMINS = [(email, password)]

app = create_app()

with app.app_context():
    for email, password in ADMINS:
        admin = AdminUser.query.filter_by(username=email).first()
        if admin:
            admin.set_password(password)
            print(f"Contraseña actualizada para {email}")
        else:
            admin = AdminUser(username=email)
            admin.set_password(password)
            db.session.add(admin)
            print(f"Admin creado: {email}")
    db.session.commit()
    print("Proceso terminado.")
