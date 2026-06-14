from flask import Flask
import os
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()


def create_app():
    app = Flask(__name__)
    app.config.from_object("config")

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = "admin.login"

    from .routes import main
    from .admin_routes import admin
    app.register_blueprint(main)
    app.register_blueprint(admin, url_prefix="/admin")

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    with app.app_context():
        from .models import AdminUser, ContactMessage, ClientFolder, ClientFile, Product, ClientAbono, Quotation, Order, Shipment

    return app
