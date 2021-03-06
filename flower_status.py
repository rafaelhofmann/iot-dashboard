import json
import time
from btlewrap.bluepy import BluepyBackend
from miflora.miflora_poller import MI_MOISTURE, MI_TEMPERATURE, MI_LIGHT, MiFloraPoller
import paho.mqtt.publish as publish
import configuration

mqtt_config = configuration.load_configuration("mqtt")
config = configuration.load_configuration("flower")

poller = MiFloraPoller(mac=config["mac_address"], backend=BluepyBackend, retries=3)

while True:
    payload = {"temperature": poller.parameter_value(MI_TEMPERATURE), "moisture": poller.parameter_value(MI_MOISTURE), "light": poller.parameter_value(MI_LIGHT)}
    publish.single(config["topic"], json.dumps(payload), hostname=mqtt_config["hostname"])
    time.sleep(config["refresh_intervall"])
