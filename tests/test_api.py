import pytest
from app import create_app
from app.extensions import db
from unittest.mock import patch
from app.helpers.sms import send_sms

# Models
from app.models.customer import Customer
from app.models.transaction import TransactionLog

# Fixtures for Flask App and Client
@pytest.fixture
def app():
    """Fixture to create and configure the Flask application for testing."""
    app = create_app()
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['TESTING'] = True
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Fixture to create a test client."""
    return app.test_client()


# Mock Fixtures for SMS and Logs
@pytest.fixture(autouse=True)
def mock_transaction_log(mocker):
    """Mock the TransactionLog.log() method for every test to prevent database operations."""
    return mocker.patch('app.models.transaction.TransactionLog.log', autospec=True)


@pytest.fixture(autouse=True)
def mock_send_sms(mocker):
    """Mock the send_sms method to prevent sending actual SMS during tests."""
    return mocker.patch('app.routes.api.send_sms', autospec=True)

@pytest.fixture(autouse=True)
def reset_all_mocks(mock_transaction_log, mock_send_sms):
    """Reset mocks before every test."""
    mock_transaction_log.reset_mock()
    mock_send_sms.reset_mock()


# Tests

def test_register_customer(client, mock_transaction_log):
    """
    Test customer registration endpoint.
    """
    response = client.post("/api/register", json={
        "name": "John Doe",
        "code": "C001",
        "phone_number": "+254758793099"
    })

    # Assert the response status is 201 (Created)
    assert response.status_code == 201
    assert response.json["msg"] == "Customer registered successfully"

    # Verify log entry
    mock_transaction_log.assert_called_once_with(
        None, "Customer registered", "New customer John Doe registered."
    )


def test_register_customer_duplicate(client, mock_transaction_log):
    """
    Test duplicate customer registration.
    """
    # Register the first customer
    client.post("/api/register", json={
        "name": "John Doe",
        "code": "C001",
        "phone_number": "+254758793099"
    })

    # Register the same customer again
    response = client.post("/api/register", json={
        "name": "Jane Doe",
        "code": "C001",  # Duplicate code
        "phone_number": "+254758793098"
    })

    # Assert duplicate registration response
    assert response.status_code == 400
    assert "Customer code already exists" in response.json["msg"]

    # Ensure no additional logs were created for duplicate registration
    assert mock_transaction_log.call_count == 1


def test_login(client, mock_transaction_log):
    """
    Test customer login functionality.
    """
    # Register a customer
    client.post("/api/register", json={
        "name": "John Doe",
        "code": "C001",
        "phone_number": "+254758793099"
    })

    # Log in with valid credentials
    response = client.post("/api/login", json={
        "code": "C001",
        "phone_number": "+254758793099"
    })

    # Assert login success
    assert response.status_code == 200
    assert "access_token" in response.json

    # Verify log entry for login
    mock_transaction_log.assert_any_call(
        None, "Customer login", "Customer John Doe logged in."
    )


@pytest.mark.parametrize("phone_number,expected_code,expected_msg", [
    ("+254758793099", 200, None),  # Valid number
    ("invalidnumber", 400, "Invalid code or phone number")  # Invalid number
])
def test_login_invalid_phone_number(client, phone_number, expected_code, expected_msg, mock_transaction_log):
    """
    Test login with invalid phone numbers.
    """
    # Register a customer
    client.post("/api/register", json={
        "name": "John Doe",
        "code": "C001",
        "phone_number": "+254758793099"
    })

    # Attempt login
    response = client.post("/api/login", json={
        "code": "C001",
        "phone_number": phone_number
    })

    # Assert status code and message
    assert response.status_code == expected_code
    if expected_msg:
        assert expected_msg in response.json["msg"]

    # Check log behavior
    if expected_code == 200:
        mock_transaction_log.assert_any_call(
            None, "Customer login", "Customer John Doe logged in."
        )
    else:
        mock_transaction_log.assert_called_once()


def test_create_order(client, mock_transaction_log, mock_send_sms):
    """
    Test creating an order.
    """
    # Register and log in
    client.post("/api/register", json={
        "name": "John Doe",
        "code": "C001",
        "phone_number": "+254758793099"
    })
    token = client.post("/api/login", json={
        "code": "C001",
        "phone_number": "+254758793099"
    }).json["access_token"]

    # Create an order
    response = client.post("/api/orders", json={}, headers={"Authorization": f"Bearer {token}"})
    
    # Assert success
    assert response.status_code == 201
    assert "order_id" in response.json
    assert response.json["msg"] == "Order created successfully"
    
    # Verify log and SMS
    mock_transaction_log.assert_any_call(
        1, "Order created", "Order created by customer John Doe."
    )
    
    mock_send_sms.assert_called_once_with(
        "Hi John Doe, your order has been created successfully!",
        "+254758793099"
    )


def test_get_orders(client, mock_transaction_log):
    """
    Test retrieving customer orders.
    """
    # Register, log in, and create an order
    client.post("/api/register", json={
        "name": "John Doe",
        "code": "C001",
        "phone_number": "+254758793099"
    })
    token = client.post("/api/login", json={
        "code": "C001",
        "phone_number": "+254758793099"
    }).json["access_token"]
    client.post("/api/orders", json={}, headers={"Authorization": f"Bearer {token}"})

    # Retrieve orders
    response = client.get("/api/orders", headers={"Authorization": f"Bearer {token}"})

    # Assert success
    assert response.status_code == 200
    assert isinstance(response.json, list)


def test_approve_order(client, mock_transaction_log, mock_send_sms):
    """
    Test approving an order.
    """
    # Register, log in, and create an order
    client.post("/api/register", json={
        "name": "John Doe",
        "code": "C001",
        "phone_number": "+254758793099"
    })
    token = client.post("/api/login", json={
        "code": "C001",
        "phone_number": "+254758793099"
    }).json["access_token"]
    order_id = client.post("/api/orders", json={}, headers={"Authorization": f"Bearer {token}"}).json["order_id"]

    # Approve the order
    response = client.put(f"/api/orders/{order_id}/approve", headers={"Authorization": f"Bearer {token}"})

    # Assert success
    assert response.status_code == 200
    assert "Order approved successfully" in response.json["msg"]

    # Verify log and SMS
    mock_transaction_log.assert_any_call(
        1, "Order approved", f"Order {order_id} approved."
    )

    # Check that send_sms was called twice
    assert mock_send_sms.call_count == 2

    # Verify the first call (order creation)
    mock_send_sms.assert_any_call(
        "Hi John Doe, your order has been created successfully!", "+254758793099"
    )

    # Verify the second call (order approval)
    mock_send_sms.assert_any_call(
        f"Hi John Doe, your order {order_id} has been approved!", "+254758793099"
    )