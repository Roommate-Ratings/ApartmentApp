from App.database import db
from App.models.Amenities import Amenities
from App.models.listing import Listing

class ListingAmenity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    listing_id = db.Column(db.Integer, db.ForeignKey('listing.id'), nullable=False)
    amenity_id = db.Column(db.Integer, db.ForeignKey('amenities.id'), nullable=False)

    listing = db.relationship(Listing, backref=db.backref('amenities', lazy='dynamic'))
    amenity = db.relationship(Amenities, backref='listing_amenities')

    def __init__(self, listing_id, amenity_id):
        self.listing_id = listing_id
        self.amenity_id = amenity_id

    def get_json(self):
        return {
            'id': self.id,
            'listing_id': self.listing_id,
            'amenity_id': self.amenity_id
        }
