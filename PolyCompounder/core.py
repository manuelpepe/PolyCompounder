import getpass

from typing import List
from pathlib import Path

from web3 import Web3
from web3.middleware import geth_poa_middleware

from utils import *
from task import *
from config import ENDPOINT, MY_ADDRESS
from contract import ContractManager
from exceptions import *


_PARENT = Path(__file__).parent / "resources"
KEYFILE = _PARENT / "key.file"
POOL_ID = 11


def get_w3_connection(rpc):
    w3 = Web3(Web3.HTTPProvider(rpc))
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    return w3


def load_wallet(w3: Web3):
    with open(KEYFILE) as fp:
        wallet_pass = getpass.getpass("Enter wallet password: ")
        return w3.eth.account.decrypt(fp.read(), wallet_pass)


class Compounder:
    """ Compounds a list of Pairs sequentially """
    def __init__(self, w3: Web3, tasks: List["CompoundTask"]):
        self.w3 = w3
        self.tasks = tasks

    def run(self):
        for task in self.tasks:
            try:
                task.compound()
            except CompoundError as e:
                print(e)


def main():
    w3 = get_w3_connection(ENDPOINT)
    wallet = load_wallet(w3)
    manager = ContractManager(w3, _PARENT)
    pair = PZAPCompoundTask(w3, manager, MY_ADDRESS, POOL_ID, wallet)
    pounder = Compounder(manager, [pair])
    pounder.run()


if __name__ == "__main__":
    main()