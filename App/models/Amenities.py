from App.database import db
from App.models.listing import Listing

class Amenities(db.Model):
    __tablename__ = 'amenities'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)

    def __init__(self, name):
        self.name = name
      
    def get_json(self):
        return{
            'id': self.id,
            'name': self.name
        }