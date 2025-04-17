from werkzeug.security import generate_password_hash
from main import db
from models import Admin

def create_admin(username, password):
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
    new_admin = Admin(admin=username, password=hashed_password)
    db.session.add(new_admin)
    db.session.commit()
    print("Admin user created successfully!")

if __name__ == "__main__":
    from flask import Flask

    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///myproject.db"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    with app.app_context():
        db.create_all()  # Ensure the database and tables are created
        
        username = input("Enter admin username: ")
        password = input("Enter admin password: ")
        create_admin(username, password)
