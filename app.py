# render_template comes from "jinja"
from flask import Flask, render_template, request

# Passes env var name for app to initialize app
app = Flask(__name__)

# Home Page
@app.route('/')
def home():
    # Renders home.html template for this route
    # Passes variable "name" to template
	return render_template('home.html', name="Eric")

# About Page
@app.route('/about')
def about():
    return "This will be a URL shortener"

# Redirect after shortening URL
@app.route('/your-url', methods=['GET','POST'])
def your_url():
    if request.method == 'POST':
        # User's entry to "shortname" gets saved into "nameInput"
        # Variable becomes available in your_url.html
        return render_template('your_url.html', nameInput=request.form['code'])
    else:
        return "Get request not valid."