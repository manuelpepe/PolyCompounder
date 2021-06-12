import sys
import time
import logging

from typing import List, Union
from datetime import datetime, timedelta

from PolyCompounder.strategy import CompoundStrategy, RescheduleError, SpecificTimeRescheduleError
from PolyCompounder.config import DATETIME_FORMAT
from PolyCompounder.alert import alert_exception
from PolyCompounder.queue import Queue, QueueItem


class Compounder:
    """ Runs a list of strategies sequentially """
    ITERATION_SLEEP = 60

    def __init__(self, queue: Queue):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.queue = queue

    def start(self):
        while True:
            self.run()
            self.logger.debug(f"Queue iteration finished.")
            self._sleep()

    def run(self):
        for item in self.queue:
            self.process_item(item)

    def process_item(self, item: QueueItem):
        try:
            item.process()
            self._reschedule_item(item)
        except SpecificTimeRescheduleError as err:
            self.logger.warning(err)
            item.schedule_for(int(err.next_at))
        except RescheduleError as err:
            self.logger.warning(err)
            self._reschedule_item(item)
        except Exception as err:
            self.logger.exception(err)
            alert_exception(err)
            raise err
    
    def _reschedule_item(self, item: QueueItem):
        next_run = QueueItem.RUN_NEVER
        if item.repeats():
            next_run = item.next_repetition_time()
        item.schedule_for(next_run)

    def _sleep(self):
        self.logger.debug(f"Sleeping for {self.ITERATION_SLEEP} seconds.")
        time.sleep(self.ITERATION_SLEEP)