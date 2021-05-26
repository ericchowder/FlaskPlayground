from flask import Blueprint, json, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
# Extensions
from .database import db

users = Blueprint('users', __name__)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    name = db.Column(db.String(50))
    password = db.Column(db.String(80))
    admin = db.Column(db.Boolean)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(50))
    complete = db.Column(db.Boolean)
    user_id = db.Column(db.Integer)

@users.route('/login')
def login():
    return 'login here!'

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
    