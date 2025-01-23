"""
Main entry point for the Flask application.
"""

from flask import Flask
from app.extensions import db, migrate
from app.config import DevelopmentConfig
from app.helpers.auth import init_oauth
from app.routes.api import api
from flask_jwt_extended import JWTManager
from app.models import Customer, Inventory, Order, OrderItem, TransactionLog  

def create_app(config_class=DevelopmentConfig):
    """
    Application factory for creating the Flask app.
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app) #Sets up SQLAlchemy with the Flask app.
    migrate.init_app(app, db) #Enables migration support for the database.
    JWTManager(app) #Configures JWT-based authentication for secure communication.
    init_oauth(app) #Initializes OIDC for handling external authentication providers



    # Register blueprints
    from app.routes.api import api
    app.register_blueprint(api, url_prefix="/api")

    return app


if __name__ == "__main__":
    app = create_app() # initializes and configures the Flask application.
    with app.app_context():
        db.create_all()
    app.run(debug=True)
