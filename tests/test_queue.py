from PolyCompounder.queue import Queue, QueueItem, QueueLoader


def test_queue_loader_creation(blockchain):
    queueloader = QueueLoader(blockchain)
    assert queueloader


def test_queue_loader_loads(blockchain):
    queue = QueueLoader(blockchain).load()
    assert isinstance(queue, Queue)
    assert len(queue) > 0
    assert all(isinstance(item, QueueItem) for item in queue)
