import json
import time
import requests
import paho.mqtt.publish as publish
import configuration


mqtt_config = configuration.load_configuration("mqtt")
hue_config = configuration.load_configuration("hue")
hue_motion_config = configuration.load_configuration("hue_motion")


def fetch_presence():
    response = requests.get("http://{}/api/{}/sensors/{}".format(hue_config["bridge"], hue_config["username"], hue_motion_config["motion_sensor_id"]))
    json_data = json.loads(response.text)
    return json_data["state"]["presence"]


while True:
    presence = fetch_presence()
    if presence == True:
        payload = {"presence_detected": True}
        publish.single(hue_motion_config["topic"], json.dumps(payload), hostname=mqtt_config["hostname"])
    time.sleep(hue_motion_config["refresh_intervall"])
