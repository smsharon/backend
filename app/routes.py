from flask import Blueprint, request, jsonify
from models import db, Customer, Order
from datetime import datetime

api = Blueprint('api', __name__)

@api.route('/customers', methods=['POST'])
def add_customer():
    data = request.json
    customer = Customer(name=data['name'], code=data['code'])
    db.session.add(customer)
    db.session.commit()
    return jsonify({'message': 'Customer added'}), 201

@api.route('/orders', methods=['POST'])
def add_order():
    data = request.json
    order = Order(item=data['item'], amount=data['amount'], time=datetime.utcnow(), customer_id=data['customer_id'])
    db.session.add(order)
    db.session.commit()
    return jsonify({'message': 'Order added'}), 201
