"""
Defines the TransactionLog model to log changes in order states.
"""

from app.extensions import db
from datetime import datetime
from app.constants import TRANSACTION_ACTIONS

class TransactionLog(db.Model):
    """
    Model to log transaction actions like order state updates.
    """
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=True)
    reason = db.Column(db.String(255), nullable=True)

    @classmethod
    def log(cls, order_id, action, description=None, reason=None):
        """
        Log a transaction action for an order.
        """
        if action not in TRANSACTION_ACTIONS:
            raise ValueError(f"Invalid transaction action: {action}")
        description = description or TRANSACTION_ACTIONS[action]
        log = cls(action=action, description=description, order_id=order_id, reason=reason)
        db.session.add(log)
        db.session.commit()

    def __repr__(self):
        return f"<TransactionLog {self.id}, Action: {self.action}>"
