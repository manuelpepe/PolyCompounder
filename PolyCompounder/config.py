import json
from pathlib import Path

from PolyCompounder.exceptions import MissingConfig

DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'

RESOURCES = Path(__file__).parent / "resources"
ABIS_DIRECTORY = RESOURCES / "abis"

CONFIG_FILE = RESOURCES / "config.json" 
SAMPLE_CONFIG_FILE = RESOURCES / "config.sample.json" 
STRATEGIES_FILE = RESOURCES / "strategies.json"
CONTRACTS_FILE = RESOURCES / "contracts.json"

DEFAULT_KEYFILE = RESOURCES / "key.file"

if not CONFIG_FILE.is_file():
    with CONFIG_FILE.open("w") as cfg, SAMPLE_CONFIG_FILE.open("r") as sample:
        cfg.write(sample.read())

with CONFIG_FILE.open("r") as fp:
    _cfg = json.load(fp) 

ENDPOINT = _cfg['endpoint']
MY_ADDRESS = _cfg['myAddress']

_EMAIL_CONFIG = _cfg.get("emails", {})

ALERTS_ON = _EMAIL_CONFIG.get("enabled", False)
ALERTS_HOST = _EMAIL_CONFIG.get("host", "localhost")
ALERTS_PORT = _EMAIL_CONFIG.get("port", 587)
ALERTS_ADDRESS = _EMAIL_CONFIG.get("address", None)
ALERTS_PASSWORD = _EMAIL_CONFIG.get("password", None)
ALERTS_RECIPIENT = _EMAIL_CONFIG.get("recipient", None)
