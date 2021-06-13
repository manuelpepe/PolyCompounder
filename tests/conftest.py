import pytest

from PolyCompounder.exceptions import MissingConfig
from PolyCompounder.strategy import CompoundStrategy

try:
    from PolyCompounder.config import ENDPOINT
except MissingConfig as err:
    print("ERROR: Config not found. Create config with valid rpc to run tests.")
    raise err

from PolyCompounder.blockchain import Blockchain
from PolyCompounder.queue import QueueLoader


@pytest.fixture
def blockchain():
    return Blockchain(ENDPOINT, 137, "POLYGON")


@pytest.fixture
def queue(blockchain):
    return QueueLoader(blockchain).load()
