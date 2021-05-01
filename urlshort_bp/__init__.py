from flask import Flask
from flask_sqlalchemy import SQLAlchemy


# init SQLAlchemy so we can use it later in our models
db = SQLAlchemy()

def create_app(test_config=None):
	# Passes env var name for app to initialize app
	app = Flask(__name__)
	app.secret_key = 'baQfF&gAXO)bC&k'

	# Registers blueprint
	from . import urlshort_bp
	app.register_blueprint(urlshort_bp.bp)

	"""
	Auth+DB tutorial stuff
	
	app.config['SECRET_KEY'] = 'baQfF&gAXO)bC&k'
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