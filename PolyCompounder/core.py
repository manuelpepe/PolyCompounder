import sys
import time
import logging

from typing import List, Union
from datetime import datetime, timedelta

from PolyCompounder.exceptions import CompoundError, HarvestNotAvailable
from PolyCompounder.strategy import CompoundStrategy
from PolyCompounder.config import DATETIME_FORMAT


class QueuedItemNotReady(Exception):
    pass


class QueuedItem:
    """ Container for a strategy to be executed in the future """ 
    logger = logging.getLogger("QueuedItem")
    RUN_ASAP = -10
    RUN_NEVER = -20

    def __init__(self, id_: int, strat: CompoundStrategy, next_at: int = None):
        self.id = id_
        self.strategy = strat
        self.next_at = next_at

    def schedule_for(self, next_at: int):
        self.next_at = next_at
    
    def is_ready(self):
        if self.next_at == self.RUN_ASAP:
            return True
        elif self.next_at == self.RUN_NEVER:
            return False
        elif self.next_at > 0:
            return datetime.fromtimestamp(self.next_at) < datetime.now()
        else:
            raise ValueError(f"Wrong value {self.next_at} of type ({type(self.next_at)} in next_at for QueuedItem #{self.id}")

    def process(self):
        if self.is_ready():
            self.logger.info(f"Running strategy {self.strategy}")
            self.strategy.compound()
            self.logger.info(f"Done with {self.strategy}")


class Compounder:
    """ Runs a list of strategies sequentially """
    ITERATION_SLEEP = 60

    def __init__(self, strategies: List[CompoundStrategy]):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.queue = [
            QueuedItem(ix, strat, QueuedItem.RUN_ASAP) for ix, strat in enumerate(strategies)
        ]

    def start(self):
        while True:
            self.run()
            self.logger.debug(f"Queue iteration finished.")
            self.sleep()

    def run(self):
        for item in self.queue:
            self.process_item(item)

    def process_item(self, item: QueuedItem):
        try:
            item.process()
        except HarvestNotAvailable as err:
            self.logger.warning(err)
            item.schedule_for(err.next_at)
        except CompoundError as e:
            self.logger.exception(e)
            raise e
        except Exception as e:
            self.logger.exception(e)
            raise e

    def sleep(self):
        self.logger.debug(f"Sleeping for {self.ITERATION_SLEEP} seconds.")
        time.sleep(self.ITERATION_SLEEP)