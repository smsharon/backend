import pytest
from app.app import app
from app.models import db

# Test client fixture
@pytest.fixture
def client():
    #app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    #db.init_app(app)
    with app.app_context():
        db.create_all()
        yield app.test_client()
    #with app.app_context():
        db.drop_all()

# Test login functionality
def test_login(client):
    response = client.post('/login', json={"username": "joe goldberg", "code": "004"})
    assert response.status_code == 200
    assert "access_token" in response.json

# Test creating an order
def test_add_order(client):
    # Login to get a token
    login_response = client.post('/login', json={"username": "joe goldberg", "code": "004"})
    token = login_response.json["access_token"]

    # Add an order
    response = client.post(
    '/orders',
    json={"item": "watch", "amount": 1500, "phone_number": "+254758793099"},
    headers={"Authorization": f"Bearer {token}"}

)

    assert response.status_code == 201
    assert response.json["msg"] == "Order created successfully and SMS sent!"
