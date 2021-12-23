from pyowm import OWM
import configuration
import json
import paho.mqtt.publish as publish
import time

mqtt_config = configuration.load_configuration("mqtt")
config = configuration.load_configuration("weather_api")

owm = OWM(config["api_key"])
mgr = owm.weather_manager()
reg = owm.city_id_registry()

location_coordinates = reg.locations_for(config["location"]["city"], country=config["location"]["country"])[0]

while True:
    forecast = mgr.one_call(lat=location_coordinates.lat, lon=location_coordinates.lon)

    forecasts = []
    for weather in forecast.forecast_daily[:3]:
        forecasts.append(
            {
                "date_unix": weather.reference_time("unix"),
                "date_formatted": weather.reference_time("date").strftime("%d.%m"),
                "min_emperature": weather.temperature("celsius").get("min", None),
                "max_temperature": weather.temperature("celsius").get("max", None),
                "status": weather.status,
                "detailed_status": weather.detailed_status,
            }
        )
        print(forecasts)
    publish.single(config["topic"], json.dumps(forecasts), hostname=mqtt_config["hostname"])
    time.sleep(config["refresh_intervall"])
