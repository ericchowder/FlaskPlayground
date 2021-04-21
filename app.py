# render_template comes from "jinja"
from flask import Flask, render_template, request, url_for
import json

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
        # For storing all shortened URLs
        urlsDict = {}
        # Retrieves name of input from home.html, stores in dict
        urls[request.form['code']] = {'url':request.form['url']}
        # Save/write to JSON
        with open('shortened_urls.json','w') as url_file:
            # Saves url dictionary to url file
            json.dump(urlsDict, url_file)
        # User's entry to "shortname" gets saved into "nameInput"
        # Variable becomes available in your_url.html
        return render_template('your_url.html', nameInput=request.form['code'])
    else:
        return redirect(url_for('home'))