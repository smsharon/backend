from flask import Flask
from app.extensions import db, migrate
from app.extensions import db
from app.config import DevelopmentConfig
from app.routes.api import api
from flask_jwt_extended import JWTManager
from app.helpers.auth import init_oauth

def create_app(config_class=DevelopmentConfig):
    """
    Application factory for creating the Flask app.
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    JWTManager(app)
    init_oauth(app)

    # Register blueprints
    app.register_blueprint(api, url_prefix="/api")

    return app
