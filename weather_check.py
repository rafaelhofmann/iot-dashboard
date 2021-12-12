from pyowm import OWM
import configuration
import json


def check_weather_for_rain(weather):
    if weather.rain:
        return True
    else:
        return False


config = configuration.load_configuration("weather_api")

owm = OWM(config["api_key"])
mgr = owm.weather_manager()


forecast = mgr.forecast_at_place(config["location"], "3h", limit=5).forecast
will_rain = any(check_weather_for_rain(weather) for weather in forecast)

json_string = json.dumps({"will_rain": will_rain})
print(json_string)
