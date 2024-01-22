import logging
from queue import SimpleQueue, Empty

from .render_item import RenderItem

logger = logging.getLogger(__name__)

class RenderQueue:
    def __init__(self, max_size = 1_000) -> None:
        self.queue: 'SimpleQueue[RenderItem]' = SimpleQueue()
        self.max_size = max_size

    def put(self, item: RenderItem) -> bool:
        if self.queue.qsize() > self.max_size:
            logger.debug(f"Tried to put {item.token} into queue but its full. ~{self.queue.qsize()}/{self.max_size}")
            return False
        self.queue.put(item)
        logger.debug(f"Added {item.token} to the queue. ~{self.queue.qsize()}/{self.max_size}")
        return True

    def get(self, timeout: float = None) -> RenderItem:
        try:
            item = self.queue.get(timeout=timeout)
        except Empty:
            return None
        return item
    
    def qsize(self) -> int:
        return self.queue.qsize()