import json
import time
import logging

from datetime import datetime, timedelta
from pathlib import Path
from typing import List

from PolyCompounder.blockchain import Blockchain
from PolyCompounder.exceptions import HarvestNotAvailable, NoLiquidity, UnkownStrategyError
from PolyCompounder.config import DATETIME_FORMAT
from PolyCompounder.utils import *


__all__ = [
    "StrategyLoader",
    "CompoundStrategy",
    "PZAPPoolCompoundStrategy"
]


class CompoundStrategy:
    """ Base class for compound strategies """
    def __init__(self, blockchain: Blockchain, name: str):
        self.logger = logging.getLogger(f"{self.__class__.__name__}-{name}")
        self.blockchain = blockchain
        self.name = name

    def compound(self):
        raise NotImplementedError("Childs of CompoundStrategy must implement 'compound'")

    def _transact(self, func: callable, args: tuple):
        res = self.blockchain.transact(func, args)
        time.sleep(2)
    
    def __str__(self):
        return f"{self.name} on {self.blockchain}"


class PZAPPoolCompoundStrategy(CompoundStrategy):
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

    def compound(self):
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


class StrategyLoader:
    def __init__(self, blockchain):
        self.blockchain = blockchain

    def load_from_file(self, path: Path) -> List["CompoundStrategy"]:
        with open(path, "r") as fp:
            return self.load_from_list(json.load(fp))
    
    def load_from_list(self, strategies: list) -> List["CompoundStrategy"]:
        out = []
        for strat in strategies:
            strat_class = self.find_strat_by_name(strat["strategy"])
            obj = strat_class(self.blockchain, strat["name"], **strat.get("params", []))
            out.append(obj)
        return out

    def find_strat_by_name(self, name: str):
        for class_ in CompoundStrategy.__subclasses__():
            if class_.__name__ == name:
                return class_
        raise UnkownStrategyError(f"Can't find strategy '{name}'")

    @classmethod
    def list_strats(cls):
        return CompoundStrategy.__subclasses__()
