import os
from flask import Flask, render_template, flash, redirect, session, g
from functools import wraps
from flask_debugtoolbar import DebugToolbarExtension

from models import connect_db, User
from newsfeed.newsfeed import extendApp_newsfeed
from favoriting import *
from user_profile import *
from user_login_out import *
from location_info import *

CURR_USER_KEY = "curr_user"

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

app.debug = False
toolbar = DebugToolbarExtension(app)

connect_db(app)

######################################################
# Decorators

def verify_user_logged_in(function):
    """ Custom decorated to verify if user is logged in """

    @wraps(function)
    def wrapper(*args, **kwargs):
        if not g.user:
            flash("Access unauthorized.", "danger")
            return redirect("/")
        return function(*args, **kwargs)
    return wrapper

@app.errorhandler(404)
def page_not_found(e):
    """ Custom 404 page """

    return render_template('other/404.html'), 404

@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])
        return
    else:
        g.user = None

######################################################
# User Signup/Login/Logout

extendApp_signup(app)
extendApp_login(app)
extendApp_logout(app)

######################################################
# User profile

extendApp_view_profile(app)
extendApp_edit_profile(app)

######################################################
# Search locations/Homepage

extendApp_search(app)
extendApp_homepage(app)

######################################################
# Un/Favorite Locations

extendApp_unfavorite(app)
extendApp_favorite(app)

######################################################
# Climate Newsfeed

extendApp_newsfeed(app)

##############################################################################
# Turn off all caching in Flask
#   (useful for dev; in production, this kind of stuff is typically
#   handled elsewhere)
#
# https://stackoverflow.com/questions/34066804/disabling-caching-in-flask

@app.after_request
def add_header(req):
    """Add non-caching headers on every request."""

    req.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    req.headers["Pragma"] = "no-cache"
    req.headers["Expires"] = "0"
    req.headers['Cache-Control'] = 'public, max-age=0'
    return req