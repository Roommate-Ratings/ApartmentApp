from App.database import db

class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    street = db.Column(db.String(120), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    state = db.Column(db.String(50), nullable=True)
    zip_code = db.Column(db.String(20), nullable=True)
    listing_id = db.Column(db.Integer, db.ForeignKey('listing.id'), nullable=False)
