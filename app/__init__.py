from flask import Flask
import os
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import generate_csrf

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

    @app.context_processor
    def inject_csrf_token():
        return dict(csrf_token=generate_csrf)

    from .routes import main
    from .admin_routes import admin
    from .portal_routes import portal
    app.register_blueprint(main)
    app.register_blueprint(admin, url_prefix="/admin")
    app.register_blueprint(portal, url_prefix="/portal")

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    with app.app_context():
        from .models import AdminUser, ContactMessage, ClientFolder, ClientFile, Product, ClientAbono, Quotation, Order, Shipment, Country, CountryRequirement, ExportDocument, ShipmentCost, Contract, DocumentTemplate, ActivityLog, NotificationLog
        from .seed import seed_default_admin, seed_default_products, seed_default_countries

        seed_default_admin()
        seed_default_products()
        seed_default_countries()

    os.makedirs(app.config.get("DOCUMENTS_FOLDER", app.config["UPLOAD_FOLDER"]), exist_ok=True)
    os.makedirs(app.config.get("TEMPLATES_FOLDER", app.config["UPLOAD_FOLDER"]), exist_ok=True)
    os.makedirs(app.config.get("CONTRACTS_FOLDER", app.config["UPLOAD_FOLDER"]), exist_ok=True)
    os.makedirs(app.config.get("PRODUCTS_FOLDER", app.config["UPLOAD_FOLDER"]), exist_ok=True)

    return app
