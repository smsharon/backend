from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required , create_access_token, get_jwt_identity
from app.models import db, Customer, Order
from datetime import datetime
import africastalking

# Initialize Africa's Talking
username = "sandbox"  
api_key = "atsk_0a9c45f231345f2dd0b72c5261d0670e224d903d41a1e7d2732dd843e13aa09594464bbe"   
africastalking.initialize(username, api_key)
sms = africastalking.SMS

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
    Allow a logged-in customer to create an order and send an SMS notification.
    """
    try:
        # Get the logged-in customer's identity
        current_user = get_jwt_identity()
        print("Authenticated user:", current_user)  # Debug log

        # Fetch customer from the database
        customer = Customer.query.filter_by(code=current_user['code']).first()
        if not customer:
            print("Customer not found:", current_user['code'])  # Debug log
            return jsonify({"msg": "Customer not found"}), 404

        # Parse and validate the order payload
        data = request.json
        print("Order request payload:", data)  # Debug log

        item = data.get('item')
        amount = data.get('amount')
        phone_number = data.get('phone_number')

        if not item or not amount or not phone_number:
            print("Validation failed. Missing fields in payload.")  # Debug log
            return jsonify({"msg": "Item, amount, and phone number are required"}), 400

        # Create and save the order
        order = Order(
            item=item,
            amount=amount,
            time=datetime.utcnow(),
            customer_id=customer.id
        )
        db.session.add(order)
        db.session.commit()
        print("Order created successfully.")  # Debug log

        # Send SMS notification
        try:
            message = f"Hi {customer.name}, your order for {item} worth ${amount} has been received!"
            print("Sending SMS with message:", message)  # Debug log
            sms_response = sms.send(message, [phone_number])
            print("SMS API response:", sms_response)  # Debug log
        except Exception as e:
            print(f"Error sending SMS: {e}")  # Debug log
            return jsonify({"msg": "Order created, but SMS could not be sent."}), 201

        return jsonify({"msg": "Order created successfully and SMS sent!"}), 201

    except Exception as e:
        print("Error processing order:", e)  # Debug log
        return jsonify({"msg": "Internal Server Error"}), 500
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
