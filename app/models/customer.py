"""
Defines the Customer model.
"""

from app.extensions import db
from datetime import datetime


class Customer(db.Model):
    """
    Customer model representing customers in the system.
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    code = db.Column(db.String(10), unique=True, nullable=False)
    phone_number = db.Column(db.String(15), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Customer {self.name}, Code: {self.code}>"
