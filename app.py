import os
import requests, json
import time

from flask import Flask, render_template, request, flash, redirect, session, g
from functools import wraps
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from dotenv import load_dotenv, find_dotenv

from forms import UserAddForm, LoginForm, EditProfileForm
from models import db, connect_db, User, Location

load_dotenv(find_dotenv())
WEATHER_BASE_URL = 'http://api.weatherapi.com/v1/'
CURRENT_WEATHER = 'current.json'
FORECAST_WEATHER = 'forecast.json'
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')
CURR_USER_KEY = "curr_user"

app = Flask(__name__)

# Get DB_URI from environ variable (useful for production/testing) or,
# if not set there, use development local db.
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///4cast'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
toolbar = DebugToolbarExtension(app)

connect_db(app)

######################################################
# Decorators

def verify_user_logged_in(function):
    """ Verify if user is logged in """
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

@app.route('/profile')
@verify_user_logged_in
def view_profile():
    user = g.user
    return render_template('users/profile.html', user=user)

@app.route('/profile/edit', methods=["GET", "POST"])
@verify_user_logged_in
def edit_profile():
    """Update profile for current user."""
    
    form = EditProfileForm()
    user = g.user
    if form.validate_on_submit():
        user = User.authenticate(user.email,
                                 form.password.data)
        if user:
            user.first_name = form.first_name.data or user.first_name
            user.last_name = form.last_name.data or user.last_name
            user.email = form.email.data or user.email
            user.home_location = form.home_location.data or user.home_location
            user.daily_emails = form.daily_emails.data or user.daily_emails
            db.session.add(user)
            db.session.commit()
            flash("Successfully updated profile!", "success")
            return redirect(f'/profile')
        flash("Invalid password.", "error")
    return render_template("/users/edit.html", form=form, user=user)

######################################################
# Locations

def get_hourly_data(response):
    """ Create dir of 12 hours of weather data """
    response = json.loads(response)
    hour_data = []
    curr_time = response["location"]["localtime_epoch"]
    curr_hour = int(time.strftime('%H', time.localtime(curr_time)))
    hour = 0
    for i in range(12):
        if curr_hour < 24:
            if curr_hour > 12:
                format_hour = curr_hour - 12
            else:
                format_hour = curr_hour 
            hour_data.append(  
                {
                    "hour": curr_hour,
                    "format_hour": format_hour,
                    "curr_temp": response["forecast"]["forecastday"][0]["hour"][curr_hour]["temp_f"],
                    "temp_icon": response["forecast"]["forecastday"][0]["hour"][curr_hour]["condition"]["icon"]
                })
            curr_hour += 1
        else:
            if hour == 0:
                format_hour = 12
            else:
                format_hour = hour
            hour_data.append(
                {
                    "hour": hour,
                    "format_hour": format_hour,
                    "curr_temp": response["forecast"]["forecastday"][1]["hour"][hour]["temp_f"],
                    "temp_icon": response["forecast"]["forecastday"][1]["hour"][hour]["condition"]["icon"]
            })
            hour += 1
    return json.dumps(hour_data)

def get_four_day_forecast(response):
    response = json.loads(response)
    days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    daily_data = []
    i = 1
    while i < 5:
        day = int(((int(response["forecast"]["forecastday"][i]["date_epoch"]) / 86400) + 4) % 7)
        data = response["forecast"]["forecastday"][i]["day"]
        daily_data.append(
            {   
                "date": response["forecast"]["forecastday"][i]["date"],
                "day": days[day],
                "high_temp": data["maxtemp_f"],
                "low_temp": data["mintemp_f"],
                "temp_icon": data["condition"]["icon"]
        })
        i+=1
    return json.dumps(daily_data)

@app.route('/weather')
def get_weather():
    """ View weather of searched location """

    search = request.args.get('q')
    if not search:
        search = "San Francisco, CA"
        flash("Please input a location", "danger")
        return redirect('/')
    if search:
        response = requests.get(f'{WEATHER_BASE_URL}{FORECAST_WEATHER}?key={WEATHER_API_KEY}&q={search}&days=5&aqi=no&alerts=no')
        if "No matching location found." in response.text:
            flash("No matching location, please try again!", "danger")
            return redirect('/')
        hour_data = json.loads(get_hourly_data(response.text))
        four_day_data = json.loads(get_four_day_forecast(response.text))
        print(four_day_data)
        return render_template('location.html', response=response.json(), hour_data=hour_data, four_day_data=four_day_data)
    # return render_template('response.html', response=response)



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