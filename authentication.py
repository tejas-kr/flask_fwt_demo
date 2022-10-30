from flask import current_app, Blueprint, jsonify, render_template, request, make_response
from functools import wraps
import jwt
import re
import uuid

from .models import register_user

authentication = Blueprint('authentication', __name__, \
                            template_folder='templates/authentication', \
                            static_folder='static', url_prefix='/auth')

# Authentication decorator
# def token_required(f):
#     @wraps(f)
#     def decorator(*args, **kwargs):
#         token = None
#         # ensure the jwt-token is passed with the headers
#         if 'x-access-token' in request.headers:
#             token = request.headers['x-access-token']
#         if not token: # throw error if no token provided
#             return make_response(jsonify({"message": "A valid token is missing!"}), 401)
#         try:
#            # decode the token to obtain user public_id
#             data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
#             current_user = User.query.filter_by(public_id=data['public_id']).first()
#         except:
#             return make_response(jsonify({"message": "Invalid token!"}), 401)
#          # Return the user information attached to the token
#         return f(current_user, *args, **kwargs)
#     return decorator

def validate_username(username):
    sp_chars = '[@!#$%^&*()<>?/\|}{~:]'
    if any(c in sp_chars for c in username):
        return False
    return True

def validate_email(email):
    regex = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')
    if re.fullmatch(regex, email):
      return True
    else:
      return False

def validate_password(password):
    sp_chars = '[@_!#$%^&*()<>?/\|}{~:]'
    if len(password) < 8:
        return False, "Kindly use a 8+ character password"
    
    alpha = []
    num = []
    sp = []

    for c in password:
        if c.isalpha():
            alpha.append(c)
        elif c.isnumeric():
            num.append(c)
        elif c in sp_chars:
            sp.append(c)

    if len(alpha) == 0 or len(num) == 0 or len(sp) == 0:
        return False, "Password should contain Alphabets, Numbers and Special Symbols"
    
    return True, "Password Validated"

def validate_uuid(user_uuid):
    try:
        uuid.UUID(str(user_uuid))
        return True
    except ValueError:
        return False

def validate_mandatory_fields(req):
    if not req['username'] or not req['fname'] or not req['email'] or not req['password']:
        current_app.logger.error("Please enter all the feilds")
        return "Please enter all the feilds", 400
    
    if not validate_username(req['username']):
        current_app.logger.error("Only allowed special symbol is '_'")
        return "Only allowed special symbol is '_'", 400

    if not validate_email(req['email']):
        current_app.logger.error("Please enter a valid email")
        return "Please enter a valid email", 400

    val_pass, pass_msg = validate_password(req['password'])
    if not val_pass:
        current_app.logger.error(pass_msg)
        return pass_msg, 400

@authentication.route('/register', methods=['POST'])
def register():
    req = {
        'username': request.args.get('username'),
        'fname': request.args.get('fname'),
        'lname': request.args.get('lname'),
        'email': request.args.get('email'),
        'password': request.args.get('password'),
    }

    validate_mandatory_fields(req)

    count, result = register_user(req)

    if count == 1 and result[0] == req['username'] and validate_uuid(result[1]):
        current_app.logger.info(f"User has been registed with username: {result[0]} and user_uuid: {result[1]}")
        return f"User has been registed with username: {result[0]} and user_uuid: {result[1]}", 200

    current_app.logger.error("Unable to add user")
    return "Unable to add user", 400