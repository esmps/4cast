# Edit profile

import os, requests, json
from dotenv import load_dotenv, find_dotenv
from flask import g, render_template, redirect, flash

from forms import EditProfileForm
from models import db, Location, User


load_dotenv(find_dotenv())

WEATHER_BASE_URL = 'http://api.weatherapi.com/v1/'
FORECAST_WEATHER = 'forecast.json'
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')

def extendApp_edit_profile(app):

    from app import verify_user_logged_in

    @verify_user_logged_in
    @app.route('/profile/edit', methods=["GET", "POST"])
    def edit_profile():
        """Update profile for current user."""
        
        form = EditProfileForm()
        user = g.user
        old_home_location = Location.query.filter(Location.user_id==user.id, Location.location==user.home_location).first()
        if form.validate_on_submit():
            response = requests.get(f'{WEATHER_BASE_URL}{FORECAST_WEATHER}?key={WEATHER_API_KEY}&q={form.home_location.data}&days=5&aqi=no&alerts=no')
            if "No matching location found." in response.text:
                flash("No matching location, please try again!", "danger")
                return redirect('/signup')

            user = User.authenticate(user.username,
                                    form.password.data)
        
            if user:
                user.first_name = form.first_name.data or user.first_name
                user.last_name = form.last_name.data or user.last_name
                user.username = form.username.data or user.username
                if form.home_location.data:
                    user.home_location = f'{response.json()["location"]["name"]}, {response.json()["location"]["region"]}'
                else:
                    user.home_location = user.home_location
                user.c_or_f = form.c_or_f.data or user.c_or_f
                db.session.add(user)
                db.session.commit()

                if form.home_location.data:
                    new_home_location = fav_home_location(response.text, user)
                    db.session.commit()

                    locations = user.locations
                    if old_home_location in locations:
                        g.user.locations = [location for location in locations if location != old_home_location]
                        db.session.delete(old_home_location)
                        db.session.commit()

                flash("Successfully updated profile!", "success")
                return redirect(f'/profile')
            flash("Invalid password.", "error")
        return render_template("/users/edit.html", form=form, user=user)
