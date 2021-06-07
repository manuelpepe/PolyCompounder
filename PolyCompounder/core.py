import os
import getpass

from typing import List, Optional
from os.path import isfile

from web3 import Web3
from web3.middleware import geth_poa_middleware

from config import DEFAULT_KEYFILE
from exceptions import CompoundError


def get_w3_connection(rpc):
    w3 = Web3(Web3.HTTPProvider(rpc))
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    return w3


def load_wallet(w3: Web3, keyfile: Optional[str]):
    if keyfile is None:
        keyfile = DEFAULT_KEYFILE
    if not isfile(keyfile):
        raise Exception(f"Keyfile at '{keyfile}' not found.")
    with open(keyfile) as fp:
        wallet_pass = os.environ.get("POLYCOMP_KEY")
        if not wallet_pass:
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
