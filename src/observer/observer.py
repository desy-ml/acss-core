import json

from confluent_kafka import TIMESTAMP_NOT_AVAILABLE
from acss_core.messages.agent_result_message import AgentResultMessage
from acss_core.topics import ACTIVE_SERVICES_UPDATED_TOPIC, AGENT_EVENTS, MACHINE_EVENTS, SIMULATION_EVENTS

from src.acss_core.logger import init_logger
from src.acss_core.config import KAFKA_SERVER_URL
from src.acss_core.service import Service
from src.acss_core.event_utls.consumer import consume
from acss_core.messages.update_message_types import *
from src.observer.event_database import EventDatabase
from src.acss_core.messages.message import Headers

_logger = init_logger(__name__)


class Observer(Service):
    def __init__(self, name):
        self.db_client = EventDatabase()
        self.running_simulations = set()
        super().__init__(name)

    def post_init(self):
        for msg in consume([MACHINE_EVENTS, SIMULATION_EVENTS, ACTIVE_SERVICES_UPDATED_TOPIC, AGENT_EVENTS], timeout_poll=0.1, group_id=self.type, bootstrap_server=KAFKA_SERVER_URL):
            self.observe(msg)

    def observe(self, msg):
        timestamp_type, timestamp = msg.timestamp()
        if timestamp_type == TIMESTAMP_NOT_AVAILABLE:
            _logger.debug(f"[{self.name}] receive a message without a timestamp")
            return
        headers = Headers.from_kafka_headers(msg.headers())
        _logger.debug(f"receive message. Headers: {headers}")
        if msg.topic() == MACHINE_EVENTS or msg.topic() == SIMULATION_EVENTS:
            self.db_client.insert({"id": headers.package_id, "service_type": headers.source, "data": {}})
        if msg.topic() == ACTIVE_SERVICES_UPDATED_TOPIC:
            self.running_simulations = set()  # reset
            services = json.loads(msg.value().decode('utf-8'))
            for service_name, val in services.items():
                _, _, _, _, category = val
                if category == 'Simulation':
                    self.running_simulations.add(service_name)
            _logger.debug(f"received new list of running simulations. {self.running_simulations}")
        if msg.topic() == AGENT_EVENTS:
            agent_result = AgentResultMessage.deserialize([msg])
            obj_id = self.db_client.insert({"id": headers.package_id, "service_type": headers.source, "data": agent_result.serialize()})


if __name__ == "__main__":
    obs = Observer("obs")
    obs.init_local()
