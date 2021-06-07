from datetime import datetime, timedelta

from blockchain import Blockchain
from exceptions import HarvestNotAvailable, NoLiquidity
from config import DATETIME_FORMAT
from utils import *


__all__ = [
    "CompoundStrategy",
    "PZAPCompoundStrategy"
]


class CompoundStrategy:
    """ Base class for compound strategies """
    pass


class PZAPCompoundStrategy(CompoundStrategy):
    NAME = "PZAP-WBTC"
    SWAP_PATH = ["PZAP", "WBTC"]
    PAIR = "PAIR"
    MASTERCHEF = "MASTERCHEF"
    ROUTER = "ROUTER"

    def __init__(self, blockchain: Blockchain, pool_id: int):
        self.blockchain = blockchain
        self.owner = blockchain.owner
        self.pool_id = pool_id
        self.masterchef = blockchain.read_contract(self.MASTERCHEF)
        self.router = blockchain.read_contract(self.ROUTER)
        self.tokenA = blockchain.read_contract(self.SWAP_PATH[0])
        self.tokenB = blockchain.read_contract(self.SWAP_PATH[1])
        self.pair = blockchain.read_contract(self.PAIR)

    def _get_swap_path(self):
        return [self.tokenA.address, self.tokenB.address]

    def _transact(self, func: callable, args: tuple):
        return self.blockchain.transact(func, args)

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
        if False and not self._is_harvest_available():
            remaining = self.masterchef.functions.getHarvestUntil(self.pool_id, self.owner).call()
            dt = datetime.fromtimestamp(remaining)
            raise HarvestNotAvailable(f"Harvest unlocks at: {dt.strftime(DATETIME_FORMAT)}")
        print("* Harvesting...")
        self._transact(self.masterchef.functions.deposit, (self.pool_id, 0))
        breakpoint()
        
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
        amountADesired = self.tokenA.functions.balanceOf(self.owner).call()
        amountAMin = int(amountADesired * 0.95)
        amountBDesired = self.router.functions.getAmountsOut(amountADesired, self._get_swap_path()).call()[1]
        amountBMin = int(amountBDesired * 0.95)
        deadline = (datetime.now() + timedelta(minutes=5)).timestamp()
        print(f"* Adding liquidity ({amountToPZAP(amountADesired)} PZAP + {amountToWBTC(amountBDesired)} WBTC)...")
        input()
        self._transact(
            self.router.functions.addLiquidity, 
            (self.tokenA.address, self.tokenB.address, amountADesired, amountBDesired, amountAMin, amountBMin, self.owner, int(deadline))
        )

    def stake_liquidity(self):
        lps_to_stake = self.pair.functions.balanceOf(self.owner).call()
        if lps_to_stake < 0:
            raise NoLiquidity("No LPs to stake")
        print(f"* Staking {amountToLPs(lps_to_stake)} LPs to {self.NAME}...")
        input()
        self._transact(self.masterchef.functions.deposit, (self.pool_id, lps_to_stake))
        