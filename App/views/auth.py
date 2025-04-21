from sqlite3 import IntegrityError
from flask import Blueprint, render_template, jsonify, request, flash, send_from_directory, flash, redirect, url_for
from flask_jwt_extended import create_access_token, jwt_required, current_user, unset_jwt_cookies, set_access_cookies, get_jwt_identity

from App.controllers.user import get_all_users


from.index import index_views
from App.models import User, Landlord
from App.database import db

from App.controllers import (
    login,
    create_landlord, 
    create_tenant,   
    create_user       
)

auth_views = Blueprint('auth_views', __name__, template_folder='../templates')
index_views = Blueprint('index_views', __name__, template_folder='../templates')


'''
Page/Action Routes
'''    
@auth_views.route('/users', methods=['GET'])
def get_user_page():
    users = get_all_users()
    return render_template('users.html', users=users)

@auth_views.route('/identify', methods=['GET'])
@jwt_required()
def identify_page():
    return render_template('message.html', title="Identify", message=f"You are logged in as {current_user.id} - {current_user.username}")
    

@auth_views.route('/signup', methods=['GET'])
def signup_page():
    return render_template('signup.html')

@auth_views.route('/signup', methods=['POST'])
def signup_user_view():
    data = request.form
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    role = data.get('role')

    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        flash('Username already exists!')
        return render_template('signup.html') 

    try:
        if role == 'tenant':
            new_user = create_tenant(username, email, password)
            flash('New Tenant User Created!')
        elif role == 'landlord':
            new_user = create_landlord(username, email, password)
            flash('New Landlord User Created!')

        return render_template('home.html')

    except IntegrityError:
        db.session.rollback()
        flash("Signup failed. Please try again.")
        return render_template('signup.html')

@auth_views.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')


def login_user(username, password):
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        token = create_access_token(identity=username)
        response = redirect(url_for('index_views.index_page'))
        set_access_cookies(response, token)
        flash('Login Successful')
        
        return response

    flash('Bad username or password given')
    return render_template('login.html'), 401

@auth_views.route('/login', methods=['POST'])
def user_login_view():
    data = request.form
    response = login_user(data['username'], data['password'])
    if not response:
        return jsonify(message='bad username or password given'), 403
    return response

@auth_views.route('/logout', methods=['GET'])
def logout_action():
    response = redirect(request.referrer) 
    flash("Logged Out!")
    unset_jwt_cookies(response)
    return response

@auth_views.route('/myproperties')
@auth_views.route('/myproperties/<int:landlord_id>')
@jwt_required()
def my_properties(landlord_id=None):
    username = get_jwt_identity()
    user = User.query.filter_by(username=username).first()

    if not user or user.role != 'landlord':
        flash("You are not authorized to view this page.")
        return render_template('myproperties.html', is_authenticated=True, is_landlord=False, current_user=user, properties=[])

    # Use the provided landlord_id if available, otherwise use the current user's id
    landlord_id_to_use = landlord_id if landlord_id else user.id
    
    # Now safely cast or refetch as a Landlord if needed
    landlord = Landlord.query.get(landlord_id_to_use)
    if not landlord:
        flash("Landlord record not found.")
        return render_template('myproperties.html', is_authenticated=True, is_landlord=False, current_user=user, properties=[])

    return render_template(
        'myproperties.html',
        is_authenticated=True,
        is_landlord=True,
        current_user=landlord,
        properties=landlord.listings
    )



@auth_views.route('/search', methods=['GET'])
@jwt_required()
def search_page():
    username = get_jwt_identity() 
    user = User.query.filter_by(username=username).first()   
    search_term = request.args.get('query')
    results = user.search_listings(search_term)
    return render_template('search.html', user=user, results=results)

'''
API Routes
'''

@auth_views.route('/api/login', methods=['POST'])
def user_login_api():
  data = request.json
  token = login(data['username'], data['password'])
  if not token:
    return jsonify(message='bad username or password given'), 401
  response = jsonify(access_token=token) 
  set_access_cookies(response, token)
  return response

@auth_views.route('/api/identify', methods=['GET'])
@jwt_required()
def identify_user():
    return jsonify({'message': f"username: {current_user.username}, id : {current_user.id}"})

@auth_views.route('/api/logout', methods=['GET'])
def logout_api():
    response = jsonify(message="Logged Out!")
    unset_jwt_cookies(response)
    return response
