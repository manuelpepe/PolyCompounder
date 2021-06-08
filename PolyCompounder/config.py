import json
from pathlib import Path

from PolyCompounder.exceptions import MissingConfig


RESOURCES = Path(__file__).parent / "resources"
ABIS_DIRECTORY = RESOURCES / "abis"

CONFIG_FILE = RESOURCES / "config.json" 
STRATEGIES_FILE = RESOURCES / "strategies.json"
CONTRACTS_FILE = RESOURCES / "contracts.json"

DEFAULT_KEYFILE = RESOURCES / "key.file"

if not CONFIG_FILE.is_file():
    raise MissingConfig(f"Config not found at {CONFIG_FILE}")

with CONFIG_FILE.open("r") as fp:
    cfg = json.load(fp) 
    ENDPOINT = cfg['endpoint']
    MY_ADDRESS = cfg['myAddress']

DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
