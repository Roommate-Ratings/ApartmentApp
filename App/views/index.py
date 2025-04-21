from flask import Blueprint, redirect, render_template, request, send_from_directory, jsonify
from flask_jwt_extended import get_jwt_identity
from App.controllers import create_user, initialize
from App.models import Listing

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
    return render_template(
        'listings.html', 
        apartments=apartments
        )


@index_views.route('/addproperty', methods=['GET'])
def add_property_page():
    return render_template('addproperty.html')

@index_views.route('/init', methods=['GET'])
def init():
    initialize()
    return jsonify(message='db initialized!')

@index_views.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status':'healthy'})