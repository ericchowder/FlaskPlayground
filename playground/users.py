from flask import Blueprint, json, request, jsonify, make_response
from flask.helpers import make_response
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import uuid, datetime, jwt
# Extensions
from playground.database import db
from playground import app

print("KEY IS: " + app.config['SECRET_KEY'])

# Initialize file as blueprint
users = Blueprint('users', __name__)

# SQL Config stuff
'''
users.config["SECRET_KEY"] = "mysecretkey"
users.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("SQLITE_URI", "")
users.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
'''

##########################
### CLASS DECLARATIONS ###
##########################
# Basic user properties
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    name = db.Column(db.String(50))
    password = db.Column(db.String(80))
    admin = db.Column(db.Boolean)

# Properties of todo tasks
class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(50))
    complete = db.Column(db.Boolean)
    user_id = db.Column(db.Integer)

# Decorator for checking token
# Function that gets decorated is passed in
def token_required(f):
    @wraps(f)
    # Decorator function(position args, keyword args)
    def decorated(*args, **kwargs):
        token = None
        # Check for x-access-token in request headers
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        # If not token in header, return missing 401 message
        if not token:
            return jsonify({'message' : 'Token is missing!'}), 401
        # Uses jwt to decode token, checks for validity of decoded token
        try:
            print("DECODE KEY: " + app.config['SECRET_KEY'])
            # Stores decoded token (using secret key)
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            print("DECODE KEY: " + app.config['SECRET_KEY'])
            print("data is: ", data)
            # Query db for user that the public id and token belongs to 
            current_user = User.query.filter_by(public_id=data['public_id']).first()
        except:
            # Try fails, returns invalid 401 message
            return jsonify({'message' : 'Token is invalid!'}), 401
        # Passes user back to route, along with function's args (I think)
        return f(current_user, *args, **kwargs)
    return decorated

##############
### ROUTES ###
##############
@users.route('/login')
def login():
    # Retrieve auth info from request
    auth = request.authorization
    # Ensure auth info complete
    if not auth or not auth.username or not auth.password:
        # Return 401 error with WWW-Authenticate header
        return make_response('Could not verify', 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})
    # Get user info (first user, there should only be 1 user anyways)
    user = User.query.filter_by(name=auth.username).first()
    # If no user in request, return 401
    if not user:
        return make_response('Could not verify', 401, {'WWW-Authenticate' : 'Basic realm="Login required"'})
    # Check password (user from db, auth from req)
    if check_password_hash(user.password, auth.password):
        # Create token
        # arg1: Use public id to not expose user's id
        # arg2: Set expiration - relative to utc time, currently set to +30min
        # arg3: Pass in secret key to encode token
        token = jwt.encode({'public_id' : user.public_id, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'], algorithm="HS256")
        print("ENCODE KEY: " + app.config['SECRET_KEY'])
        # respond with token as json
        #return jsonify({'token' : token.decode('UTF-8')}) <- no need to decode apparently
        return jsonify({'token' : token})
    # if password incorrect, return 401
    return make_response('Could not verify', 401, {'WWW-Authenticate' : 'Basic realm="Login required"'})

# Returns all existing users
@users.route('/user', methods=['GET'])
@token_required
def get_all_users(current_user):
    # Ensure user is admin to access route
    if not current_user.admin:
        return jsonify({'message' : 'Cannot perform that function!'})
    # Create a table of users to access
    users = User.query.all()
    # List of users to output
    output = []
    # Loop through users in users table
    for user in users:
        # Dictionary to store data of current user
        user_data = {}
        # Store each property (as specified from User class)
        user_data['public_id'] = user.public_id
        user_data['name'] = user.name
        user_data['password'] = user.password
        user_data['admin'] = user.admin
        # Append current user to output list
        output.append(user_data)
    return jsonify({'users' : output})

# Returns one specified user
@users.route('/user/<public_id>', methods=['GET'])
@token_required
def get_one_user(current_user, public_id):
    # Query for first public id match
    user = User.query.filter_by(public_id=public_id).first()
    # If specified user does not exist
    if not user:
        return jsonify({'message' : 'No user found!'})
    # If found, grab user poperty to return
    user_data = {}
    user_data['public_id'] = user.public_id
    user_data['name'] = user.name
    user_data['password'] = user.password
    user_data['admin'] = user.admin
    return jsonify({'user' : user_data})

@users.route('/user', methods=['POST'])
@token_required
def create_user(current_user):
    # Store request info into data
    data = request.get_json()
    # Hash new user's password (json request 'password' key)
    hashed_password = generate_password_hash(data['password'], method='sha256')
    # Instantiate new user
    new_user = User(public_id=str(uuid.uuid4()), name=data['name'], password=hashed_password, admin=False)
    # Add to db
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message' : 'New user created!'})

@users.route('/user/<public_id>', methods=['PUT'])
@token_required
def promote_user(current_user, public_id):
    # Query for first public id match
    user = User.query.filter_by(public_id=public_id).first()
    # If specified user does not exist
    if not user:
        return jsonify({'message' : 'No user found!'})
    # Set user as admin
    user.admin = True
    db.session.commit()
    return jsonify({'message' : user.name + ' has been promoted'})

@users.route('/user/<public_id>', methods=['DELETE'])
@token_required
def delete(current_user, public_id):
    # Query for first public id match
    user = User.query.filter_by(public_id=public_id).first()
    # If specified user does not exist
    if not user:
        return jsonify({'message' : 'No user found!'})
    name = user.name
    # Delete specified user
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message' : name + ' has been deleted.'})
    