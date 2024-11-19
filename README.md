# Backend Challenge Application

This is a Flask-based backend application for managing customers and orders. The application uses SQLite for the database and Africa’s Talking API for sending SMS notifications.

## Features
- JWT-based authentication
- CRUD operations for customers and orders
- SMS notifications using Africa's Talking API
- Unit tests with pytest and coverage reporting
- CI/CD ready with GitHub Actions

## Requirements
- Python 3.8+
- SQLite
- Africa’s Talking API credentials

## Setup Instructions
1. Clone the repository:
   - git clone git@github.com:smsharon/backend.git
   - cd backend
2. Install dependancies:
   - pip install -r requirements.txt
3. Set up the database:
   - python -m flask db init
   - python -m flask db migrate
   - python -m flask db upgrade
4. Run the application:
   - python app/app.py
5. Run the tests:
   - pytest --cov=app tests/
## API Endpoints
- Authentication
   POST /login: Logs in a customer and returns a JWT token.
- Customers
   POST /customers: Adds a new customer (protected).
- Orders
   POST /orders: Adds a new order and sends an SMS notification (protected).
## Licence
- MIT




   
   
  
