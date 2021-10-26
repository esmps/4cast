import os
import requests, json

from flask import Flask, render_template, request, flash, redirect, session, g
from functools import wraps
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError

from forms import UserAddForm, LoginForm, EditProfileForm
from models import db, connect_db, User, Location

CURR_USER_KEY = "curr_user"

app = Flask(__name__)

# Get DB_URI from environ variable (useful for production/testing) or,
# if not set there, use development local db.
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///4cast'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
toolbar = DebugToolbarExtension(app)

connect_db(app)

######################################################
# Decorators

def verify_user_logged_in(function):
    """ Verify if user is logged in """

    @wraps(function)
    def wrapper():
        if not g.user:
            flash("Access unauthorized.", "danger")
        return redirect("/")

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
# User signup/login/logout

def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id

def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Handle user signup. """

    form = UserAddForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                email=form.email.data,
                password=form.password.data,
                home_location=form.home_location.data,
                daily_emails=form.daily_emails.data
            )
            db.session.commit()

        except IntegrityError:
            flash("Username already taken", 'danger')
            return render_template('users/signup.html', form=form)

        do_login(user)

        return redirect("/")

    else:
        return render_template('users/signup.html', form=form)

@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.email.data,
                                 form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.email}!", "success")
            return redirect("/")

        flash("Invalid credentials.", 'danger')

    return render_template('users/login.html', form=form)

@app.route('/logout')
def logout():
    """Handle logout of user."""
    if g.user:
        do_logout()
        flash("Successfully logged out.", 'success')
        return redirect('/login')
    return redirect('/')

######################################################
# User profile

@verify_user_logged_in
@app.route('/profile')
def view_profile():
    return render_template('users/profile.html')

@app.route('/profile/edit', methods=["GET", "POST"])
def edit_profile():
    return


######################################################
# Locations

@app.route('/weather', methods=["GET", "POST"])
def get_weather():
    search = request.args.get('q')

    response = requests.get('http://api.weatherapi.com/v1/')

    # search for locations from API
    # if no matches, show error
    # if matches, show template with cards for locations with info


######################################################
# Homepage

@app.route('/')
def homepage():

    if g.user:
        user = User.query.get_or_404(g.user.id)
        locations = user.locations
        return render_template('users/homepage.html', locations=locations)
    else:
        return render_template('users/homepage.html')