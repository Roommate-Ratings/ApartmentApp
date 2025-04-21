from App.database import db

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    listing_id = db.Column(db.Integer, db.ForeignKey('listing.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.String(120), nullable=False)
    date = db.Column(db.DateTime, default=db.func.current_timestamp())

    listing = db.relationship('Listing', backref='reviews')
    tenant = db.relationship('User', primaryjoin="Review.user_id == User.id", backref='reviews')

    def __init__(self, listing_id, user_id, rating, comment):
        self.listing_id = listing_id
        self.user_id = user_id
        self.rating = rating
        self.comment = comment

    def get_json(self):
        return {
            'id': self.id,
            'listing_id': self.listing_id,
            'user_id': self.user_id,
            'rating': self.rating,
            'comment': self.comment,
            'date': self.date.isoformat()
        }
    