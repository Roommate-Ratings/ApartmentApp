from App.database import db
from App.models.location import Location

class Listing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(20), nullable=False)
    description = db.Column(db.String(120), nullable=False)
    price = db.Column(db.Float, nullable=False)
    bedrooms = db.Column(db.Integer, nullable=False)
    bathrooms = db.Column(db.Integer, nullable=False)
    landlord_id = db.Column(db.Integer, db.ForeignKey('landlords.id'), nullable=False)
    image_url = db.Column(db.String(255), nullable=True)

    
    location = db.relationship('Location', backref='listing', uselist=False, lazy=True)

