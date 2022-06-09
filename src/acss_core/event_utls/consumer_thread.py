import threading

from ..logger import logging
from .consumer import consume

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


class ConsumerThread(threading.Thread):
    def __init__(self, topics, group_id, bootstrap_server, message_handler, consumer_started_hook, **kwargs):
        super(ConsumerThread, self).__init__()
        self.lock = threading.Lock()
        self.bootstrap_server = bootstrap_server
        self.name = group_id
        #        self.daemon = True
        self._stop_event = threading.Event()
        self._ready_event = threading.Event()
        self.message_handlers = [message_handler] if message_handler else []
        self.consumer_started_hook = consumer_started_hook if consumer_started_hook else None
        self.topics = topics

        self.group_id = group_id
        self.kwargs = kwargs

    def stop(self):
        self._stop_event.set()

    def wait_until_ready(self):
        self._ready_event.wait()

    def restart(self):
        self._stop_event.clear()

    def stopped(self):
        return self._stop_event.is_set()

    def subscribe(self, msg_handler):
        with self.lock:
            self.message_handlers.append(msg_handler)

    def unsubscribe(self, msg_handler):
        func_id = id(msg_handler)
        for idx, active_msg_handler in enumerate(self.message_handlers):
            if func_id == id(active_msg_handler):
                with self.lock:
                    self.message_handlers.pop(idx)
                return

    def run(self):
        def thread_started(msg):
            if not self._ready_event.is_set():
                self._ready_event.set()

        for msg in consume(topics=self.topics, timeout_poll=0.1, group_id=self.group_id, consumer_started_hook=self.consumer_started_hook, all_msg_hook=thread_started, stop_hook=self.stopped, bootstrap_server=self.bootstrap_server):
            with self.lock:
                for message_handler in self.message_handlers:
                    message_handler(msg, **self.kwargs)
