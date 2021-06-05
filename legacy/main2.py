import getpass

from typing import List
from pathlib import Path
from datetime import datetime, timedelta

from web3 import Web3
from web3.middleware import geth_poa_middleware
from hexbytes import HexBytes

from utils import *


ENDPOINT = "https://rpc-mainnet.maticvigil.com/v1/APIKEY"
MY_ADDRESS = "0xADDRESS"
DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
_PARENT = Path(__file__).parent
KEYFILE = _PARENT / "key.file"
POOL_ID = 11


class CompoundError(Exception):
    """ Base class for errors while compounding """
    pass

class HarvestNotAvailable(CompoundError): pass
class NoLiquidity(CompoundError): pass


def get_w3_connection(rpc):
    w3 = Web3(Web3.HTTPProvider(rpc))
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    return w3


def load_wallet(w3: Web3):
    with open(KEYFILE) as fp:
        wallet_pass = getpass.getpass("Enter wallet password: ")
        wallet = w3.eth.account.decrypt(fp.read(), wallet_pass)


class ContractManager:
    """
    Stores contract definitions (address and location of the abi file).
    Reads and returns contracts from the network.
    """

    CONTRACTS = {
        "PZAP": {
            "address": "0xeb2778f74e5ee038e67aa6c77f0f0451abd748fd",
            "abifile": "pzap.abi",
        },
        "WBTC": {
            "address": "0x1bfd67037b42cf73acf2047067bd4f2c47d9bfd6",
            "abifile": "wbtc.abi",
        },
        "MASTERCHEF": {
            "address": "0xB93C082bCfCCf5BAeA0E0f0c556668E25A41B896",
            "abifile": "masterchef.abi",
        },
        "ROUTER": {
            "address": "0x4aAEC1FA8247F85Dc3Df20F4e03FEAFdCB087Ae9",
            "abifile": "router.abi",
        },
        "PAIR": {
            "address": "0x9876157578B9F53A244632693B69938353915d5C",
            "abifile": "IPoliZapPair.abi"
        }
    }

    def __init__(self, w3: Web3, parent: Path):
        self.w3 = w3
        self.parent = parent

    def read_contract(self, name: str):
        if not name in self.CONTRACTS.keys():
            raise ValueError("Contract not found.")
        contract = self.CONTRACTS[name] 
        with open(self.parent / contract["abifile"], "r") as fp:
            return self.w3.eth.contract(
                address=Web3.toChecksumAddress(contract["address"]), 
                abi=fp.read()
            )


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


class CompoundTask:
    """ Base class for compound tasks """
    pass


class PZAPCompoundTask(CompoundTask):
    NAME = "PZAP-WBTC"
    SWAP_PATH = ["PZAP", "WBTC"]
    PAIR = "PAIR"
    MASTERCHEF = "MASTERCHEF"
    ROUTER = "ROUTER"

    def __init__(self, w3: Web3, manager: ContractManager, owner: str, pool_id: int, private_key: HexBytes):
        self.w3 = w3
        self.manager = manager
        self.owner = owner
        self.pool_id = pool_id
        self.masterchef = manager.read_contract(self.MASTERCHEF)
        self.router = manager.read_contract(self.ROUTER)
        self.tokenA = manager.read_contract(self.SWAP_PATH[0])
        self.tokenB = manager.read_contract(self.SWAP_PATH[1])
        self.pair = manager.read_contract(self.PAIR)
        self.private_key = private_key

    def _trans_details(self):
        return {
            "chainId" : 137,
            "gas" : 239185,
            "gasPrice" : self.w3.toWei('1', 'gwei'),
            "nonce" : self.w3.eth.getTransactionCount(self.owner),
        }

    def _transact(self, func: callable, args: tuple):
        """ Submits transaction and prints hash """
        txn = func(*args).buildTransaction(self._trans_details())
        stxn = self.w3.eth.account.sign_transaction(txn, private_key=self.private_key)
        sent = self.w3.eth.send_raw_transaction(stxn.rawTransaction)
        rcpt = self.w3.eth.wait_for_transaction_receipt(sent) 
        print(f"Transaction: {txn}")
        print(f"Block Hash: {rcpt.blockHash.hex()}")
        print(f"Gas Used: {rcpt.gasUsed}")
        return sent, rcpt

    def compound(self):
        """ Runs complete compound process """
        print(f"\nCompounding {self.NAME}")
        self.print_pending_rewards()
        self.harvest()
        self.swap_half_harvest()
        self.add_liquidity()
        self.stake_liquidity()

    def print_pending_rewards(self):
        pending_amount = self.masterchef.functions.pendingPZap(self.pool_id, MY_ADDRESS).call()
        print(f"Pending rewards: {amountToPZAP(pending_amount)}")
    
    def harvest(self):
        if not self._is_harvest_available():
            remaining = self.masterchef.functions.getHarvestUntil(self.pool_id, self.owner).call()
            dt = datetime.fromtimestamp(remaining)
            raise HarvestNotAvailable(f"Harvest unlocks at: {dt.strftime(DATETIME_FORMAT)}")
        print("Harvesting...")
        self._transact(self.masterchef.functions.deposit, (self.pool_id, 0))
        
    def _is_harvest_available(self):
        return self.masterchef.functions.canHarvest(self.pool_id, self.owner).call()
    
    def swap_half_harvest(self):
        amountIn = int(self.tokenA.functions.balanceOf(self.owner).call() / 1.99)
        amountOutMin = self.router.functions.getAmountsOut(amountIn, self.SWAP_PATH).call()[-1]
        if amountOutMin <= 0:
            raise NoLiquidity("No liquidity for swap")
        deadline = (datetime.now() + timedelta(minutes=5)).timestamp()
        print(f"Swapping {amountToPZAP(amountIn)} PZAP for {amountToPZAP(amountOutMin)} WBTC...")
        self._transact(
            self.router.functions.swapExactTokensForTokens, 
            (amountIn, amountOutMin, SWAP_PATH, MY_ADDRESS, int(deadline))
        )

    def add_liquidity(self):
        amountADesired = amountAMin = self.tokenA.functions.balanceOf(MY_ADDRESS).call()
        amountBDesired = amountBMin = self.router.functions.getAmountsOut(amountADesired, SWAP_PATH).call()[1]
        deadline = (datetime.now() + timedelta(minutes=5)).timestamp()
        print(f"Adding liquidity ({amountToPZAP(amountADesired)} PZAP + {amountToPZAP(amountBDesired)} WBTC)...")
        self._transact(
            self.router.functions.addLiquidity, 
            (SWAP_PATH[0], SWAP_PATH[1], amountADesired, amountAMin, amountBDesired, amountBMin, MY_ADDRESS, int(deadline))
        )

    def stake_liquidity(self):
        lps_to_stake = self.pair.functions.balanceOf(MY_ADDRESS).call()
        print(f"Staking {lps_to_stake} LPs to {self.NAME}...")
        self._transact(self.router.functions.deposit, (self.pool_id, lps_to_stake))
        

def main():
    w3 = get_w3_connection(ENDPOINT)
    wallet = load_wallet(w3)
    manager = ContractManager(w3, _PARENT)
    pair = PZAPCompoundTask(w3, manager, MY_ADDRESS, POOL_ID, wallet)
    pounder = Compounder(manager, [pair])
    pounder.run()


if __name__ == "__main__":
    main()