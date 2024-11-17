from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Customer, Order
from datetime import datetime

api = Blueprint('api', __name__)

@api.route('/customers', methods=['POST'])
@jwt_required()  # Protect this endpoint with JWT
def add_customer():
    """
    Endpoint to add a new customer.
    Only accessible by authenticated users.
    """
    current_user = get_jwt_identity()  # Get the identity of the current user
    
    data = request.json
    customer = Customer(name=data['name'], code=data['code'])
    db.session.add(customer)
    db.session.commit()
    return jsonify({'message': 'Customer added'}), 201

@api.route('/orders', methods=['POST'])
@jwt_required()  # Protect this endpoint with JWT
def add_order():
    current_user = get_jwt_identity()
    data = request.json
    order = Order(item=data['item'], amount=data['amount'], time=datetime.utcnow(), customer_id=data['customer_id'])
    db.session.add(order)
    db.session.commit()
    return jsonify({'message': 'Order added'}), 201
