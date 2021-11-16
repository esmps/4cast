import json
from flask import g


def get_daily_info(response):
    """ Create dir of daily weather data """

    response = json.loads(response)
    current = response["current"]
    astro = response["forecast"]["forecastday"][0]["astro"]
    daily_info = {
        "sunrise": astro["sunrise"],
        "sunset": astro["sunset"],
        "moonphase": astro["moon_phase"],
        "windspeed": current["wind_mph"],
        "winddir": current["wind_dir"],
        "humidity": current["humidity"],
        "feelslike_f": current["feelslike_f"],
        "feelslike_c": current["feelslike_c"],
        "visibility": current["vis_miles"],
        "uv": current["uv"],
        }
    return json.dumps(daily_info)

def get_hourly_data(response, temp_pref):
    """ Create dir of 12 hours of weather data """
    response = json.loads(response)
    hour_data = []
    curr_time = response["current"]["last_updated"]
    curr_hour = int(curr_time[11:13])
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
                    "curr_temp": response["forecast"]["forecastday"][0]["hour"][curr_hour][f"temp_{temp_pref}"],
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
                    "curr_temp": response["forecast"]["forecastday"][1]["hour"][hour][f"temp_{temp_pref}"],
                    "temp_icon": response["forecast"]["forecastday"][1]["hour"][hour]["condition"]["icon"]
            })
            hour += 1
    return json.dumps(hour_data)

def get_four_day_forecast(response, temp_pref):
    """ Get forecast information for next four days """

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
                "high_temp": data[f"maxtemp_{temp_pref}"],
                "low_temp": data[f"mintemp_{temp_pref}"],
                "temp_icon": data["condition"]["icon"]
        })
        i+=1
    return json.dumps(daily_data)