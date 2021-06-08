from typing import List

from PolyCompounder.exceptions import CompoundError
from PolyCompounder.strategy import CompoundStrategy


class Compounder:
    """ Compounds a list of Pairs sequentially """
    def __init__(self, strategies: List[CompoundStrategy]):
        self.strategies = strategies

    def run(self):
        for task in self.strategies:
            try:
                task.compound()
            except CompoundError as e:
                print(e)
