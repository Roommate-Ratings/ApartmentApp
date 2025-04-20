from App.database import db

class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    street = db.Column(db.String(120), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    state = db.Column(db.String(50), nullable=False)
    zip_code = db.Column(db.String(10), nullable=False)
    lat = db.Column(db.Float, nullable=True)
    lng = db.Column(db.Float, nullable=True)

    listing_id = db.Column(db.Integer, db.ForeignKey('listing.id'), nullable=False)
    listing = db.relationship('Listing', back_populates='location')

    def __init__(self, listing, street, city, state, zip_code, lat=None, lng=None):
        self.listing = listing
        self.street = street
        self.city = city
        self.state = state
        self.zip_code = zip_code
        self.lat = lat
        self.lng = lng
