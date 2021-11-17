""" Search location and get weather data """

import os, requests, json
from flask import g, render_template, redirect, flash, request

from .helpers import get_hourly_data, get_daily_info, get_four_day_forecast


WEATHER_BASE_URL = os.environ.get('WEATHER_BASE_URL')
FORECAST_WEATHER = 'forecast.json'
WEATHER_API_KEY = os.environ.get('WEATHER_API_KEY')

def extendApp_search(app):
    @app.route('/weather')
    def get_weather():
        """ View weather of searched location """

        search = request.args.get('q')
        if not search:
            flash("Please input a location", "danger")
            return redirect('/')
        if search:
            response = requests.get(f'{WEATHER_BASE_URL}{FORECAST_WEATHER}?key={WEATHER_API_KEY}&q={search}&days=5&aqi=no&alerts=no')
            if "No matching location found." in response.text:
                flash("No matching location, please try again!", "danger")
                return redirect('/')
            if g.user:
                hour_data = json.loads(get_hourly_data(response.text, g.user.c_or_f))
                four_day_data = json.loads(get_four_day_forecast(response.text, g.user.c_or_f))
                daily_info = json.loads(get_daily_info(response.text))
                locations = []
                location_names = []
                for location in g.user.locations:
                    locations.append(location)
                    location_names.append(location.location)
                return render_template('location.html', response=response.json(), locations=locations, location_names=location_names, hour_data=hour_data, four_day_data=four_day_data, daily_info=daily_info)
            else:
                hour_data = json.loads(get_hourly_data(response.text, "f"))
                four_day_data = json.loads(get_four_day_forecast(response.text, "f"))
                daily_info = json.loads(get_daily_info(response.text))
                return render_template('location.html', response=response.json(), hour_data=hour_data, four_day_data=four_day_data, daily_info=daily_info)
