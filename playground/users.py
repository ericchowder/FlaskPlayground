from flask import Blueprint
from . import db

users = Blueprint('users', __name__)

@users.route('/getusers')
def login():
    return 'Users here!'