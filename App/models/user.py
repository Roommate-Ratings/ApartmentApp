from werkzeug.security import check_password_hash, generate_password_hash
from App.database import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username =  db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    phone = db.Column(db.String(20), nullable=False, unique=True)
    role = db.Column(db.String(10), nullable=False)  # 'tenant' or 'landlord'


    def __init__(self, username, password):
        self.username = username
        self.set_password(password)

    def get_json(self):
        return{
            'id': self.id,
            'username': self.username
        }

    def set_password(self, password):
        """Create hashed password."""
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        """Check hashed password."""
        return check_password_hash(self.password, password)
    
class Tenant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref='tenant')

    def __init__(self, user_id):
        self.user_id = user_id

    def get_json(self):
        return {
            'id': self.id,
            'user': self.user.get_json()
        }
    
    def create_review(self, content, rating, apartment_id):
        """Create a new review."""
        new_review = Review(content, rating, self.user_id, apartment_id)
        db.session.add(new_review)
        db.session.commit()
        return new_review.get_json()
    
class Landlord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref='landlord')

    def __init__(self, user_id):
        self.user_id = user_id

    def get_json(self):
        return {
            'id': self.id,
            'user': self.user.get_json()
        }
    
    def create_apartment(self, address, city, state, zipcode, amenities):
        """Create a new apartment."""
        new_apartment = Apartment(address, city, state, zipcode, amenities, self.user_id)
        db.session.add(new_apartment)
        db.session.commit()
        return new_apartment.get_json()
    
    
class Apartment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    amenities = db.Column(db.Text) 
    landlord_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    landlord = db.relationship('User', backref='apartments')

    def get_json(self):
        return {
            'id': self.id,
            'address': self.address,
            'city': self.city,
            'amenities': self.amenities.split(',') if self.amenities else [],
            'landlord': self.landlord.username
        }

    def __init__(self, address, city, state, zipcode, amenities, landlord_id):
        self.address = address
        self.city = city
        self.amenities = amenities
        self.landlord_id = landlord_id


class ApartmentAmenity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    apartment_id = db.Column(db.Integer, db.ForeignKey('apartment.id'), nullable=False)
    amenity_id = db.Column(db.Integer, db.ForeignKey('amenity.id'), nullable=False)

    apartment = db.relationship('Apartment', backref='apartment_amenities')
    amenity = db.relationship('Amenity', backref='apartment_amenities')

    def get_json(self):
        return {
            'id': self.id,
            'apartment_id': self.apartment_id,
            'amenity_id': self.amenity_id
        }

class Amenity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)

    def get_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description
        }

    def __init__(self, name, description):
        self.name = name
        self.description = description


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.String(255), nullable=False)
    rating = db.Column(db.Integer, nullable=False) 
    date = db.Column(db.DateTime, default=db.func.current_timestamp())
    apartment_id = db.Column(db.Integer, db.ForeignKey('apartment.id'), nullable=False)
    tenant_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    tenant = db.relationship('User', backref='reviews')
    apartment = db.relationship('Apartment', backref='reviews')

    def get_json(self):
        return {
            'id': self.id,
            'rating': self.rating,
            'content': self.content,
            'tenant': self.tenant.username,
            'apartment_id': self.apartment_id,
            'created_at': self.created_at.isoformat()
        }
    
    def __init__(self, comment, rating, tenant_id, apartment_id):
        self.content = comment
        self.rating = rating
        self.tenant_id = tenant_id
        self.apartment_id = apartment_id




