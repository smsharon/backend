"""
Pytest configuration and test setup.
"""

import pytest
from app import create_app
from app.extensions import db
from flask_jwt_extended import create_access_token

@pytest.fixture
def app():
    """
    Creates a Flask app instance for testing.
    """
    app = create_app("app.config.DevelopmentConfig")
    with app.app_context():
        db.create_all() # Initialize a clean database
        yield app # Provide the app to the test
        db.drop_all() # Clean up the database after the test

@pytest.fixture
def client(app):
    """
    Provides a test client for the app.
    For simulating HTTP requests to the application.
    """
    return app.test_client()

@pytest.fixture
def auth_header():
    """
    Returns a valid authorization header for testing protected routes.
    """
    token = create_access_token(identity={"id": 1, "code": "C001"})
    return {"Authorization": f"Bearer {token}"}
