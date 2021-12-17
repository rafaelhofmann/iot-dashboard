import configuration
import time
import json
from mitemp_monitor2_poller import MiTempMonitor2Poller
import paho.mqtt.publish as publish

MQTT_TOPIC = "sensor/room"

mqtt_config = configuration.load_configuration("mqtt")
config = configuration.load_configuration("room_monitor")

poller = MiTempMonitor2Poller(mac=config["mac_address"])

while True:
    data = poller.fetch_values()
    print(data)
    publish.single(MQTT_TOPIC, json.dumps(data), hostname=mqtt_config["hostname"])
    time.sleep(config["refresh_intervall"])
