from flask import Blueprint, json, request, jsonify, make_response
from flask.helpers import make_response
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import sqlalchemy
import uuid
import datetime
import jwt
import os
# Extensions
from .database import db
from .config import DevelopmentConfig

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
        token = jwt.encode({'public_id' : user.public_id, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, DevelopmentConfig.SECRET_KEY)
        # respond with token as json
        #return jsonify({'token' : token.decode('UTF-8')}) <- no need to decode apparently
        return jsonify({'token' : token})
    # if password incorrect, return 401
    return make_response('Could not verify', 401, {'WWW-Authenticate' : 'Basic realm="Login required"'})

# Returns all existing users
@users.route('/user', methods=['GET'])
def get_all_users():
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
def get_one_user(public_id):
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
def create_user():
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
def promote_user(public_id):
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
def delete(public_id):
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
    