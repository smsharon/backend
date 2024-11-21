"""
SMS Helper using Africa's Talking API.
"""

import africastalking
import os

# Initialize Africa's Talking
africastalking.initialize(
    os.getenv("AFRICASTALKING_USERNAME"),
    os.getenv("AFRICASTALKING_API_KEY")
)
sms = africastalking.SMS

def send_sms(message, phone_number):
    """
    Send SMS to the given phone number.
    """
    try:
        response = sms.send(message, [phone_number])
        return response
    except Exception as e:
        print(f"Failed to send SMS: {e}")
        raise
