from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required , create_access_token, get_jwt_identity
from models import db, Customer, Order
from datetime import datetime

api = Blueprint('api', __name__)

@api.route('/login', methods=['POST'])
def login():
    """
    Login endpoint for customers. If the customer doesn't exist, a new one is created.
    """
    data = request.json
    username = data.get('username')
    code = data.get('code')  # Unique code for each customer

    if not username or not code:
        return jsonify({"msg": "Username and code are required"}), 400

    # Check if the customer already exists
    customer = Customer.query.filter_by(code=code).first()
    if not customer:
        # Create a new customer if they don't exist
        customer = Customer(name=username, code=code)
        db.session.add(customer)
        db.session.commit()

    # Generate a JWT token for the customer
    access_token = create_access_token(identity={"username": username, "code": code})
    return jsonify({"access_token": access_token, "msg": "Login successful"}), 200


@api.route('/orders', methods=['POST'])
@jwt_required()
def add_order():
    """
    Allow a logged-in customer to create an order.
    """
    # Get the logged-in customer's identity
    current_user = get_jwt_identity()
    customer = Customer.query.filter_by(code=current_user['code']).first()
    if not customer:
        return jsonify({"msg": "Customer not found"}), 404

    # Get order details from request
    data = request.json
    item = data.get('item')
    amount = data.get('amount')

    if not item or not amount:
        return jsonify({"msg": "Item and amount are required"}), 400

    # Create the order
    order = Order(
        item=item,
        amount=amount,
        time=datetime.utcnow(),
        customer_id=customer.id
    )
    db.session.add(order)
    db.session.commit()

    return jsonify({"msg": "Order created successfully"}), 201

#endpoint for customers to view their orders
@api.route('/orders', methods=['GET'])
@jwt_required()
def get_orders():
    current_user = get_jwt_identity()
    customer = Customer.query.filter_by(code=current_user['code']).first()
    if not customer:
        return jsonify({"msg": "Customer not found"}), 404

    orders = Order.query.filter_by(customer_id=customer.id).all()
    return jsonify([{"item": o.item, "amount": o.amount, "time": o.time} for o in orders]), 200
