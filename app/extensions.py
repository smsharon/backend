"""
For initializing the sqlAlchemy and migrate extensiuons the Flask application.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()
