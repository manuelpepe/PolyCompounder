from datetime import datetime, timedelta
from typing import List

from pab.config import DATETIME_FORMAT
from pab.utils import amountToDecimal
from pab.strategy import SpecificTimeRescheduleError, RescheduleError, BaseStrategy


class HarvestNotAvailable(SpecificTimeRescheduleError): 
    """ Harvest wasn't available. Should retry when it unlocks. """
    pass


class NoLiquidity(RescheduleError):
    """ No liquidity found at the time. Compounder may retry whenever possible. """ 
    pass


class PZAPPoolCompoundStrategy(BaseStrategy):
    """ Compound strategy for PZAP Pools """

    def __init__(self, *args, swap_path: List[str], pair: str, masterchef: str, router: str, pool_id: int, acc_ix: int, retry_asap: bool = False):
        super().__init__(*args)
        self.owner = self.accounts[acc_ix]
        self.pool_id = pool_id
        self.masterchef = self.contracts.get(masterchef)
        self.router = self.contracts.get(router)
        self.tokenA = self.contracts.get(swap_path[0])
        self.tokenB = self.contracts.get(swap_path[1])
        self.pair = self.contracts.get(pair)
        self.retry_asap = retry_asap

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
        pending_amount = self.masterchef.functions.pendingPZap(self.pool_id, self.owner.address).call()
        self.logger.info(f"Pending rewards: {amountToDecimal(pending_amount, 18)}")
    
    def harvest(self):
        if not self._is_harvest_available():
            next_at = self.masterchef.functions.getHarvestUntil(self.pool_id, self.owner.address).call()
            dt = datetime.fromtimestamp(next_at)
            if self.retry_asap:
                raise HarvestNotAvailable(f"Harvest unlocks at: {dt.strftime(DATETIME_FORMAT)}", next_at)
            raise RescheduleError(f"Harvest unlocks at: {dt.strftime(DATETIME_FORMAT)}")
        self.logger.info("* Harvesting...")
        self.transact(self.masterchef.functions.deposit, (self.pool_id, 0))
        
    def _is_harvest_available(self):
        return self.masterchef.functions.canHarvest(self.pool_id, self.owner.address).call()
    
    def swap_half_harvest(self):
        amountIn = int(self.tokenA.functions.balanceOf(self.owner.address).call() / 1.99)
        amountOutMin = self.router.functions.getAmountsOut(amountIn, self._get_swap_path()).call()[-1]
        if amountOutMin <= 0:
            raise NoLiquidity("No liquidity for swap")
        deadline = (datetime.now() + timedelta(minutes=5)).timestamp()
        self.logger.info(f"* Swapping {amountToDecimal(amountIn, 18)} PZAP for {amountToDecimal(amountOutMin, 8)} WBTC...")
        self.transact(
            self.router.functions.swapExactTokensForTokens, 
            (amountIn, amountOutMin, self._get_swap_path(), self.owner.address, int(deadline))
        )

    def add_liquidity(self):
        amountADesired = self.tokenA.functions.balanceOf(self.owner.address).call()
        amountAMin = int(amountADesired * 0.92)
        amountBDesired = self.router.functions.getAmountsOut(amountADesired, self._get_swap_path()).call()[1]
        amountBMin = int(amountBDesired * 0.92)
        deadline = (datetime.now() + timedelta(minutes=5)).timestamp()
        self.logger.info(f"* Adding liquidity ({amountToDecimal(amountADesired, 18)} PZAP + {amountToDecimal(amountBDesired, 8)} WBTC or at least ({amountToDecimal(amountAMin, 18)} PZAP + {amountToDecimal(amountBMin, 8)} WBTC))...")
        self.transact(
            self.owner,
            self.router.functions.addLiquidity, 
            (self.tokenA.address, self.tokenB.address, amountADesired, amountBDesired, amountAMin, amountBMin, self.owner.address, int(deadline))
        )

    def stake_liquidity(self):
        lps_to_stake = self.pair.functions.balanceOf(self.owner.address).call()
        if lps_to_stake < 0:
            raise NoLiquidity("No LPs to stake")
        self.logger.info(f"* Staking {amountToDecimal(lps_to_stake, 18)} LPs to {self.name}...")
        self.transact(self.masterchef.functions.deposit, (self.pool_id, lps_to_stake))
