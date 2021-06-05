import json
from pathlib import Path

RESOURCES = Path(__file__).parent / "resources"
CONFIG_FILE = RESOURCES / "config.json" 
DEFAULT_KEYFILE = RESOURCES / "key.file"

with CONFIG_FILE.open("r") as fp:
    cfg = json.load(fp) 
    ENDPOINT = cfg['endpoint']
    MY_ADDRESS = cfg['myAddress']

DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
