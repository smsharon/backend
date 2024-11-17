from flask import Flask
from models import db
app = Flask(__name__)

# Configure the database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db.init_app(app)

@app.route('/')
def home():
    return "Backend is running!"

if __name__ == "__main__":
    # Create database tables
    with app.app_context():
        db.create_all()

    app.run(debug=True)
