from flask import Flask
from flask_jwt_extended import JWTManager
from models import db
from routes import api
app = Flask(__name__)

# Configure the database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configure JWT authentication
app.config['JWT_SECRET_KEY'] = 'said8354'
jwt = JWTManager(app)  

# Initialize the database
db.init_app(app)

# Register the API routes blueprint
app.register_blueprint(api)

@app.route('/')
def home():
    return "Backend is running!"

if __name__ == "__main__":
    # Create database tables
    with app.app_context():
        db.create_all()

    app.run(debug=True)
