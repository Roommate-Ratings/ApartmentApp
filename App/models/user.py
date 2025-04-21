from werkzeug.security import check_password_hash, generate_password_hash
from App.database import db
from App.models.listing import Listing  # Import the Apartment model


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # Role column

    type = db.Column(db.String(50))

    __mapper_args__ = {
        'polymorphic_identity': 'user',
        'polymorphic_on': type,
        'with_polymorphic': '*'
    }

    def __init__(self, username, email, password, role="tenant"):
        self.username = username
        self.email = email
        self.role = role
        self.set_password(password)

    def get_json(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role
        }

    def set_password(self, password):
        self.password = generate_password_hash(password) 
    def check_password(self, password):
        return check_password_hash(self.password, password) 
    
    def search_listings(self, term):
        return Listing.query.filter(
            (Listing.title.ilike(f'%{term}%')) |
            (Listing.description.ilike(f'%{term}%'))
        ).all()

