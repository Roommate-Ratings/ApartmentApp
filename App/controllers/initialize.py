from .user import create_user
from .landlord import create_landlord
from .tenant import create_tenant
from App.database import db


def initialize():
    # Drop all tables and recreate them
    db.drop_all()
    db.create_all()

    # Create a regular user
    create_user('bob', 'bob@gmail.com', 'bobpass')

    # Create a landlord and a tenant
    jill = create_landlord("jill", "jill@gmail.com", "jillpass")
    mike = create_tenant("mike", "mike@gmail.com", "mikepass")

    # Create listings for the landlord
    apartment1 = jill.create_listing(
        title="Apartment 1",
        description="A nice apartment",
        price=1200,
        bedrooms=2,
        bathrooms=1,
        street="123 Main St",
        city="New York",
        state="NY",
        zip_code="10001"
    )
    apartment2 = jill.create_listing(
        title="Apartment 2",
        description="Another nice apartment",
        price=1500,
        bedrooms=3,
        bathrooms=2,
        street="456 Elm St",
        city="New York",
        state="NY",
        zip_code="10002"
    )
    apartment3 = jill.create_listing(
        title="Apartment 3",
        description="A spacious apartment",
        price=1800,
        bedrooms=4,
        bathrooms=3,
        street="789 Oak St",
        city="New York",
        state="NY",
        zip_code="10003"
    )
    apartment4 = jill.create_listing(
        title="Apartment 4",
        description="A cozy apartment",
        price=900,
        bedrooms=1,
        bathrooms=1,
        street="101 Pine St",
        city="New York",
        state="NY",
        zip_code="10004"
    )

    # Add the landlord and tenant to the session
    db.session.add(jill)
    db.session.add(mike)

    # Commit all changes to the database
    db.session.commit()

