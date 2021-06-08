import pytest
from PolyCompounder.exceptions import MissingConfig

try:
    from PolyCompounder.config import ENDPOINT
except MissingConfig as err:
    print("ERROR: Config not found. Create config with valid rpc to run tests.")
    raise err

from PolyCompounder.blockchain import Blockchain


@pytest.fixture
def blockchain():
    return Blockchain(ENDPOINT, 137, "POLYGON")
