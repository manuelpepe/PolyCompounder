import pytest

from datetime import datetime, timedelta
from unittest.mock import MagicMock

from PolyCompounder.strategy import CompoundStrategy, HarvestNotAvailable
from PolyCompounder.core import Compounder
from PolyCompounder.queue import Queue, QueueItem

RANDOM_DELTA = timedelta(days=1)
RANDOM_DATE = datetime.now() + RANDOM_DELTA


class StrategyTestHarvestNotAvailable(CompoundStrategy):
    def compound(self):
        raise HarvestNotAvailable("TEST", RANDOM_DATE.timestamp())


class StrategyTestWorks(CompoundStrategy):
    def compound(self):
        return True


def test_compounder_is_created(queue):
    compounder = Compounder(queue)
    assert compounder


def test_item_runs():
    strat = StrategyTestHarvestNotAvailable(None, "Test Strategy")
    strat.compound = MagicMock(name="compound")
    item = QueueItem(0, strat, QueueItem.RUN_ASAP)
    compounder = Compounder(Queue([item]))
    assert len(compounder.queue) == 1
    compounder.run()
    strat.compound.assert_called_once()


def test_that_fails_is_rescheduled():
    strat = StrategyTestHarvestNotAvailable(None, "Test Strategy")
    item = QueueItem(0, strat, QueueItem.RUN_ASAP)
    compounder = Compounder(Queue([item]))
    compounder.run()
    assert compounder.queue[0].next_at == int(RANDOM_DATE.timestamp())
    # Should wait RANDOM_DELTA before calling compound again
    strat.compound = MagicMock(name="compound")
    compounder.run()
    strat.compound.assert_not_called()
    # If we change the next_at time it should process it
    some_passed_date = (datetime.now() - timedelta(days=1)).timestamp()
    compounder.queue[0].schedule_for(int(some_passed_date))
    compounder.run()
    strat.compound.assert_called_once()


def test_failed_strategty_reschedules_using_repeat_every():
    strat = StrategyTestWorks(None, "Test Strategy that works")
    item = QueueItem(0, strat, QueueItem.RUN_ASAP, repeat_every={"days": 1, "hours": 1})
    compounder = Compounder(Queue([item]))
    compounder.run()
    item_next_exec = datetime.fromtimestamp(compounder.queue[0].next_at)
    difference_in_time = item_next_exec - datetime.now()
    assert difference_in_time > timedelta(days=1) and difference_in_time < timedelta(days=1, hours=1, seconds=1)
