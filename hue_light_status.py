import json
import time
from phue import Bridge
import paho.mqtt.publish as publish
import configuration

mqtt_config = configuration.load_configuration("mqtt")
hue_config = configuration.load_configuration("hue")
hue_light_config = configuration.load_configuration("hue_light")

b = Bridge(ip=hue_config["bridge"], username=hue_config["username"])
b.connect()

while True:
    groups_raw = b.get_group()
    payload = []
    for group_key in groups_raw:
        group_obj = groups_raw[group_key]
        payload.append({"name": group_obj["name"], "state": group_obj["state"]["any_on"]})
    publish.single(hue_light_config["topic"], json.dumps(payload), hostname=mqtt_config["hostname"])
    time.sleep(hue_light_config["refresh_intervall"])
