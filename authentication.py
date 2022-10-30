from flask import current_app, Blueprint, jsonify, render_template, request, make_response
from functools import wraps
import jwt
import re
import uuid
from datetime import datetime, timezone, timedelta

from .models import register_user, login_user, get_user_uuid

authentication = Blueprint('authentication', __name__, \
                            template_folder='templates/authentication', \
                            static_folder='static', url_prefix='/auth')

# Authentication decorator
def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None
        # ensure the jwt-token is passed with the headers
        current_app.logger.info(request.headers)

        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split()[1]
        
        if not token: # throw error if no token provided
            current_app.logger.error("A valid token is missing!")
            return make_response(jsonify({"message": "A valid token is missing!"}), 401)
        
        try:
           # decode the token to obtain user public_id
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = get_user_uuid(data['public_id'])[1][0][0]
        
        except:
            current_app.logger.error("Invalid token!")
            return make_response(jsonify({"message": "Invalid token!"}), 401)
        
        # Return the user information attached to the token
        return f(*args, **kwargs)
    
    return decorator

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

    try:
        count, result = register_user(req)

        if count == 1 and result[0] == req['username'] and validate_uuid(result[1]):
            current_app.logger.info(f"User has been registed with username: {result[0]} and user_uuid: {result[1]}")
            return f"User has been registed with username: {result[0]} and user_uuid: {result[1]}", 200
    except Exception as e:
        current_app.logger.error("Unable to add user: " + str(e))
        return "Unable to add user", 400

@authentication.route('/login', methods=['POST'])
def login():
    req = {
        'username': request.args.get("username"),
        'password': request.args.get("password")
    }
    
    if not req['username'] or not req['password']:
        current_app.logger.error("Please enter all the feilds")
        return "Please enter all the feilds", 400
    
    if not validate_username(req['username']):
        current_app.logger.error("Only allowed special symbol is '_'")
        return "Only allowed special symbol is '_'", 400

    val_pass, pass_msg = validate_password(req['password'])
    if not val_pass:
        current_app.logger.error(pass_msg)
        return pass_msg, 400

    try: 
        count, result = login_user(req)
        result = result[0]
        print(count, result)
        current_app.logger.info(f"{count}, {result}")

        if count == 1 and result[2] == req['username']:
            token = jwt.encode({'public_id': result[1], "exp": datetime.now(tz=timezone.utc) + timedelta(hours=2)}, current_app.config['SECRET_KEY'], 'HS256')
            current_app.logger.info(f"user: {result[2]} successfully authenticated")
            return make_response(jsonify({'token': token}), 201)

    except Exception as e:
        current_app.logger.error('Could not verify user!: ' + str(e))
        return make_response('Could not verify user!', 401, {'WWW-Authenticate': 'Basic-realm= "No user found!"'})



