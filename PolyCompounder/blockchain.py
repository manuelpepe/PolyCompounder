import os
import getpass

from os.path import isfile
from typing import Optional

from web3 import Web3
from web3.middleware.geth_poa import geth_poa_middleware

from contract import ContractManager
from transaction import TransactionHandler
from config import DEFAULT_KEYFILE


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

class Blockchain:
    """ API for contracts and transactions """

    def __init__(self, rpc: str, id: int, name: str, txn_handler_class: TransactionHandler = TransactionHandler):
        self.rpc = rpc
        self.id = id
        self.name = name
        self.w3 = self._connect_web3()
        self.txn_handler = txn_handler_class(self.w3, self.id, 239185)
        self.contract_manager = ContractManager(self.w3)
        self.wallet = None
        self.owner = None

    def _connect_web3(self):
        w3 = Web3(Web3.HTTPProvider(self.rpc))
        w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        return w3

    def load_wallet(self, owner: str, keyfile: str):
        if self.wallet:
            raise Exception("Wallet already loaded")
        self.wallet = load_wallet(self.w3, keyfile)
        self.owner = owner
        self.update_txn_handler()

    def update_txn_handler(self):
        if self.txn_handler:
            self.txn_handler.private_key = self.wallet
            self.txn_handler.owner = self.owner

    def transact(self, func: callable, args: tuple):
        return self.txn_handler.transact(func, args)

    def read_contract(self, name):
        return self.contract_manager.read_contract(name)