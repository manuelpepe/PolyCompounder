from datetime import datetime, timedelta
from pathlib import Path
from typing import List

from pab.blockchain import Blockchain
from pab.config import DATETIME_FORMAT
from pab.utils import *
from pab.strategy import SpecificTimeRescheduleError, RescheduleError, BaseStrategy


class HarvestNotAvailable(SpecificTimeRescheduleError): 
    """ Harvest wasn't available. Should retry when it unlocks. """
    pass


class NoLiquidity(RescheduleError):
    """ No liquidity found at the time. Compounder may retry whenever possible. """ 
    pass


class PZAPPoolCompoundStrategy(BaseStrategy):
    """ Compound strategy for PZAP Pools """

    def __init__(self, blockchain: Blockchain, name: str, swap_path: List[str], pair: str, masterchef: str, router: str, pool_id: int):
        super().__init__(blockchain, name)
        self.owner = blockchain.owner
        self.pool_id = pool_id
        self.masterchef = blockchain.read_contract(masterchef)
        self.router = blockchain.read_contract(router)
        self.tokenA = blockchain.read_contract(swap_path[0])
        self.tokenB = blockchain.read_contract(swap_path[1])
        self.pair = blockchain.read_contract(pair)

    def _get_swap_path(self):
        return [self.tokenA.address, self.tokenB.address]

    def run(self):
        """ Runs complete compound process """
        self.print_pending_rewards()
        self.harvest()
        self.swap_half_harvest()
        self.add_liquidity()
        self.stake_liquidity()

    def print_pending_rewards(self):
        pending_amount = self.masterchef.functions.pendingPZap(self.pool_id, self.owner).call()
        self.logger.info(f"Pending rewards: {amountToPZAP(pending_amount)}")
    
    def harvest(self):
        if not self._is_harvest_available():
            next_at = self.masterchef.functions.getHarvestUntil(self.pool_id, self.owner).call()
            dt = datetime.fromtimestamp(next_at)
            raise HarvestNotAvailable(f"Harvest unlocks at: {dt.strftime(DATETIME_FORMAT)}", next_at)
        self.logger.info("* Harvesting...")
        self._transact(self.masterchef.functions.deposit, (self.pool_id, 0))
        
    def _is_harvest_available(self):
        return self.masterchef.functions.canHarvest(self.pool_id, self.owner).call()
    
    def swap_half_harvest(self):
        amountIn = int(self.tokenA.functions.balanceOf(self.owner).call() / 1.99)
        amountOutMin = self.router.functions.getAmountsOut(amountIn, self._get_swap_path()).call()[-1]
        if amountOutMin <= 0:
            raise NoLiquidity("No liquidity for swap")
        deadline = (datetime.now() + timedelta(minutes=5)).timestamp()
        self.logger.info(f"* Swapping {amountToPZAP(amountIn)} PZAP for {amountToWBTC(amountOutMin)} WBTC...")
        self._transact(
            self.router.functions.swapExactTokensForTokens, 
            (amountIn, amountOutMin, self._get_swap_path(), self.owner, int(deadline))
        )

    def add_liquidity(self):
        amountADesired = self.tokenA.functions.balanceOf(self.owner).call()
        amountAMin = int(amountADesired * 0.92)
        amountBDesired = self.router.functions.getAmountsOut(amountADesired, self._get_swap_path()).call()[1]
        amountBMin = int(amountBDesired * 0.92)
        deadline = (datetime.now() + timedelta(minutes=5)).timestamp()
        self.logger.info(f"* Adding liquidity ({amountToPZAP(amountADesired)} PZAP + {amountToWBTC(amountBDesired)} WBTC or at least ({amountToPZAP(amountAMin)} PZAP + {amountToWBTC(amountBMin)} WBTC))...")
        self._transact(
            self.router.functions.addLiquidity, 
            (self.tokenA.address, self.tokenB.address, amountADesired, amountBDesired, amountAMin, amountBMin, self.owner, int(deadline))
        )

    def stake_liquidity(self):
        lps_to_stake = self.pair.functions.balanceOf(self.owner).call()
        if lps_to_stake < 0:
            raise NoLiquidity("No LPs to stake")
        self.logger.info(f"* Staking {amountToLPs(lps_to_stake)} LPs to {self.name}...")
        self._transact(self.masterchef.functions.deposit, (self.pool_id, lps_to_stake))

