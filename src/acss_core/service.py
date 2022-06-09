import json
import typing
import time
import requests
from abc import ABC

from confluent_kafka import TIMESTAMP_NOT_AVAILABLE

from .config import KAFKA_SERVER_URL, REGISTER_URL
from .logger import init_logger
from .utils.utils import wait_until_server_is_online
from .event_utls.consumer_thread import ConsumerThread
from .event_utls.producer import Producer
from .messages.message import Headers
from .topics import CONTROL_TOPIC, MACHINE_EVENTS
from .topics import IS_ALIVE
from .utils.TimerThread import TimerThread
from .messages.message import Headers, AliveMessage

_logger = init_logger(__name__)


class Service(ABC):
    def __init__(self, name, **kwargs):
        self.name: str = name
        self.creation_timestamp = int(
            time.time() * 1000)  # The creation_timestamp is the number of milliseconds since the epoch (UTC).
        self.control_log_consumer = None
        self.producer = None
        self.type = self.__class__.__name__
        self.category = ''
        self.status = "INIT"

    def to_json(self):
        return json.dumps({'name': self.name})

    @classmethod
    def from_json(cls, serialized_service_obj):
        service_obj_json = json.loads(serialized_service_obj)
        name = service_obj_json.get('name')
        if not name:
            raise ValueError('Key name is not in json object.')
        return cls(name)

    def _control_log_handler(self, msg):
        _logger.debug(f"[{self.name}] call _control_log_handler")
        timestamp_type, timestamp = msg.timestamp()
        if timestamp_type == TIMESTAMP_NOT_AVAILABLE:
            _logger.debug(
                f"[{self.name}] receive a message without a timestamp")
            return
        if timestamp < self.creation_timestamp:
            return
        message = json.loads(msg.value().decode('utf-8'))
        _logger.debug(
            f"[{self.name}] call _control_log_handler receive message: {message}")
        command = message.get('command')
        if self.name == message.get('name'):
            if command == "start":
                self.start()
            elif command == "stop":
                self.stop()

    def info(self) -> str:
        return "No info string is defined. The concrete service have to overload info()."

    def _init_alive_thread(self):
        self.producer.wait_until_topics_created([IS_ALIVE], poll_time=1, max_iterations=30)
        self.alive_thread = TimerThread(0.1, self._alive)
        self.alive_thread.start()

    def post_init(self):
        pass

    def _alive(self):
        self.producer.async_produce(topic=IS_ALIVE, value=AliveMessage(info=self.info(), type=self.type, status=self.status, category=self.category).serialize(), headers=Headers(self.name))

    def _register(self):
        wait_until_server_is_online(REGISTER_URL, logger=_logger)
        res = requests.get(f"http://{REGISTER_URL}/register/{self.name}")
        _logger.debug(f"receive status code {res.status_code}")
        _logger.debug(f"error: {res.content}")
        if res.status_code != 200:
            raise Exception(f"Registration of service failed. An service with the name {self.name} is already running/")
        self.producer = Producer()

    def init_local(self):
        _logger.debug(f"[{self.name}] call init_local")

        self._register()

        self.producer = Producer()
        wait_until_server_is_online(url=KAFKA_SERVER_URL, logger=_logger)
        # wait maximal ~30s to let topics be created. Just for startup
        self.producer.wait_until_topics_created([CONTROL_TOPIC, MACHINE_EVENTS], poll_time=1, max_iterations=30)

        self.control_log_consumer = ConsumerThread(topics=[CONTROL_TOPIC], group_id=self.name + "_" + CONTROL_TOPIC,
                                                   bootstrap_server=KAFKA_SERVER_URL,
                                                   message_handler=self._control_log_handler, consumer_started_hook=None)

        self.control_log_consumer.start()
        self.control_log_consumer.wait_until_ready()

        self._init_alive_thread()

        self.status = 'RUNNING'
        self.post_init()
        _logger.debug(f"[{self.name}] exit init_local")

        # wait until stop() is executed.
        self.control_log_consumer.join()

    def stop(self):
        _logger.debug(f"stop is called on service {self.name}")
        if self.alive_thread:
            self.alive_thread.stop()
            self.alive_thread.join()

        # note: .join() is already called in init_local which is called mainThread
        self.control_log_consumer.stop()

    def send(self, topic, message, headers):
        _logger.debug(f"[{self.name}] call send {str(headers)}")
        self.producer.sync_produce(topic=topic,
                                   value=message.serialize(),
                                   headers=headers)

    # used for pickle class
    def __getstate__(self):
        odict = {'name': self.name}
        return odict

    # used for pickle class
    def __setstate__(self, state):
        kwargs = {}
        self.__dict__ = type(self)(state['name'], **kwargs).__dict__
