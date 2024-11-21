"""
Constants used throughout the application.
"""

# Order states
DRAFT = "DRAFT"
SUBMITTED = "SUBMITTED"
APPROVED = "APPROVED"
REJECTED = "REJECTED"

# Transaction actions
TRANSACTION_ACTIONS = {
    "CREATE_ORDER": "Order created",
    "APPROVE_ORDER": "Order approved",
    #"CREATE_CUSTOMER": "Customer registered",
    "CUSTOMER_REGISTERED": "Customer registered",
}

# Inventory statuses
INVENTORY_STATUS = {
    "AVAILABLE": "AVAILABLE",
    "FEW_REMAINING": "FEW REMAINING",
    "OUT_OF_STOCK": "OUT OF STOCK",
}
