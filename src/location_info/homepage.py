""" Homepage for logged out and logged in users """

import os, requests, json
from flask import g, render_template
from dotenv import load_dotenv, find_dotenv

from models import User
from .helpers import get_daily_info, get_hourly_data, get_four_day_forecast

load_dotenv(find_dotenv())

WEATHER_BASE_URL = 'http://api.weatherapi.com/v1/'
FORECAST_WEATHER = 'forecast.json'
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')

def extendApp_homepage(app):
    @app.route('/')
    def homepage():
        """ Show search bar and if signed in, show favorite locations """

        if g.user:
            user = User.query.get_or_404(g.user.id)
            locations = user.locations
            location_data = []
            for location in locations:
                response = requests.get(f'{WEATHER_BASE_URL}{FORECAST_WEATHER}?key={WEATHER_API_KEY}&q={location.location}&days=5&aqi=no&alerts=no')
                hour_data = json.loads(get_hourly_data(response.text, g.user.c_or_f))
                four_day_data = json.loads(get_four_day_forecast(response.text, g.user.c_or_f))
                daily_info = json.loads(get_daily_info(response.text))
                location_data.append({
                    "id": location.id,
                    "res": response.json(),
                    "hour_data": hour_data,
                    "four_day_data": four_day_data,
                    "daily_info": daily_info
                })
            return render_template('/users/homepage.html', location_data=location_data)
        else:
            return render_template('users/homepage.html')