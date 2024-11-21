"""
Defines the Order and OrderItem models.
"""

from app.extensions import db
from datetime import datetime


class Order(db.Model):
    """
    Order model representing customer orders.
    """
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    state = db.Column(db.String(20), default="DRAFT", nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    customer = db.relationship("Customer", backref="orders")

    def __repr__(self):
        return f"<Order {self.id}, State: {self.state}>"


class OrderItem(db.Model):
    """
    OrderItem model representing items in an order.
    """
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("order.id"), nullable=False)
    inventory_id = db.Column(db.Integer, db.ForeignKey("inventory.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

    order = db.relationship("Order", backref="items")

    def __repr__(self):
        return f"<OrderItem {self.id}, Order: {self.order_id}>"
