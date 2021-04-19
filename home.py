from flask import Flask

# Passes env var name for app to initialize app
app = Flask(__name__)

@app.route('/')
def home():
	return "Welcome to Home Page!!"