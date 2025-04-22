from App.database import db
from datetime import datetime

class Rental(db.Model):
    __tablename__ = 'rentals'
    
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    listing_id = db.Column(db.Integer, db.ForeignKey('listing.id'), nullable=False)
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.DateTime, nullable=True)  # NULL for active rentals
    
    # Relationships
    tenant = db.relationship('User', backref=db.backref('rentals', lazy='dynamic'))
    listing = db.relationship('Listing', backref=db.backref('rentals', lazy='dynamic'))
    
    def __init__(self, tenant_id, listing_id, start_date=None, end_date=None):
        self.tenant_id = tenant_id
        self.listing_id = listing_id
        self.start_date = start_date or datetime.utcnow()
        self.end_date = end_date
    
    def get_json(self):
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'listing_id': self.listing_id,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None
        } 