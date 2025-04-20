from App.database import  db
from App.models.location import Location


class Listing(db.Model):
    id = db.Column(db.Integer, primary_key=True)  
    title = db.Column(db.String(20), nullable=False)
    description = db.Column(db.String(120), nullable=False)
    price = db.Column(db.Float, nullable=False)
    bedrooms = db.Column(db.Integer, nullable=False)
    bathrooms = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  
    location = db.relationship('Location', back_populates='listing', uselist=False, lazy=True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
 

    def __init__(self, title, description, price, bedrooms, bathrooms, user_id, location):
        self.title = title
        self.description = description  
        self.price = price
        self.bedrooms = bedrooms
        self.bathrooms = bathrooms
        self.user_id = user_id  
        self.location = location


from App.models.ListingAmenity import ListingAmenity
