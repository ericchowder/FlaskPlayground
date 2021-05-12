from flask import Blueprint

users = Blueprint('users', __name__)

@users.route('/getusers')
def login():
    return 'Users here!'