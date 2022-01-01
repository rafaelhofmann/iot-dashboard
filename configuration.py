import yaml
import os


base_path = os.path.dirname(os.path.realpath(__file__))


CONFIGURATION_FILE_PATH = os.path.join(base_path, "configuration.yaml")


def load_configuration(category):
    with open(CONFIGURATION_FILE_PATH, "r") as yaml_file:
        return yaml.safe_load(yaml_file)["iot_dashboard"][category]
