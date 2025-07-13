import json
import os

CONFIG_FILE = 'secrets.json'

def load_auth_config():
    if not os.path.exists(CONFIG_FILE):
        raise FileNotFoundError(f"{CONFIG_FILE} does not exist.")
    
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

def save_auth_config(data: dict):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(data, f, indent=4)