from flask import Blueprint, render_template, request, send_from_directory, jsonify, redirect, url_for, session, make_response, flash
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
from App.models.rental import Rental

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

@index_views.route('/submit-review', methods=['GET', 'POST'])
def add_review_page():
    # Handle GET requests (in case the form gets submitted accidentally as GET)
    if request.method == 'GET':
        return redirect(url_for('index_views.get_listing_page'))
        
    # For POST requests, continue with processing
    try:
        # Verify JWT but make it optional
        verify_jwt_in_request(optional=True)
        username = get_jwt_identity()
        user = User.query.filter_by(username=username).first() if username else None
        
        apt_id = request.form.get('apt_id')
        if not apt_id:
            flash("Missing apartment ID")
            return redirect(url_for('index_views.get_listing_page'))
            
        # Verify the apartment exists
        apartment = Listing.query.get(apt_id)
        if not apartment:
            flash("Apartment not found")
            return redirect(url_for('index_views.get_listing_page'))
        
        # Check if user is a tenant
        if not user:
            flash("Please log in to leave a review")
            return redirect(url_for('index_views.get_listing_page', apt_id=apt_id))
            
        if user.role != 'tenant':
            flash("Only tenants can leave reviews")
            return redirect(url_for('index_views.get_listing_page', apt_id=apt_id))
            
        comment = request.form.get('comment')
        rating = request.form.get('rating')
        
        # Check if the tenant has rented this apartment
        rental = Rental.query.filter_by(tenant_id=user.id, listing_id=apt_id).first()
        
        # Enforce that only tenants who have rented the apartment can leave reviews
        if not rental:
            flash(f"You can only review apartments you have rented.")
            return redirect(url_for('index_views.get_listing_page', apt_id=apt_id))
        
        # Use user's actual ID for the review
        review = Review(
            listing_id=apt_id,
            user_id=user.id,
            rating=int(rating),
            comment=comment
        )
        
        db.session.add(review)
        db.session.commit()
        
        flash("Review added successfully")
        return redirect(url_for('index_views.get_listing_page', apt_id=apt_id))
    except Exception as e:
        # Log the error (in a real app, you'd use a proper logger)
        print(f"Error submitting review: {str(e)}")
        flash(f"Error submitting review: {str(e)}")
        return redirect(url_for('index_views.get_listing_page'))

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

@index_views.route('/editproperty/<int:property_id>', methods=['GET', 'POST'])
@jwt_required()
def edit_property_page(property_id):
    # Get the listing from the database
    listing = Listing.query.get_or_404(property_id)
    
    # Check if the current user is the owner of the property
    username = get_jwt_identity()
    user = User.query.filter_by(username=username).first()
    
    if not user or user.role != 'landlord' or listing.landlord_id != user.id:
        return "Unauthorized: You can only edit your own properties", 401
    
    # Get all available amenities
    all_amenities = Amenities.query.all()
    
    # Get the amenities that this listing already has
    listing_amenity_ids = [la.amenity_id for la in ListingAmenity.query.filter_by(listing_id=property_id).all()]
    
    if request.method == 'POST':
        # Update listing with form data
        listing.title = request.form.get('propertyTitle')
        listing.price = float(request.form.get('price'))
        listing.description = request.form.get('description')
        listing.bedrooms = int(request.form.get('bedrooms', 0))
        listing.bathrooms = float(request.form.get('bathrooms', 0))
        
        # Update location info
        if listing.location:
            listing.location.street = request.form.get('address')
            listing.location.city = request.form.get('city')
        else:
            # Create a new location if it doesn't exist
            location = Location(
                street=request.form.get('address'),
                city=request.form.get('city'),
                state="",
                zip_code="",
                listing_id=listing.id
            )
            db.session.add(location)
        
        # Handle image upload if a new image is provided
        if 'image' in request.files and request.files['image'].filename != '':
            image_file = request.files['image']
            # Create uploads directory if it doesn't exist
            uploads_dir = os.path.join('App', 'static', 'uploads')
            os.makedirs(uploads_dir, exist_ok=True)
            
            # Secure the filename and save the file
            filename = secure_filename(image_file.filename)
            file_path = os.path.join(uploads_dir, filename)
            image_file.save(file_path)
            
            # Create a URL for the image
            listing.image_url = url_for('static', filename=f'uploads/{filename}')

        # Handle amenities
        # First remove all existing amenities
        ListingAmenity.query.filter_by(listing_id=property_id).delete()
        
        # Then add the new selections
        amenities = request.form.getlist('amenities')
        if amenities:
            for amenity_id in amenities:
                listing_amenity = ListingAmenity(
                    listing_id=listing.id,
                    amenity_id=int(amenity_id)
                )
                db.session.add(listing_amenity)
        
        db.session.commit()
        return redirect(url_for('index_views.get_listing_page', apt_id=listing.id))
        
    # For GET request, render the edit form with the current property data
    return render_template(
        'editproperty.html', 
        listing=listing, 
        all_amenities=all_amenities,
        listing_amenity_ids=listing_amenity_ids
    )

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
        # First, see if the query matches any amenity names
        matching_amenities = Amenities.query.filter(Amenities.name.ilike(f'%{query}%')).all()
        matching_amenity_ids = [amenity.id for amenity in matching_amenities]
        
        if matching_amenity_ids:
            # If we found matching amenities, find listings with those amenities
            listings_with_amenities = db.session.query(Listing.id).join(
                ListingAmenity, ListingAmenity.listing_id == Listing.id
            ).filter(
                ListingAmenity.amenity_id.in_(matching_amenity_ids)
            ).all()
            
            listing_ids_with_amenities = [listing_id for (listing_id,) in listings_with_amenities]
            
            # Search in title, description, location fields, AND include listings with matching amenities
            listings_query = listings_query.join(Listing.location).filter(
                db.or_(
                    Listing.title.ilike(f'%{query}%'),
                    Listing.description.ilike(f'%{query}%'),
                    Location.street.ilike(f'%{query}%'),
                    Location.city.ilike(f'%{query}%'),
                    Location.state.ilike(f'%{query}%'),
                    Location.zip_code.ilike(f'%{query}%'),
                    Listing.id.in_(listing_ids_with_amenities)
                )
            )
        else:
            # If no matching amenities, just search in the usual fields
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

@index_views.route('/register_tenant', methods=['GET', 'POST'])
@jwt_required()
def register_tenant():
    # Check if user is a landlord
    username = get_jwt_identity()
    user = User.query.filter_by(username=username).first()
    
    if not user or user.role != 'landlord':
        return "Unauthorized: Only landlords can register tenants", 401
    
    if request.method == 'POST':
        tenant_id = request.form.get('tenant_id')
        listing_id = request.form.get('listing_id')
        
        # Check if the listing belongs to this landlord
        listing = Listing.query.get(listing_id)
        if not listing or listing.landlord_id != user.id:
            return "Unauthorized: You can only register tenants for your own properties", 401
        
        # Check if the tenant exists and is actually a tenant
        tenant = User.query.get(tenant_id)
        if not tenant or tenant.role != 'tenant':
            return "Error: Invalid tenant selected", 400
        
        # Check if a rental already exists
        existing_rental = Rental.query.filter_by(
            tenant_id=tenant_id, 
            listing_id=listing_id,
            end_date=None  # Active rental
        ).first()
        
        if existing_rental:
            return "Error: This tenant is already registered for this property", 400
        
        # Create a new rental
        rental = Rental(
            tenant_id=tenant_id,
            listing_id=listing_id
        )
        
        db.session.add(rental)
        db.session.commit()
        
        return redirect(url_for('index_views.get_listing_page', apt_id=listing_id))
    
    # For GET request, show the registration form
    landlord_properties = Listing.query.filter_by(landlord_id=user.id).all()
    tenants = User.query.filter_by(role='tenant').all()
    
    return render_template(
        'register_tenant.html',
        properties=landlord_properties,
        tenants=tenants
    )

@index_views.route('/debug', methods=['GET'])
def debug_info():
    # Get all users and their roles
    users = User.query.all()
    user_info = []
    for user in users:
        user_info.append({
            'id': user.id,
            'username': user.username,
            'role': user.role
        })
    
    # Get all rental records
    rentals = Rental.query.all()
    rental_info = []
    for rental in rentals:
        apartment = Listing.query.get(rental.listing_id)
        tenant = User.query.get(rental.tenant_id)
        rental_info.append({
            'tenant_id': rental.tenant_id,
            'tenant_name': tenant.username if tenant else 'Unknown',
            'listing_id': rental.listing_id,
            'apartment_title': apartment.title if apartment else 'Unknown'
        })
    
    return jsonify({
        'users': user_info,
        'rentals': rental_info
    })

@index_views.route('/tenant-review-submission-secure', methods=['GET', 'POST'])
def submit_tenant_review():
    # Handle GET requests (in case the form gets submitted accidentally as GET)
    if request.method == 'GET':
        return redirect(url_for('index_views.get_listing_page'))
        
    # For POST requests, continue with processing
    try:
        # Verify JWT but make it optional
        verify_jwt_in_request(optional=True)
        username = get_jwt_identity()
        user = User.query.filter_by(username=username).first() if username else None
        
        apt_id = request.form.get('apt_id')
        if not apt_id:
            flash("Missing apartment ID")
            return redirect(url_for('index_views.get_listing_page'))
            
        # Verify the apartment exists
        apartment = Listing.query.get(apt_id)
        if not apartment:
            flash("Apartment not found")
            return redirect(url_for('index_views.get_listing_page'))
        
        # Check if user is a tenant
        if not user:
            flash("Please log in to leave a review")
            return redirect(url_for('index_views.get_listing_page', apt_id=apt_id))
            
        if user.role != 'tenant':
            flash("Only tenants can leave reviews")
            return redirect(url_for('index_views.get_listing_page', apt_id=apt_id))
            
        comment = request.form.get('comment')
        rating = request.form.get('rating')
        
        # Check if the tenant has rented this apartment
        rental = Rental.query.filter_by(tenant_id=user.id, listing_id=apt_id).first()
        
        # Enforce that only tenants who have rented the apartment can leave reviews
        if not rental:
            flash(f"You can only review apartments you have rented.")
            return redirect(url_for('index_views.get_listing_page', apt_id=apt_id))
        
        # Use user's actual ID for the review
        review = Review(
            listing_id=apt_id,
            user_id=user.id,
            rating=int(rating),
            comment=comment
        )
        
        db.session.add(review)
        db.session.commit()
        
        flash("Review added successfully")
        return redirect(url_for('index_views.get_listing_page', apt_id=apt_id))
    except Exception as e:
        # Log the error (in a real app, you'd use a proper logger)
        print(f"Error submitting review: {str(e)}")
        flash(f"Error submitting review: {str(e)}")
        return redirect(url_for('index_views.get_listing_page'))

@index_views.route('/delete_property/<int:property_id>', methods=['POST'])
@jwt_required()
def delete_property(property_id):
    # Get the listing from the database
    listing = Listing.query.get_or_404(property_id)
    
    # Check if the current user is the owner of the property
    username = get_jwt_identity()
    user = User.query.filter_by(username=username).first()
    
    if not user or user.role != 'landlord' or listing.landlord_id != user.id:
        flash("Unauthorized: You can only delete your own properties")
        return redirect(url_for('auth_views.my_properties'))
    
    try:
        # Delete all associated amenities first
        ListingAmenity.query.filter_by(listing_id=property_id).delete()
        
        # Delete all associated reviews
        Review.query.filter_by(listing_id=property_id).delete()
        
        # Delete all associated rental records
        Rental.query.filter_by(listing_id=property_id).delete()
        
        # Delete associated location
        if listing.location:
            db.session.delete(listing.location)
        
        # Delete the property image from the file system if it exists
        if listing.image_url and 'uploads' in listing.image_url:
            try:
                # Extract the filename from the URL
                image_path = os.path.join('App', 'static', listing.image_url.split('static/')[1])
                if os.path.exists(image_path):
                    os.remove(image_path)
            except Exception as e:
                print(f"Error removing image file: {e}")
        
        # Delete the listing itself
        db.session.delete(listing)
        db.session.commit()
        
        flash("Property successfully deleted")
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting property: {str(e)}")
        print(f"Error deleting property: {str(e)}")  # Add detailed error logging
    
    return redirect(url_for('auth_views.my_properties'))