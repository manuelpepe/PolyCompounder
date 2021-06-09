import logging

from web3 import Web3
from hexbytes import HexBytes


class TransactionError(Exception): pass


class TransactionHandler:
    def __init__(self, w3: Web3, chain_id: int, gas: int = 1, owner: str = None, private_key: HexBytes = None):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.w3 = w3
        self.owner = owner
        self.private_key = private_key
        self.chain_id = chain_id
        self.gas = gas

    def _trans_details(self):
        return {
            "chainId" : self.chain_id,
            "gas" : self.gas,
            "gasPrice" : self.w3.toWei('1', 'gwei'),
            "nonce" : self.w3.eth.getTransactionCount(self.owner),
        }

    def transact(self, func: callable, args: tuple):
        """ Submits transaction and prints hash """
        if not self.private_key:
            raise TransactionError("Private key not set")
        txn = func(*args).buildTransaction(self._trans_details())
        stxn = self.w3.eth.account.sign_transaction(txn, private_key=self.private_key)
        sent = self.w3.eth.send_raw_transaction(stxn.rawTransaction)
        rcpt = self.w3.eth.wait_for_transaction_receipt(sent) 
        self.logger.info(f"Block Hash: {rcpt.blockHash.hex()}")
        self.logger.info(f"Gas Used: {rcpt.gasUsed}")
        return sent, rcpt
