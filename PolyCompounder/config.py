import json
from pathlib import Path

from PolyCompounder.exceptions import MissingConfig


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
    cfg = json.load(fp) 
    ENDPOINT = cfg['endpoint']
    MY_ADDRESS = cfg['myAddress']

DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
