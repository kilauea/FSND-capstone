import sys
from functools import wraps
import json
from dotenv import load_dotenv, find_dotenv
import os
from os import environ as env
from werkzeug.exceptions import HTTPException
# Import flask dependencies
from flask import Blueprint, request, render_template, \
                  flash, g, session, redirect, url_for, \
                  current_app
import app.mod_auth.constants as constants
import app.mod_auth.auth as auth

__STORE_SESSION__ = False

# Define the blueprint: 'auth', set its url prefix: app.url/auth
mod_auth = Blueprint('auth', __name__, url_prefix='/auth')

if constants.AUTH0_CALLBACK_URL not in env:
    ENV_FILE = find_dotenv()
    if ENV_FILE:
        load_dotenv(ENV_FILE)

AUTH0_CALLBACK_URL = env.get(constants.AUTH0_CALLBACK_URL)
AUTH0_CLIENT_ID = env.get(constants.AUTH0_CLIENT_ID)
AUTH0_CLIENT_SECRET = env.get(constants.AUTH0_CLIENT_SECRET)
AUTH0_DOMAIN = env.get(constants.AUTH0_DOMAIN)
AUTH0_BASE_URL = 'https://' + AUTH0_DOMAIN
AUTH0_AUDIENCE = env.get(constants.AUTH0_AUDIENCE)

from authlib.integrations.flask_client import OAuth
from six.moves.urllib.parse import urlencode

oauth = OAuth(current_app)

auth0 = oauth.register(
    'auth0',
    client_id=AUTH0_CLIENT_ID,
    client_secret=AUTH0_CLIENT_SECRET,
    api_base_url=AUTH0_BASE_URL,
    access_token_url=AUTH0_BASE_URL + '/oauth/token',
    authorize_url=AUTH0_BASE_URL + '/authorize',
    client_kwargs={
    #    'scope': 'openid profile email get:calendars get:tasks'
    #}
        'scope': 'openid profile email',
    },
)

# Controllers API
@mod_auth.route('/callback/')
def callback_handling():
    try:
        # Handles response from token endpoint
        auth0.authorize_access_token()
        resp = auth0.get('userinfo')
        userinfo = resp.json()

        # Store the user information in flask session.
        session[constants.JWT_PAYLOAD] = userinfo
        session[constants.PROFILE_KEY] = {
            'user_id': userinfo['sub'],
            'name': userinfo['name'],
            'picture': userinfo['picture']
        }
        session[constants.JWT_TOKEN] = auth0.token['access_token']
        if __STORE_SESSION__:
            import pickle
            session_info = {}
            session_info[constants.JWT_PAYLOAD] = userinfo
            session_info[constants.PROFILE_KEY] = {
                'user_id': userinfo['sub'],
                'name': userinfo['name'],
                'picture': userinfo['picture']
            }
            session_info[constants.JWT_TOKEN] = auth0.token['access_token']
            pickle.dump(session_info, open(os.path.join(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, 'session.p')), 'wb'))
    except:
        session.clear()
        print("Unexpected error:", sys.exc_info()[0])
    return redirect('/calendar')

@mod_auth.route('/login')
def login():
    return auth0.authorize_redirect(audience=AUTH0_AUDIENCE, redirect_uri=AUTH0_CALLBACK_URL)

@mod_auth.route('/logout')
def logout():
    # Clear session stored data
    session.clear()
    # Redirect user to logout endpoint
    params = {'returnTo': url_for('index', _external=True), 'client_id': AUTH0_CLIENT_ID}
    return redirect(auth0.api_base_url + '/v2/logout?' + urlencode(params))

@mod_auth.route('/dashboard')
@auth.requires_auth()
def dashboard():
    return render_template('auth/dashboard.html',
                           userinfo=session[constants.PROFILE_KEY],
                           userinfo_pretty=json.dumps(session[constants.JWT_PAYLOAD], indent=4),
                           userperm_pretty=json.dumps(auth.verify_decode_jwt(session[constants.JWT_TOKEN]), indent=4))
