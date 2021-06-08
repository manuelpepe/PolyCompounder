import pytest

from PolyCompounder.exceptions import MissingConfig
from PolyCompounder.strategy import StrategyLoader, CompoundStrategy
from PolyCompounder.config import RESOURCES, STRATEGIES_FILE

try:
    from PolyCompounder.config import ENDPOINT
except MissingConfig as err:
    print("ERROR: Config not found. Create config with valid rpc to run tests.")
    raise err

from PolyCompounder.blockchain import Blockchain


@pytest.fixture
def blockchain():
    return Blockchain(ENDPOINT, 137, "POLYGON")

@pytest.fixture
def stratloader(blockchain):
    return StrategyLoader(blockchain)

@pytest.fixture
def strategies(stratloader: StrategyLoader):
    return stratloader.load_from_file(STRATEGIES_FILE)
