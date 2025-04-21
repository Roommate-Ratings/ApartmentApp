from flask_jwt_extended import create_access_token, jwt_required, JWTManager, get_jwt_identity, verify_jwt_in_request

from App.models import User

def login(username, password):
  user = User.query.filter_by(username=username).first()
  if user and user.check_password(password):
    return create_access_token(identity=username)
  return None


def setup_jwt(app):
  jwt = JWTManager(app)

  # configure's flask jwt to resolve get_current_identity() to the corresponding user's ID
  @jwt.user_identity_loader
  def user_identity_lookup(identity):
    user = User.query.filter_by(username=identity).one_or_none()
    if user:
        return str(user.id)
    return None

  @jwt.user_lookup_loader
  def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    return User.query.get(identity)

  return jwt


# Context processor to make 'is_authenticated' available to all templates
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from App.models import User

def add_auth_context(app):
    @app.context_processor
    def inject_user():
        try:
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            current_user = User.query.get(user_id)
            is_authenticated = current_user is not None
            is_landlord = current_user.role == 'landlord' if current_user else False
            landlord_id = current_user.id if is_landlord else None
        except Exception as e:
            print(e)
            current_user = None
            is_authenticated = False
            is_landlord = False
            landlord_id = None

        return dict(
            is_authenticated=is_authenticated,
            current_user=current_user,
            is_landlord=is_landlord,
            landlord_id=landlord_id
        )
