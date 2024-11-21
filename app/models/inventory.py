"""
Defines the Inventory model for tracking inventory items.
"""

from app.extensions import db
from datetime import datetime

class Inventory(db.Model):
    """
    Inventory model representing items available for sale.
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    on_hand = db.Column(db.Integer, default=0, nullable=False)
    warn_limit = db.Column(db.Integer, default=5, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def get_status(self):
        """
        Returns the inventory status based on stock availability.
        """
        if self.on_hand == 0:
            return "OUT OF STOCK"
        elif self.on_hand <= self.warn_limit:
            return "FEW REMAINING"
        return "AVAILABLE"

    def __repr__(self):
        return f"<Inventory {self.name}, On Hand: {self.on_hand}>"
