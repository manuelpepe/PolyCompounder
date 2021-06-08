from PolyCompounder.strategy import StrategyLoader, CompoundStrategy
from PolyCompounder.config import STRATEGIES_FILE


def test_strategy_loader_creation(blockchain):
    stratloader = StrategyLoader(blockchain)
    assert stratloader


def test_strategy_loader_fixture(stratloader):
    assert isinstance(stratloader, StrategyLoader)


def test_strategy_loader_loads_list(blockchain):
    stratloader = StrategyLoader(blockchain)
    assert isinstance(stratloader.load_from_file(STRATEGIES_FILE), list)


def test_strategy_loader_loads_list_of_strategies(strategies):
    assert all((isinstance(s, CompoundStrategy) for s in strategies))