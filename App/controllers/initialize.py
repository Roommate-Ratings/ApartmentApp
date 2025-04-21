from .user import create_user
from .landlord import create_landlord
from .tenant import create_tenant
from App.database import db


def initialize():
    db.drop_all()
    db.create_all()
    create_user('bob','bob@gmail.com','bobpass')
    jill=create_landlord("jill","jill@gmail.com","jillpass")
    mike=create_tenant("mike","mike@gmail.com","mikepass")
    apartment1 = jill.create_listing("Apartment 1", "A nice apartment", 1200, 2, 1, "123 Main St", "New York", "NY", "10001")
    apartment2 = jill.create_listing("Apartment 2", "Another nice apartment", 1500, 3, 2, "456 Elm St", "New York", "NY", "10002")
    apartment3 = jill.create_listing("Apartment 3", "A spacious apartment", 1800, 4, 3, "789 Oak St", "New York", "NY", "10003")
    apartment4 = jill.create_listing("Apartment 4", "A cozy apartment", 900, 1, 1, "101 Pine St", "New York", "NY", "10004")
    db.session.add(jill)
    db.session.add(mike)
    db.session.commit()

