import json
from phue import Bridge
import configuration
import sys


def get_group_name_from_input():
    input_data = json.loads(sys.argv[1])
    input_group_name = input_data["name"]
    return input_group_name


def get_group_id_for_name(bridge, group_name):
    groups_raw = bridge.get_group()
    for group_key in groups_raw:
        group = groups_raw[group_key]
        if group["name"] == group_name:
            return {"group_id": int(group_key), "light_on": group["state"]["any_on"]}

    return None


hue_config = configuration.load_configuration("hue")

b = Bridge(ip=hue_config["bridge"], username=hue_config["username"])
b.connect()

group = get_group_id_for_name(b, get_group_name_from_input())
group_id = group["group_id"]
ligh_status = not group["light_on"]
b.set_group(group_id, "on", ligh_status)
