import json
import time
from btlewrap.bluepy import BluepyBackend
from miflora.miflora_poller import MI_MOISTURE, MI_TEMPERATURE, MiFloraPoller
import paho.mqtt.publish as publish
import configuration

MQTT_TOPIC = "sensor/flower"

mqtt_config = configuration.load_configuration("mqtt")
config = configuration.load_configuration("flower")

poller = MiFloraPoller(mac=config["mac_address"], backend=BluepyBackend, retries=3)

while True:
    flower_data = {"temperature": poller.parameter_value(MI_TEMPERATURE), "moisture": poller.parameter_value(MI_MOISTURE)}
    publish.single(MQTT_TOPIC, json.dumps(flower_data), hostname=mqtt_config["hostname"])
    time.sleep(config["refresh_intervall"])
