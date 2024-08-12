# chapa_cli/utils.py
import os
import json
import base64

CONFIG_FILE_PATH = os.path.expanduser("~/.chapa_cli_config.json")

def save_token(token):
    """Save the secret token to a config file."""
    config_data = {
        "token": base64.b64encode(token.encode("utf-8")).decode("utf-8")
    }
    with open(CONFIG_FILE_PATH, "w") as config_file:
        json.dump(config_data, config_file)

def load_token():
    """Load the secret token from the config file."""
    if os.path.exists(CONFIG_FILE_PATH):
        with open(CONFIG_FILE_PATH, "r") as config_file:
            config_data = json.load(config_file)
            token = base64.b64decode(config_data.get("token")).decode("utf-8")
            return token
    return None
