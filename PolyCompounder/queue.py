import json
import logging

from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, List

from PolyCompounder.blockchain import Blockchain
from PolyCompounder.strategy import CompoundStrategy
from PolyCompounder.config import TASKS_FILE


class QueueItem:
    """ Container for a strategy to be executed in the future """ 
    logger = logging.getLogger("QueuedItem")

    RUN_ASAP = -10
    RUN_NEVER = -20

    def __init__(self, id_: int, strat: CompoundStrategy, next_at: int, repeat_every: Optional[dict] = None):
        self.id = id_
        self.strategy = strat
        self.next_at = next_at
        self.repeat_every = repeat_every
        self.last_start = 0

    def repeats(self):
        return bool(self.repeat_every)

    def next_repetition_time(self):
        last = datetime.fromtimestamp(self.last_start)
        new = last + timedelta(**self.repeat_every)
        return int(new.timestamp())

    def schedule_for(self, next_at: int):
        if type(next_at) != int:
            raise ValueError("Schedule for must receive an integer timestamp")
        if next_at == self.RUN_NEVER:
            self.logger.warning(f"{self} disabled")
        self.next_at = next_at
    
    def is_ready(self):
        if self.next_at == self.RUN_ASAP:
            return True
        elif self.next_at == self.RUN_NEVER:
            return False
        elif self.next_at > 0:
            return datetime.fromtimestamp(self.next_at) < datetime.now()
        else:
            raise ValueError(f"Wrong value {self.next_at} of type {type(self.next_at)} for QueuedItem.next_at #{self.id}")

    def process(self):
        if self.is_ready():
            self.logger.info(f"Running strategy {self.strategy}")
            self.last_start = datetime.now().timestamp()
            self.strategy.compound()
            self.logger.info(f"Done with {self.strategy}")

    def __str__(self):
        return f"QueuedItem#{self.id} for {self.strategy}"


class Queue:
    """ Wrapper for a list of QueueItems """
    def __init__(self, items: List[QueueItem]):
        self.items = items

    def __getitem__(self, key):
        return self.items[key]

    def __iter__(self):
        return self.items.__iter__()
    
    def __next__(self):
        return self.items.__next__()

    def __len__(self):
        return len(self.items)


class QueueLoader:
    """ Loads a Queue from raw data """
    def __init__(self, blockchain: Blockchain):
        self.blockchain = blockchain
    
    def load(self):
        with open(Path.cwd() / TASKS_FILE, "r") as fp:
            tasks = json.load(fp)
            return self._create_queue_from_list(tasks)

    def _create_queue_from_list(self, tasks: List[dict]):
        out = []
        for ix, data in enumerate(tasks):
            strat = self._create_strat_from_data(data)
            repeat = data.get("repeat_every", {})
            item = QueueItem(ix, strat, QueueItem.RUN_ASAP, repeat_every=repeat)
            out.append(item)
        return Queue(out)

    def _create_strat_from_data(self, data: dict) -> CompoundStrategy:
        strat_class = self._find_strat_by_name(data["strategy"])
        return strat_class(self.blockchain, data["name"], **data.get("params", []))

    def _find_strat_by_name(self, name: str):
        for class_ in CompoundStrategy.__subclasses__():
            if class_.__name__ == name:
                return class_
        raise UnkownStrategyError(f"Can't find strategy '{name}'")

    @classmethod
    def list_strats(cls):
        return CompoundStrategy.__subclasses__()


class QueuedItemNotReady(Exception):
    pass


class UnkownStrategyError(Exception): 
    pass