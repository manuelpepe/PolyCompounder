import pytest

from PolyCompounder.config import ENDPOINT
from PolyCompounder.blockchain import Blockchain


@pytest.fixture
def blockchain():
    return Blockchain(ENDPOINT, 137, "POLYGON")
