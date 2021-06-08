import sys
import time

from typing import List, Union
from datetime import datetime, timedelta

from PolyCompounder.exceptions import CompoundError, HarvestNotAvailable
from PolyCompounder.strategy import CompoundStrategy
from PolyCompounder.config import DATETIME_FORMAT


class Compounder:
    """ Compounds a list of Pairs sequentially """
    def __init__(self, strategies: List[CompoundStrategy]):
        self.strategies = strategies

    def run(self):
        while True:
            for task in self.strategies:
                try:
                    task.compound()
                except HarvestNotAvailable as err:
                    print(err)
                    self._sleep_until(err.next_at)
                except CompoundError as e:
                    print(e)
                    raise e
    
    def _sleep_until(self, timestamp: Union[int, float], offset: int = 10):
        sleep_in_seconds = timestamp - datetime.now().timestamp() + offset
        sleep_for = timedelta(seconds=sleep_in_seconds)
        sleep_end = datetime.now() + sleep_for
        print(f"Sleeping until {sleep_end.strftime(DATETIME_FORMAT)}\n")
        sys.stdout.flush()
        time.sleep(sleep_in_seconds)
