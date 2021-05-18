from flask import Flask, Blueprint, json, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy
import uuid
from werkzeug.security import generate_password_hash, check_password_hash

from .urlshort_bp import bp
from .auth import auth
from .users import users
import os

# Allow use of .env.local file
from dotenv import load_dotenv

# Load .env.local file and specify relative path
load_dotenv(dotenv_path="./playground/.env.local") 


def create_app(test_config=None):
	# Passes env var name for app to initialize app
	app = Flask(__name__)
	app.secret_key = os.environ.get("SECRET_KEY", "")

	# SQL Config stuff
	app.config["SECRET_KEY"] = "mysecretkey"
	app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("SQLITE_URI", "")
	app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

	# init SQLAlchemy so we can use it later in our models
	db = SQLAlchemy(app)

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

	##############
	### ROUTES ###
	##############
	# Home
	@app.route('/', methods=['GET'])
	def home():
		return 'Hello World'

	# Returns all existing users
	@app.route('/user', methods=['GET'])
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
	@app.route('/user/<public_id>', methods=['GET'])
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

	@app.route('/user', methods=['POST'])
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

	@app.route('/user/<public_id>', methods=['PUT'])
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

	@app.route('/user/<public_id>', methods=['DELETE'])
	def delete(public_id):
		return ''
	

	###########################
	### BLUE PRINT REGISTER ###
	###########################
	app.register_blueprint(bp)
	app.register_blueprint(auth, url_prefix='/auth')
	app.register_blueprint(users)

	db.create_all()

	"""
	Auth+DB tutorial stuff
	
	app.config['SECRET_KEY'] = 'baQfF&gAXO)bC&k' g
    #app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'

	db.init_app(app)

	# blueprint for auth routes in our app
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # blueprint for non-auth parts of app
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
	"""

	return app

# app = create_app()
# db = SQLAlchemy(app)