from flask import Blueprint, render_template, request, send_from_directory, jsonify, redirect, url_for, session, make_response
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
import os
from werkzeug.utils import secure_filename

from App.database import db
from App.controllers import (
    initialize
)
from App.models import Listing, Landlord, User, Location
from App.models.review import Review
from App.models.Amenities import Amenities
from App.models.ListingAmenity import ListingAmenity

index_views = Blueprint('index_views', __name__, template_folder='../templates')

@index_views.route('/', methods=['GET'])
def index_page():
    # Get real properties from the database instead of hardcoded ones
    filter_type = request.args.get('filter', 'all')
    
    # Fetch properties from the database
    if filter_type == 'all':
        properties = Listing.query.all()
    else:
        # Add more filter logic here if needed
        properties = Listing.query.all()
    
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
            state="",  # Passing empty string for state
            zip_code=""  # Passing empty string for zip_code
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

@index_views.route('/search', methods=['GET'])
def search_listings():
    # Get search parameters
    query = request.args.get('query', '')
    bedrooms = request.args.get('bedrooms')
    bathrooms = request.args.get('bathrooms')
    min_price = request.args.get('min_price')
    max_price = request.args.get('max_price')
    amenities = request.args.getlist('amenities')
    
    # Start with all listings
    listings_query = Listing.query
    
    # Apply filters based on parameters
    if query:
        # Search in title, description, and location fields
        listings_query = listings_query.join(Listing.location).filter(
            db.or_(
                Listing.title.ilike(f'%{query}%'),
                Listing.description.ilike(f'%{query}%'),
                Location.street.ilike(f'%{query}%'),
                Location.city.ilike(f'%{query}%'),
                Location.state.ilike(f'%{query}%'),
                Location.zip_code.ilike(f'%{query}%')
            )
        )
    
    # Filter by bedrooms if specified
    if bedrooms:
        try:
            bedrooms = int(bedrooms)
            listings_query = listings_query.filter(Listing.bedrooms >= bedrooms)
        except (ValueError, TypeError):
            pass
    
    # Filter by bathrooms if specified
    if bathrooms:
        try:
            bathrooms = float(bathrooms)
            listings_query = listings_query.filter(Listing.bathrooms >= bathrooms)
        except (ValueError, TypeError):
            pass
    
    # Filter by price range if specified
    if min_price:
        try:
            min_price = float(min_price)
            listings_query = listings_query.filter(Listing.price >= min_price)
        except (ValueError, TypeError):
            pass
    
    if max_price:
        try:
            max_price = float(max_price)
            listings_query = listings_query.filter(Listing.price <= max_price)
        except (ValueError, TypeError):
            pass
    
    # Filter by amenities if specified
    if amenities:
        for amenity_id in amenities:
            try:
                amenity_id = int(amenity_id)
                # Join with ListingAmenity for each amenity
                listings_query = listings_query.join(
                    ListingAmenity, 
                    db.and_(
                        ListingAmenity.listing_id == Listing.id,
                        ListingAmenity.amenity_id == amenity_id
                    )
                )
            except (ValueError, TypeError):
                pass
    
    # Execute the query
    listings = listings_query.all()
    
    # Get all amenities for the advanced search form
    all_amenities = Amenities.query.all()
    
    # Render the search results template
    return render_template(
        'search_results.html', 
        listings=listings, 
        query=query,
        bedrooms=bedrooms,
        bathrooms=bathrooms,
        min_price=min_price,
        max_price=max_price,
        selected_amenities=amenities,
        all_amenities=all_amenities
    )