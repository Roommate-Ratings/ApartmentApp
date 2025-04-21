from App.models import Landlord
from App.models import User
from App.models import db

def create_landlord(username, email, password):
    landlord = Landlord(username=username, email=email, password=password)
    db.session.add(landlord)
    db.session.commit()
    return landlord