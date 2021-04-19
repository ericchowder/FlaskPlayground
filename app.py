# render_template comes from "jinja"
from flask import Flask, render_template

# Passes env var name for app to initialize app
app = Flask(__name__)

@app.route('/')
def home():
    # Renders home.html template for this route
    # Passes variable "name" to template
	return render_template('home.html', name="Eric")

@app.route('/about')
def about():
    return "This will be a URL shortener"