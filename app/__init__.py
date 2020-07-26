from flask import Flask, render_template, current_app, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
import os
import re
import logging

# Define the database object which is imported
# by modules and controllers
db = SQLAlchemy()

def task_details_for_markup(details):
    URLS_REGEX_PATTERN = r"(https?\:\/\/[\w/\-?=%.]+\.[\w/\+\-?=%.~&\[\]\#]+)"
    DECORATED_URL_FORMAT = '<a href="{}" target="_blank">{}</a>'
    decorated_fragments = []
    fragments = re.split(URLS_REGEX_PATTERN, details)
    for index, fragment in enumerate(fragments):
        if index % 2 == 1:
            decorated_fragments.append(DECORATED_URL_FORMAT.format(fragment, fragment))
        else:
            decorated_fragments.append(fragment)

    return "".join(decorated_fragments)

'''
setup_db(app)
    binds a flask application and a SQLAlchemy service
'''
def setup_db(app, database_path, track_modifications=False):
    if database_path:
        app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = track_modifications
    db.app = app
    db.init_app(app)

'''
create_app(test_config)
    creates the flask application
'''
def create_app(test_config=None):
    csrf = CSRFProtect()

    # Define the WSGI application object
    app = Flask(__name__)

    app.jinja_env.filters["task_details_for_markup"] = task_details_for_markup

    # Configurations
    app.config.from_object('config')
    app.config['CORS_HEADERS'] = 'Content-Type'
    csrf.init_app(app)

    if 'DATABASE_URL' in os.environ:
        database_path = os.environ['DATABASE_URL']
    else:
        database_path = None
    setup_db(app, database_path)
    CORS(app)#, resources={r"/calendar/*": {"origins": "*"}})

    # Import a module / component using its blueprint handler variable (mod_auth)
    from app.mod_auth.controllers import mod_auth as auth_module
    from app.mod_calendar.controllers import mod_calendar as calendar_module

    # Register blueprint(s)
    app.register_blueprint(auth_module)
    app.register_blueprint(calendar_module)

    # To avoid main_calendar_action below shallowing favicon requests and generating error logs
    @app.route("/favicon.ico")
    def favicon():
        send_from_directory(
            os.path.join("static", "ico"), "favicon.ico", mimetype="image/vnd.microsoft.icon",
        )

    # Create the Flask-Migrate object
    migrate = Migrate(app, db)

    return app

app = create_app()

# CORS Headers 
@app.after_request
def after_request(response):
   response.headers.add('Access-Control-Allow-Origin', '*')
   response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
   return response

# @app.after_request
# def after_request(response):
#     header = response.headers
#     header['Access-Control-Allow-Origin'] = '*'
#     header['Access-Control-Allow-Headers'] = 'Content-Type,Authorization,true'
#     header['Access-Control-Allow-Methods'] = 'GET,PUT,POST,PATCH,DELETE,OPTIONS'
#     header['Allow'] = 'GET,HEAD,PUT,POST,PATCH,DELETE,OPTIONS'
#     return response

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500
