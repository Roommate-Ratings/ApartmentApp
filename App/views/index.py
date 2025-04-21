from flask import Blueprint, render_template, request, send_from_directory, jsonify, redirect, url_for, session, make_response
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
import os
from werkzeug.utils import secure_filename

from App.database import db
from App.controllers import (
    initialize
)
from App.models import Listing, Landlord, User
from App.models.review import Review
from App.models.Amenities import Amenities
from App.models.ListingAmenity import ListingAmenity

index_views = Blueprint('index_views', __name__, template_folder='../templates')

@index_views.route('/', methods=['GET'])
def index_page():

    properties = [
        {
            'id': 1,
            'title': 'Cozy Apartment',
            'location': 'Downtown',
            'image_url': 'https://picsum.photos/id/1015/800/600',
            'description': 'A cozy apartment in the heart of the city, perfect for young professionals.'
        },
        {
            'id': 2,
            'title': 'Luxury Condo',
            'location': 'Uptown',
            'image_url': 'https://picsum.photos/id/1025/800/600',
            'description': 'Modern condo with high-end finishes and a great view of the city skyline.'
        },
        {
            'id': 3,
            'title': 'Suburban House',
            'location': 'Suburbs',
            'image_url': 'https://picsum.photos/id/1035/800/600',
            'description': 'A spacious house in a quiet neighborhood with a big backyard.'
        },
        {
            'id': 4,
            'title': 'Modern Loft',
            'location': 'Midtown',
            'image_url': 'https://picsum.photos/id/1045/800/600',
            'description': 'A trendy loft with an open floor plan and lots of natural light.'
        },
        {
            'id': 5,
            'title': 'Charming Studio',
            'location': 'Old Town',
            'image_url': 'https://picsum.photos/id/1055/800/600',
            'description': 'A compact and charming studio, ideal for students and singles.'
        }
    ]
    
    filter_type = request.args.get('filter', 'all')
    # Not filtering dummy data; just passing all properties.
    return render_template('home.html', properties=properties)



@index_views.route('/listings', methods=['GET'])
def get_listing_page():
    apartments = Listing.query.all()
    apt_id = request.args.get('apt_id')
    selected_apartment = Listing.query.get(apt_id) if apt_id else None
    
    # Get current user from JWT if available
    current_user = None
    try:
        # Try to verify JWT but don't fail if not present (optional=True)
        verify_jwt_in_request(optional=True)
        username = get_jwt_identity()
        if username:
            current_user = User.query.filter_by(username=username).first()
    except:
        # User is not logged in, continue without user info
        pass
        
    return render_template('listings.html', 
                          apartments=apartments, 
                          selected_apartment=selected_apartment,
                          current_user=current_user)

def add_review(apt_id, comment, rating):
    apartment = Listing.query.get(apt_id)
    if not apartment:
        return "Apartment not found", 404
    
    # Get current user id (assuming user is logged in)
    user_id = get_jwt_identity() if get_jwt_identity() else 1  # Default to user 1 if not logged in
    
    review = Review(
        listing_id=apt_id,
        user_id=user_id,
        rating=int(rating),
        comment=comment
    )
    
    db.session.add(review)
    db.session.commit()
    return True

@index_views.route('/addreview', methods=['POST'])
@jwt_required()
def add_review_page():
    # Get current user
    username = get_jwt_identity()
    user = User.query.filter_by(username=username).first()
    
    # Check if user is a tenant
    if not user or user.role != 'tenant':
        return "Unauthorized: Only verified tenants can leave reviews", 401
        
    apt_id = request.form.get('apt_id')
    comment = request.form.get('comment')
    rating = request.form.get('rating')
    
    # Use user's actual ID for the review
    review = Review(
        listing_id=apt_id,
        user_id=user.id,
        rating=int(rating),
        comment=comment
    )
    
    db.session.add(review)
    db.session.commit()
    
    return redirect(url_for('index_views.get_listing_page', apt_id=apt_id))

@index_views.route('/addproperty', methods=['GET', 'POST'])
@jwt_required()
def add_property_page():
    if request.method == 'POST':
        title = request.form.get('propertyTitle')
        address = request.form.get('address')
        city = request.form.get('city')
        state = request.form.get('state')
        zip_code = request.form.get('zipCode')
        price = float(request.form.get('price'))
        description = request.form.get('description')
        bedrooms = int(request.form.get('bedrooms', 0))
        bathrooms = float(request.form.get('bathrooms', 0))
        
        # Handle image upload
        image_url = None
        if 'image' in request.files:
            image_file = request.files['image']
            if image_file.filename != '':
                # Create uploads directory if it doesn't exist
                uploads_dir = os.path.join('App', 'static', 'uploads')
                os.makedirs(uploads_dir, exist_ok=True)
                
                # Secure the filename and save the file
                filename = secure_filename(image_file.filename)
                file_path = os.path.join(uploads_dir, filename)
                image_file.save(file_path)
                
                # Create a URL for the image
                image_url = url_for('static', filename=f'uploads/{filename}')

        username = get_jwt_identity()
        user = User.query.filter_by(username=username).first()
        
        if not user or user.role != 'landlord':
            return "Unauthorized", 401
            
        # Get the landlord object
        landlord = Landlord.query.get(user.id)
        
        if not landlord:
            return "Landlord record not found", 404

        listing = landlord.create_listing(
            title=title,
            description=description,
            price=price,
            bedrooms=bedrooms,
            bathrooms=bathrooms,
            street=address,
            city=city,
            state=state,
            zip_code=zip_code
        )
        
        # Set the image URL if an image was uploaded
        if image_url:
            listing.image_url = image_url
        
        # Handle amenities
        amenities = request.form.getlist('amenities')
        if amenities:
            for amenity_id in amenities:
                # Create a new ListingAmenity association
                listing_amenity = ListingAmenity(
                    listing_id=listing.id,
                    amenity_id=int(amenity_id)
                )
                db.session.add(listing_amenity)
        
        db.session.commit()

        return redirect(url_for('index_views.get_listing_page', apt_id=listing.id))

    # Make sure amenities exist before showing the form
    seed_amenities()
    return render_template('addproperty.html')


@index_views.route('/init', methods=['GET'])
def init():
    initialize()
    return jsonify(message='db initialized!')

@index_views.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status':'healthy'})

@index_views.route('/seed-amenities', methods=['GET'])
def seed_amenities():
    # Define default amenities if none exist
    if Amenities.query.count() == 0:
        default_amenities = [
            "Air Conditioning", "Heating", "Washer/Dryer", "Dishwasher", 
            "Parking", "Gym", "Pool", "Balcony", "Pets Allowed", 
            "Furnished", "Wi-Fi", "Cable TV", "Security System"
        ]
        
        for name in default_amenities:
            amenity = Amenities(name=name)
            db.session.add(amenity)
        
        db.session.commit()
        return jsonify(message="Default amenities seeded!")
    
    return jsonify(message="Amenities already exist!")

@index_views.route('/amenities', methods=['GET'])
def get_amenities():
    amenities = Amenities.query.all()
    return jsonify([amenity.get_json() for amenity in amenities])