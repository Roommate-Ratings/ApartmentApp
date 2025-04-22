from .user import create_user
from .landlord import create_landlord
from .tenant import create_tenant
from App.database import db
from App.models.Landlord import Landlord
from flask import url_for
from App.models.Amenities import Amenities
from App.models.ListingAmenity import ListingAmenity
from App.models.rental import Rental
import random


def initialize():
    db.drop_all()
    db.create_all()

    # Create Bob as a tenant instead of a regular user
    bob = create_tenant('bob', 'bob@gmail.com', 'bobpass')

    # Create a landlord and a tenant
    jill = create_landlord("jill", "jill@gmail.com", "jillpass")
    mike = create_tenant("mike", "mike@gmail.com", "mikepass")

    # Create listings for the landlord
    apartment1 = jill.create_listing(
        title="Trincity Home",
        description="A nice apartment",
        price=1200,
        bedrooms=2,
        bathrooms=1,
        street="123 Main St",
        city="Trincity"
    )
    # Set image URL for apartment 1
    apartment1.image_url = "/static/uploads/apartment1.jpg"
    
    apartment2 = jill.create_listing(
        title="Arouca Penthouse",
        description="Another nice apartment",
        price=1500,
        bedrooms=3,
        bathrooms=2,
        street="456 Elm St",
        city="Arouca"
    )
    # Set image URL for apartment 2
    apartment2.image_url = "/static/uploads/apartment2.jpg"
    
    apartment3 = jill.create_listing(
        title="San Juan Villa",
        description="A spacious apartment",
        price=1800,
        bedrooms=4,
        bathrooms=3,
        street="789 Oak St",
        city="San Juan"
    )
    # Set image URL for apartment 3
    apartment3.image_url = "/static/uploads/apartment3.jpg"
    
    apartment4 = jill.create_listing(
        title="San Fernando Apartment",
        description="A cozy apartment",
        price=900,
        bedrooms=1,
        bathrooms=1,
        street="101 Pine St",
        city="San Fernando"
    )
    # Set image URL for apartment 4
    apartment4.image_url = "/static/uploads/apartment4.jpg"

    # Add the landlord and tenant to the session
    db.session.add(jill)
    db.session.add(mike)
    
    # Create amenities
    amenities_list = [
        "Air Conditioning", "Heating", "Washer/Dryer", "Dishwasher", 
        "Parking", "Gym", "Pool", "Balcony", "Pets Allowed", 
        "Furnished", "Wi-Fi", "Cable TV", "Security System"
    ]
    
    created_amenities = []
    for name in amenities_list:
        amenity = Amenities(name=name)
        db.session.add(amenity)
        created_amenities.append(amenity)
    
    # Commit to get IDs for the amenities
    db.session.commit()
    
    # Associate random amenities with each apartment
    apartments = [apartment1, apartment2, apartment3, apartment4]
    
    for apartment in apartments:
        # Randomly determine how many amenities to add (3-8)
        num_amenities = random.randint(3, 8)
        
        # Randomly select which amenities to add
        selected_amenities = random.sample(created_amenities, num_amenities)
        
        # Create associations between apartment and selected amenities
        for amenity in selected_amenities:
            listing_amenity = ListingAmenity(
                listing_id=apartment.id,
                amenity_id=amenity.id
            )
            db.session.add(listing_amenity)
    
    # Commit all changes to the database
    db.session.commit()
    
    # Create rental relationships for demo purposes
    # This allows the tenant 'mike' to leave reviews for apartment1
    rental1 = Rental(
        tenant_id=mike.id,
        listing_id=apartment1.id
    )
    
    # This allows the tenant 'bob' to leave reviews for apartment2 (Arouca Penthouse)
    rental2 = Rental(
        tenant_id=bob.id,
        listing_id=apartment2.id
    )
    
    db.session.add(rental1)
    db.session.add(rental2)
    db.session.commit()

