from App.models.user import User
from App.database import db
from App.models.listing import Listing
from App.models.location import Location

class Landlord(User):
    __tablename__ = 'landlords'

    id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    listings = db.relationship('Listing', backref='landlord', lazy=True)

    __mapper_args__ = {
        'polymorphic_identity': 'landlord',
    }

    def __init__(self, username, email, password):
        super().__init__(username=username, email=email, password=password)
        self.role = 'landlord' 

    def get_json(self):
      return {
        'id': self.id,
        'user': self.user.get_json()
      }  
    
    def create_listing(self, title, description, price, bedrooms, bathrooms, street, city, state="", zip_code=""):
        if not self.id:
            db.session.add(self)
            db.session.commit()

        listing = Listing(
            title=title,
            description=description,
            price=price,
            bedrooms=bedrooms,
            bathrooms=bathrooms,
            landlord_id=self.id
        )
        db.session.add(listing)
        db.session.commit()

        location = Location(
            street=street,
            city=city,
            state=state,
            zip_code=zip_code,
            listing_id=listing.id
        )
        db.session.add(location)
        db.session.commit()

        return listing

