from typing import Dict
from time import time
import threading
import logging

from src.render_queue import RenderQueue, RenderItem
from .avg_render_time import AvgRenderTimer

logger = logging.getLogger(__name__)

class ThreadManager:
    def __init__(
        self, 
        threads: int = 2,
        max_queue_size: int = 1_000,
        thread_wait_timeout: float = 2.0
    ) -> None:
        self.queue = RenderQueue(max_queue_size)
        self.item_index: Dict[str, RenderItem] = {}
        self.render_time_history = AvgRenderTimer(10)
        self.thread_timeout = thread_wait_timeout
        self.thread_count = threads
        self.continue_running = True
        self.threads_started = False

        logger.info(f"ThreadManager: starting {self.thread_count} threads...")
        for _ in range(self.thread_count):
            threading.Thread(
                target=self.__worker
            ).start()

    def add_render_task(self, item: RenderItem) -> bool:
        result = self.queue.put(item)
        if result: 
            item.status = 'Queued'
            self.item_index[item.token] = item
        return result
    
    def __worker(self) -> None:
        main_thread = threading.main_thread()
        thread_name = threading.current_thread().getName() + \
                      str(threading.current_thread().native_id)
        logger.info(f"{thread_name} started, main thread: {main_thread.name}")
        logger.debug(f"{thread_name}: local threads: {threading.enumerate()}")
        while main_thread.is_alive() and self.continue_running:
            try:
                item = self.queue.get(timeout=self.thread_timeout)
                if isinstance(item, RenderItem):
                    logger.info(f"{thread_name} rendering {item.token}")
                    start_time = time()
                    item.render()
                    time_taken = time() - start_time
                    del self.item_index[item.token]
                    self.render_time_history.add(time_taken)
                    logger.info(f"{thread_name} finished {item.token}")
                else:
                    logger.debug(f"{thread_name} queue empty, waiting")
            except Exception as e:
                logger.error(f"{thread_name}: {e}")
        logger.info(f"{thread_name} ended.\n" + \
                     f"main_thread.alive()={main_thread.is_alive()}\n" + \
                     f"continue_running={self.continue_running}")

    def stop_threads_safe(self) -> None:
        self.continue_running = False
        # delete all tpm files if left
        # TODO
