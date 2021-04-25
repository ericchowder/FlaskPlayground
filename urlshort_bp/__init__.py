from flask import Flask


def create_app(test_config=None):
	# Passes env var name for app to initialize app
	app = Flask(__name__)
	app.secret_key = 'baQfF&gAXO)bC&k'

	# Registers blueprint
	from . import urlshort_bp
	app.register_blueprint(urlshort_bp.bp)

	return app