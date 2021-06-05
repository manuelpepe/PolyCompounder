import json
from pathlib import Path

CONFIG_FILE = Path(__file__).parent / "resources/config.json" 

with CONFIG_FILE.open("r") as fp:
    cfg = json.load(fp) 
    ENDPOINT = cfg['endpoint']
    MY_ADDRESS = cfg['myAddress']

DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
