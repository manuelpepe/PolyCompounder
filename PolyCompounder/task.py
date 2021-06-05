from datetime import datetime, timedelta

from web3 import Web3
from hexbytes import HexBytes

from contract import ContractManager
from utils import *
from exceptions import HarvestNotAvailable, NoLiquidity
from config import DATETIME_FORMAT

__all__ = [
    "CompoundTask",
    "PZAPCompoundTask"
]


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
        self.private_key = private_key
        self.masterchef = manager.read_contract(self.MASTERCHEF)
        self.router = manager.read_contract(self.ROUTER)
        self.tokenA = manager.read_contract(self.SWAP_PATH[0])
        self.tokenB = manager.read_contract(self.SWAP_PATH[1])
        self.pair = manager.read_contract(self.PAIR)

    def _get_swap_path(self):
        return [self.tokenA.address, self.tokenB.address]

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
        print("Done")

    def print_pending_rewards(self):
        pending_amount = self.masterchef.functions.pendingPZap(self.pool_id, self.owner).call()
        print(f"Pending rewards: {amountToPZAP(pending_amount)}")
    
    def harvest(self):
        if not self._is_harvest_available():
            remaining = self.masterchef.functions.getHarvestUntil(self.pool_id, self.owner).call()
            dt = datetime.fromtimestamp(remaining)
            raise HarvestNotAvailable(f"Harvest unlocks at: {dt.strftime(DATETIME_FORMAT)}")
        print("* Harvesting...")
        self._transact(self.masterchef.functions.deposit, (self.pool_id, 0))
        
    def _is_harvest_available(self):
        return self.masterchef.functions.canHarvest(self.pool_id, self.owner).call()
    
    def swap_half_harvest(self):
        amountIn = int(self.tokenA.functions.balanceOf(self.owner).call() / 1.99)
        amountOutMin = self.router.functions.getAmountsOut(amountIn, self._get_swap_path()).call()[-1]
        if amountOutMin <= 0:
            raise NoLiquidity("No liquidity for swap")
        deadline = (datetime.now() + timedelta(minutes=5)).timestamp()
        print(f"* Swapping {amountToPZAP(amountIn)} PZAP for {amountToWBTC(amountOutMin)} WBTC...")
        self._transact(
            self.router.functions.swapExactTokensForTokens, 
            (amountIn, amountOutMin, self._get_swap_path(), self.owner, int(deadline))
        )

    def add_liquidity(self):
        amountADesired = amountAMin = self.tokenA.functions.balanceOf(self.owner).call()
        amountBDesired = amountBMin = self.router.functions.getAmountsOut(amountADesired, self._get_swap_path()).call()[1]
        deadline = (datetime.now() + timedelta(minutes=5)).timestamp()
        print(f"* Adding liquidity ({amountToPZAP(amountADesired)} PZAP + {amountToWBTC(amountBDesired)} WBTC)...")
        self._transact(
            self.router.functions.addLiquidity, 
            (self.tokenA.address, self.tokenB.address, amountADesired, amountAMin, amountBDesired, amountBMin, self.owner, int(deadline))
        )

    def stake_liquidity(self):
        lps_to_stake = self.pair.functions.balanceOf(self.owner).call()
        print(f"* Staking {amountToLPs(lps_to_stake)} LPs to {self.NAME}...")
        self._transact(self.masterchef.functions.deposit, (self.pool_id, lps_to_stake))
        