import pytest

from datetime import datetime, timedelta
from unittest.mock import MagicMock

from PolyCompounder.strategy import CompoundStrategy
from PolyCompounder.core import Compounder
from PolyCompounder.exceptions import HarvestNotAvailable

RANDOM_DELTA = timedelta(days=1)
RANDOM_DATE = datetime.now() + RANDOM_DELTA


class StrategyForTesting(CompoundStrategy):
    def compound(self):
        raise HarvestNotAvailable("TEST", RANDOM_DATE.timestamp())


def test_compounder_is_created(stratloader):
    compounder = Compounder([])
    assert compounder


def test_item_runs():
    strat = StrategyForTesting(None, "Test Strategy")
    strat.compound = MagicMock(name="compound")
    compounder = Compounder([strat])
    assert len(compounder.queue) == 1
    compounder.run()
    strat.compound.assert_called_once()


def test_that_fails_is_rescheduled():
    strat = StrategyForTesting(None, "Test Strategy")
    compounder = Compounder([strat])
    compounder.run()
    assert compounder.queue[0].next_at == RANDOM_DATE.timestamp()
    # Should wait RANDOM_DELTA before calling compound again
    strat.compound = MagicMock(name="compound")
    compounder.run()
    strat.compound.assert_not_called()
    # If we change the next_at time it should process it
    compounder.queue[0].next_at = (datetime.now() - timedelta(days=1)).timestamp()
    compounder.run()
    strat.compound.assert_called_once()
    