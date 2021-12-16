import json
import time
from phue import Bridge
import paho.mqtt.publish as publish
import configuration

MQTT_TOPIC = "sensor/hue"

mqtt_config = configuration.load_configuration("mqtt")
config = configuration.load_configuration("hue")

b = Bridge(ip=config["bridge"], username=config["username"])
b.connect()

while True:
    groups_raw = b.get_group()
    groups = []
    for group_key in groups_raw:
        group_obj = groups_raw[group_key]
        groups.append({"name": group_obj["name"], "state": group_obj["state"]["any_on"]})
    publish.single(MQTT_TOPIC, json.dumps(groups), hostname=mqtt_config["hostname"])
    time.sleep(config["refresh_intervall"])
