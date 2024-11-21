"""
API routes for handling customer registration, login, and order operations.
"""

from flask import Blueprint, request, jsonify, session, redirect, url_for
from app.helpers.auth import oauth
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from app.models.customer import Customer
from app.models.order import Order
from app.models.transaction import TransactionLog
from app.helpers.sms import send_sms
from app.extensions import db
from app.constants import TRANSACTION_ACTIONS

api = Blueprint("api", __name__)

@api.route("/login", endpoint="api_google_login")
def login():
    """
    Redirects to Google for authentication.
    """
    redirect_uri = url_for("api.api_google_auth", _external=True)
  # Use "api.auth" for Blueprint-based routing
    return oauth.google.authorize_redirect(redirect_uri)

@api.route("/auth", endpoint="api_google_auth")
def auth():
    """
    Handles the OpenID Connect callback.
    """
    token = oauth.google.authorize_access_token()
    user_info = oauth.google.parse_id_token(token)
    session['user'] = user_info

    # Check if user exists in the database
    user = Customer.query.filter_by(name=user_info["name"]).first()
    if not user:
        # Automatically register the user if not found
        user = Customer(name=user_info["name"], code="auto-code", phone_number="Unknown")
        db.session.add(user)
        db.session.commit()

    return jsonify(user_info)

@api.route("/register", methods=["POST"])
def register_customer():
    """
    Register a new customer with name, code, and phone number.
    """
    data = request.json
    name = data.get("name")
    code = data.get("code")
    phone_number = data.get("phone_number")

    if not all([name, code, phone_number]):
        return jsonify({"msg": "All fields are required"}), 400

    if Customer.query.filter_by(code=code).first():
        return jsonify({"msg": "Customer code already exists"}), 400

    customer = Customer(name=name, code=code, phone_number=phone_number)
    db.session.add(customer)
    db.session.commit()

    TransactionLog.log(None, TRANSACTION_ACTIONS["CUSTOMER_REGISTERED"], f"New customer {name} registered.")

    return jsonify({"msg": "Customer registered successfully"}), 201


@api.route("/login", methods=["POST"])
def login():
    """
    Log in a customer by verifying their code and phone number.
    Returns a JWT token if valid.
    """
    data = request.json
    code = data.get("code")
    phone_number = data.get("phone_number")

    if not all([code, phone_number]):
        return jsonify({"msg": "Code and phone number are required"}), 400

    customer = Customer.query.filter_by(code=code, phone_number=phone_number).first()

    if not customer:
        return jsonify({"msg": "Invalid code or phone number"}), 400

    token = create_access_token(identity={"id": customer.id, "code": customer.code})
    # Log the successful login
    TransactionLog.log(None, "Customer login", f"Customer {customer.name} logged in.")
    return jsonify({"access_token": token}), 200


@api.route("/orders", methods=["POST"])
@jwt_required()
def create_order():
    """
    Create a new order for the authenticated customer.
    """
    current_user = get_jwt_identity()
    customer = Customer.query.filter_by(id=current_user["id"]).first()

    if not customer:
        return jsonify({"msg": "Customer not found"}), 404

    order = Order(customer_id=customer.id)
    db.session.add(order)
    db.session.commit()

    TransactionLog.log(order.id, "Order created", f"Order created by customer {customer.name}.")

    # Ensure send_sms is called
    send_sms(
        f"Hi {customer.name}, your order has been created successfully!",
        customer.phone_number
    )

    return jsonify({"msg": "Order created successfully", "order_id": order.id}), 201


@api.route("/orders", methods=["GET"])
@jwt_required()
def get_orders():
    """
    Get all orders for the authenticated customer.
    """
    current_user = get_jwt_identity()
    customer = Customer.query.filter_by(id=current_user["id"]).first()

    if not customer:
        return jsonify({"msg": "Customer not found"}), 404

    orders = Order.query.filter_by(customer_id=customer.id).all()
    data = [{"id": order.id, "state": order.state, "created_at": order.created_at} for order in orders]

    return jsonify(data), 200


@api.route("/orders/<int:order_id>/approve", methods=["PUT"])
@jwt_required()
def approve_order(order_id):
    """
    Approve an order by updating its state to APPROVED.
    """
    current_user = get_jwt_identity()
    customer = Customer.query.filter_by(id=current_user["id"]).first()

    if not customer:
        return jsonify({"msg": "Customer not found"}), 404

    order = Order.query.filter_by(id=order_id, customer_id=customer.id).first()

    if not order:
        return jsonify({"msg": "Order not found"}), 404

    if order.state != "DRAFT":
        return jsonify({"msg": "Only DRAFT orders can be approved"}), 400

    order.state = "APPROVED"
    db.session.commit()

    TransactionLog.log(order.id, "Order approved", f"Order {order.id} approved.")

    # Ensure send_sms is called
    send_sms(
        f"Hi {customer.name}, your order {order.id} has been approved!",
        customer.phone_number
    )

    return jsonify({"msg": "Order approved successfully"}), 200
