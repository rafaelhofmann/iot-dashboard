import configuration
import time
import json
from mitemp_monitor2_poller import MiTempMonitor2Poller
import paho.mqtt.publish as publish

mqtt_config = configuration.load_configuration("mqtt")
config = configuration.load_configuration("room_monitor")

poller = MiTempMonitor2Poller(mac=config["mac_address"])

while True:
    payload = poller.fetch_values()
    publish.single(config["topic"], json.dumps(payload), hostname=mqtt_config["hostname"])
    time.sleep(config["refresh_intervall"])
