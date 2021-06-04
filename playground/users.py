from flask import Blueprint, json, request, jsonify, make_response
from flask.helpers import make_response
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import uuid, datetime, jwt
# Extensions
from playground.database import db
from playground import app

#print("KEY IS: " + app.config['SECRET_KEY'])

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
            # (worse) alternative of getting token via req args
            # token = request.args.get('token')
            # ^ URL = http://127.0.0.1:5000/route?token=eyasdfasdfasdfetcetc
        # If not token in header, return missing 401 message
        if not token:
            return jsonify({'message' : 'Token is missing!'}), 401
        # Uses jwt to decode token, checks for validity of decoded token
        try:
            # Stores decoded token (using secret key)
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            # Query db for user that the public id and token belongs to 
            current_user = User.query.filter_by(public_id=data['public_id']).first()
        except:
            # Try fails, returns invalid 401 message
            return jsonify({'message' : 'Token is invalid!'}), 401
        # Passes user back to route, along with function's args (I think)
        return f(current_user, *args, **kwargs)
    return decorated

###################
### USER ROUTES ###
###################
# User login
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
        return jsonify({'message' : 'Cannot perform that function, requires admin!'})
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
    # Ensure user is admin to access route
    if not current_user.admin:
        return jsonify({'message' : 'Cannot perform that function, requires admin!'})
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

# Creates new user
@users.route('/user', methods=['POST'])
@token_required
def create_user(current_user):
    # Ensure user is admin to access route
    if not current_user.admin:
        return jsonify({'message' : 'Cannot perform that function, requires admin!'})
    # Store request info into data
    # If erroring out, make sure request body is set to JSON
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
    # Ensure user is admin to access route
    if not current_user.admin:
        return jsonify({'message' : 'Cannot perform that function, requires admin!'})
    # Query for first public id match
    user = User.query.filter_by(public_id=public_id).first()
    # If specified user does not exist
    if not user:
        return jsonify({'message' : 'No user found!'})
    # Set user as admin
    user.admin = True
    db.session.commit()
    return jsonify({'message' : user.name + ' has been promoted'})

# Delete specific user
@users.route('/user/<public_id>', methods=['DELETE'])
@token_required
def delete(current_user, public_id):
    # Ensure user is admin to access route
    if not current_user.admin:
        return jsonify({'message' : 'Cannot perform that function, requires admin!'})
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
    

####################
### TO DO ROUTES ###
####################
# Retrieve list of to do items
@app.route('/todo', methods=['GET'])
@token_required
def get_all_todos(current_user):
    # Ensure user is admin to access route
    if not current_user.admin:
        return jsonify({'message' : 'Cannot perform that function, requires admin!'})
    # Query all todos, store in table to local access
    todos = Todo.query.all()
    # List of todos to output
    output = []
    # Loop through todos in todos table
    for todo in todos:
        # Dictionariy to store data of current todo
        todo_data = {}
        # Store each property (as specified from Todo class)
        todo_data['id'] =  todo.id
        todo_data['text'] =  todo.text
        todo_data['complete'] =  todo.complete
        todo_data['user_id'] =  todo.user_id
        # Append current todo to output list
        output.append(todo_data)
    return jsonify({'todos' : output})

# Retrieve specific to do item
@app.route('/todo/<todo_id>', methods=['GET'])
@token_required
def get_all_todo(current_user, todo_id):
    # Ensure user is admin to access route
    if not current_user.admin:
        return jsonify({'message' : 'Cannot perform that function, requires admin!'})
    # Query for todo item where the id matches the request todo_id
    # Also query for user_id from db to match current_user from token
    # ^ ensures that users wont query for other user's todo items
    todo = Todo.query.filter_by(id=todo_id, user_id=current_user.id).first()
    # If specified todo item does not exist
    if not todo:
        return jsonify({'message' : 'Todo does not exist!'})
    # If found, grab todo item property to return
    todo_data = {}
    todo_data['id'] =  todo.id
    todo_data['text'] =  todo.text
    todo_data['complete'] =  todo.complete
    todo_data['user_id'] =  todo.user_id
    return jsonify({'todo' : todo_data})

# Create a new to do
@app.route('/todo', methods=['POST'])
@token_required
def create_todo(current_user):
    # Store request info into data
    # force=True forces request body to be of type JSON 
    data = request.get_json(force=True)
    # Instantiate new todo item
    new_todo = Todo(text=data['text'], complete=False, user_id=current_user.id)
    # Add to db
    db.session.add(new_todo)
    db.session.commit()
    return jsonify({'message' : 'New todo item created!'})

# Mark to do item as complete
@app.route('/todo/<todo_id>', methods=['PUT'])
@token_required
def complete_todo(current_user, todo_id):
    # Ensure user is admin to access route
    if not current_user.admin:
        return jsonify({'message' : 'Cannot perform that function, requires admin!'})
    # Query for todo
    todo = Todo.query.filter_by(id=todo_id, user_id=current_user.id).first()
    # If specified todo item does not exist
    if not todo:
        return jsonify({'message' : 'Todo does not exist!'})
    # Set todo to complete
    todo.complete = True
    db.session.commit()
    return jsonify({'message' : 'Todo item has been completed!'})

# Delete specific to do
@app.route('/todo/<todo_id>', methods=['DELETE'])
@token_required
def delete_todo(current_user, todo_id):
    # Query db for matching id (to the req' todo_id)
    todo = Todo.query.filter_by(id=todo_id, user_id=current_user.id).first()
    # If specified user does not exist
    if not todo:
        return jsonify({'message' : 'Todo item not found!'})
    # Delete specified todo item
    db.session.delete(todo)
    db.session.commit()
    return jsonify({'message' : 'Todo item has been deleted.'})
