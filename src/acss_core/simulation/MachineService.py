from typing import List, Dict

from confluent_kafka import TIMESTAMP_NOT_AVAILABLE

from ..service import Service
from ..logger import init_logger
from ..topics import MACHINE_EVENTS, PROPOSAL_TOPIC
from ..messages.message import Headers
from ..config import KAFKA_SERVER_URL
from ..messages.update_message_types import SetMachineMessage, UpdateMessage
from ..event_utls.consumer import consume

_logger = init_logger(__name__)


class MachineService(Service):
    def __init__(self, name, write, read):
        super().__init__(name)
        self.write = write
        self.read = read
        self.updated_devices: Dict[int, List[List[str]]] = {}

    def simulate(self):
        pass

    def post_init(self):
        for msg in consume([PROPOSAL_TOPIC], timeout_poll=0.1, group_id=self.type, bootstrap_server=KAFKA_SERVER_URL):
            self.machine_input_handler(msg)

    def machine_input_handler(self, msg, **kwargs):
        timestamp_type, timestamp = msg.timestamp()
        if timestamp_type == TIMESTAMP_NOT_AVAILABLE:
            _logger.debug(f"[{self.name}] receive a message without a timestamp")
            return
        headers = Headers.from_kafka_headers(msg.headers())
        received_package_id = headers.package_id
        _logger.debug(f'[{self.name}] call machine_input_handler receive headers: {str(headers)}')

        message = SetMachineMessage.deserialize([msg])

        _updated_devices = []
        for write_command in message.write_commands:
            self.write(write_command.channel, write_command.device_name, write_command.property, **write_command.params)
            _updated_devices.append(f"{write_command.channel}/{write_command.device_name}")

        self.updated_event(package_id=received_package_id,
                           msg=UpdateMessage(source=headers.msg_type, updated=_updated_devices))

        _logger.debug(f"[{self.name}] end machine_input_handler")

    def updated_event(self, package_id, msg):
        self.producer.sync_produce(MACHINE_EVENTS, msg.serialize(), Headers(package_id=package_id, source=self.type))
