import json
import time
from phue import Bridge
import configuration

config = configuration.load_configuration("hue")

b = Bridge(config["bridge"])
b.connect()

while True:
    groups_raw = b.get_group()
    groups = []
    for group_key in groups_raw:
        group_obj = groups_raw[group_key]
        groups.append({"name": group_obj["name"], "state": group_obj["state"]["any_on"]})
    json_string = json.dumps(groups)
    print(json_string)
    time.sleep(config["refresh_intervall"])
