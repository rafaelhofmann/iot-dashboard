import yaml


def load_configuration(category):
    with open('configuration.yaml', 'r') as yaml_file:
        return yaml.safe_load(yaml_file)['iot_dashboard'][category]
