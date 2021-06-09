import json

from pathlib import Path
from contextlib import contextmanager

from PolyCompounder.config import ENDPOINT
from PolyCompounder.blockchain import Blockchain


class KeyfileOverrideException(Exception): pass


# To transform between the 'amount' unit and PZAP you need this UNIT_MULTIPLIER
#   AMOUNT = PZAP * UNIT_MULTIPLIER
#   20000000000000000 = 0.02 * 1000000000000000000
UNIT_MULTIPLIER = 1000000000000000000


def amountToPZAP(amount: int) -> str:
    return f"{amount / UNIT_MULTIPLIER:.8f}"


def amountToWBTC(amount: int) -> str:
    return f"{amount / 100000000:.8f}"


def amountToLPs(amount: int) -> str:
    return f"{amount / UNIT_MULTIPLIER:.25f}"


def PZAPToAmount(pzap: str) -> int:
    return int(float(pzap) * UNIT_MULTIPLIER)


def create_keyfile(path: Path, private_key: str, password: str):
    if path.is_file():
        raise KeyfileOverrideException("Warning, trying to overwrite existing keyfile")
    blockchain = Blockchain(ENDPOINT, 137, "POLYGON")
    keydata = blockchain.w3.eth.account.encrypt(private_key, password)
    with path.open("w") as fp:
        json.dump(keydata, fp)