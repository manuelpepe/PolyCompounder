from PolyCompounder.queue import Queue, QueueItem, QueueLoader
from PolyCompounder.strategy import CompoundStrategy
from PolyCompounder.config import STRATEGIES_FILE


def test_queue_loader_creation(blockchain):
    queueloader = QueueLoader(blockchain)
    assert queueloader


def test_queue_loader_loads(blockchain):
    loader = QueueLoader(blockchain)
    queue = loader.load(STRATEGIES_FILE)
    assert isinstance(queue, Queue)
    assert len(queue) > 0
    assert all(isinstance(item, QueueItem) for item in queue)
