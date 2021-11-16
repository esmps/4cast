""" Sign up a user """

import os, requests, json
from sqlalchemy.exc import IntegrityError
from dotenv import load_dotenv, find_dotenv
from forms import UserAddForm
from flask import render_template, redirect, flash
from models import db, User
from user_login_out.helper import do_login, fav_home_location

load_dotenv(find_dotenv())

WEATHER_BASE_URL = 'http://api.weatherapi.com/v1/'
FORECAST_WEATHER = 'forecast.json'
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')

def extendApp_signup(app):

    @app.route('/signup', methods=["GET", "POST"])
    def signup():
        """Handle user signup. """

        form = UserAddForm()

        if form.validate_on_submit():
            response = requests.get(f'{WEATHER_BASE_URL}{FORECAST_WEATHER}?key={WEATHER_API_KEY}&q={form.home_location.data}&days=5&aqi=no&alerts=no')
            res = response.json()
            if "No matching location found." in response.text:
                flash("No matching location, please try again!", "danger")
                return redirect('/signup')
            try:
                user = User.signup(
                    first_name=form.first_name.data,
                    last_name=form.last_name.data,
                    username=form.username.data,
                    password=form.password.data,
                    home_location=f'{res["location"]["name"]}, {res["location"]["region"]}',
                    c_or_f=form.c_or_f.data
                )
                db.session.commit()
                fav_home_location(response.text, user)
                db.session.commit()
            except IntegrityError:
                flash("Username already used", 'danger')
                return render_template('users/signup.html', form=form)
            do_login(user)
            return redirect("/")
        else:
            return render_template('users/signup.html', form=form)