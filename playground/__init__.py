from flask import Flask, Blueprint
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy

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
	app.secret_key = 'baQfF&gAXO)bC&k'

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

	# Registers blueprint
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