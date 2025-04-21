from App.models.user import User
from App.database import db
from App.models.listing import Listing
from App.models.location import Location

class Landlord(User):
    __tablename__ = 'landlord'

    id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': 'landlord',
    }

    def __init__(self, username, email, password):
        User.__init__(self, username, email, password, role="landlord")

    def get_json(self):
      return {
        'id': self.id,
        'user': self.user.get_json()
      }  
    
    def create_listing(self, title, description, price, bedrooms, bathrooms, street, city, state, zip_code):
        location = Location(street=street, city=city, state=state, zip_code=zip_code)
        listing = Listing(title=title, description=description, price=price, bedrooms=bedrooms,
                          bathrooms=bathrooms, user_id=self.id, location=location)
        db.session.add(location)
        db.session.add(listing)
        db.session.commit()
        return listing