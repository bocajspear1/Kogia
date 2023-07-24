import json

def load_config(config_path):
    config_file = open(config_path, "r")
    config_data = json.loads(config_file.read())
    config_file.close()
    return config_data