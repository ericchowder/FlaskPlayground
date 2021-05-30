from flask import Flask
import os

# Allow use of .env.local file
from dotenv import load_dotenv
# Load .env.local file and specify relative path
load_dotenv(dotenv_path="./playground/.env.local") 

# Passes env var name for app to initialize app
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "")

# Load Config based on environment
if app.config["ENV"] == "production":
	app.config.from_object('playground.config.ProductionConfig')
if app.config["ENV"] == "testing":
	app.config.from_object('playground.config.TestingConfig')
else: #Development
	app.config.from_object('playground.config.DevelopmentConfig')

'''
# SQL Config stuff
app.config["SECRET_KEY"] = "mysecretkey"
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("SQLITE_URI", "")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
'''


##############
### ROUTES ###
##############
# Home
@app.route('/', methods=['GET'])
def home():
	return 'Hello World'

from playground.database import db
from playground.urlshort_bp import bp
from playground.auth import auth
from playground.users import users

###########################
### BLUE PRINT REGISTER ###
###########################
app.register_blueprint(bp)
app.register_blueprint(auth, url_prefix='/auth')
app.register_blueprint(users)

from playground import test
print("HELLO: " + test.hello)

# init SQLAlchemy so we can use it later in our models
db.init_app(app)

with app.app_context():
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
