from typing import List, Dict

from confluent_kafka import TIMESTAMP_NOT_AVAILABLE

from ..service import Service
from ..logger import init_logger
from ..topics import MACHINE_EVENTS, SIMULATION_EVENTS
from ..messages.message import Headers
from ..config import KAFKA_SERVER_URL
from ..messages.update_message_types import UpdateMessage
from ..event_utls.consumer import consume

_logger = init_logger(__name__)


class SimulationService(Service):
    def __init__(self, name, write, read, channels: List = []):
        super().__init__(name)
        self.category = 'Simulation'
        self.read = read

        self._write = write
        self._updated_channels = []

        self.updated_devices: Dict[int, List[List[str]]] = {}
        self.channels = set(channels)
        self.__stop_consumer_loop = False

    def write(self, channel: str, device: str, _property, **kwargs):
        self._updated_channels.append(channel)
        self._write(channel, device, _property, **kwargs)

    def _is_message_for_me(self, msg: UpdateMessage):
        if len(self.channels) == 0:
            return True
        for channel in msg.updated:
            if channel in self.channels:
                return True
        return False

    def simulate(self):
        pass

    def stop(self):
        self.__stop_consumer_loop = True
        super().stop()

    def __consumer_stop_hook(self):
        return self.__stop_consumer_loop

    def post_init(self):
        for msg in consume([MACHINE_EVENTS], stop_hook=self.__consumer_stop_hook, timeout_poll=0.1, group_id=self.type, bootstrap_server=KAFKA_SERVER_URL):
            self.machine_input_handler(msg)

    def machine_input_handler(self, msg, **kwargs):
        timestamp_type, timestamp = msg.timestamp()
        if timestamp_type == TIMESTAMP_NOT_AVAILABLE:
            _logger.debug(f"[{self.name}] receive a message without a timestamp")
            return
        headers = Headers.from_kafka_headers(msg.headers())
        received_package_id = headers.package_id
        _logger.debug(f'[{self.name}] call machine_input_handler receive headers: {str(headers)}')

        message = UpdateMessage.deserialize([msg])

        if self._is_message_for_me(message):
            _logger.debug("simulate...")
            self.simulate()
            self.sim_updated_event(package_id=received_package_id,
                                   msg=UpdateMessage(source=headers.msg_type, updated=self._updated_channels))
            self._updated_channels = []

        _logger.debug(f"[{self.name}] end machine_input_handler")

    def sim_updated_event(self, package_id, msg):
        self.producer.sync_produce(SIMULATION_EVENTS, msg.serialize(), Headers(package_id=package_id, source=self.type))
