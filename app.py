# render_template comes from "jinja"
from flask import Flask, render_template, request, redirect
from flask import url_for, flash, abort, session
from werkzeug.utils import secure_filename
import json
import os.path


# Passes env var name for app to initialize app
app = Flask(__name__)
app.secret_key = 'baQfF&gAXO)bC&k'


# Home Page
@app.route('/')
def home():
    # Renders home.html template for this route
    # Stores all sessions into variable "codes"
    # Passes variable "name" to template
	return render_template('home.html', codes=session.keys(), name="Eric")


# About Page
@app.route('/about')
def about():
    return "This will be a URL shortener"


# Redirect after shortening URL
@app.route('/your-url', methods=['GET','POST'])
def your_url():
    # Post requests
    if request.method == 'POST':
        # For storing all shortened URLs
        urlsDict = {}

        # Checking for existing url json file
        if os.path.exists('urls_list.json'):
            # Open URL json file
            with open('urls_list.json') as urls_file:
                # Loads existing URLs into url dictionary
                urlsDict = json.load(urls_file)
        
        # If URL name already exists, go back to home page
        if request.form['code'] in urlsDict.keys():
            flash("Name already taken, please select new name.")
            return redirect(url_for('home'))

        # If new URL name, continue
        else:
            # If request is for URL (form keys detects 'url')
            if 'url' in request.form.keys():
                # Retrieves name of input from home.html, stores in dict
                urlsDict[request.form['code']] = {'url':request.form['url']}
            # If request is for file (form keys detects 'file')
            else:
                # Gets file instance
                f = request.files['file']
                # Create name with shortname+filename, secure_filename for safety
                full_name = request.form['code'] + secure_filename(f.filename)
                # Saves file to uploads directory
                f.save(app.root_path + '/static/user_uploads/' + full_name)
                # Stores file into dictionary
                urlsDict[request.form['code']] = {'file':full_name}

            # Save/write to JSON
            with open('urls_list.json','w') as url_file:
                # Saves url dictionary to url file
                json.dump(urlsDict, url_file)
                # Save session (as cookie), session is dictionary of sessions
                # i.e. {code: True}
                session[request.form['code']] = True
            # User's entry to "shortname" gets saved into "nameInput"
            # Variable becomes available in your_url.html
            return render_template('your_url.html', nameInput=request.form['code'])
    # Non-Post requests    
    else:
        return redirect(url_for('home'))


# For accessing (redirecting) the shortened URLs
# Assigns URL to a string variable called code
@app.route('/<string:code>')
def redirect_to_url(code):
    # Check to make sure url json file exists
    if os.path.exists('urls_list.json'):
        # open url json file
        with open('urls_list.json') as urls_file:
            # loads urls into variable
            urls = json.load(urls_file)
            # Check if URL exists in json url list
            # Checks all "first layer" keys, eg google, mask
            if code in urls.keys():
                # Make sure it's URL and not file upload
                # Checks "second layer" key for specified "code" (which is first layer key)
                if 'url' in urls[code].keys():
                    # Redirects to key's definition in dictionary
                    return redirect(urls[code]['url'])
                # If it's a file upload
                else:
                    # Redirects to name for uploaded file within static/user_uploads
                    return redirect(url_for('static', filename='user_uploads/' + urls[code]['file']))
    # 404 error if page not found
    return abort(404)


# 404 Error handler
@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404
