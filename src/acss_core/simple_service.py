import json
from abc import abstractmethod
from typing import Optional, Tuple
import requests
import time

from confluent_kafka import TIMESTAMP_NOT_AVAILABLE

from .logger import init_logger
from .config import KAFKA_SERVER_URL
from .service import Service
from .event_utls.consumer import consume
from .messages.message import Headers
from .messages.simple_service_message import SimpleServiceMessage
from .topics import AGENT_EVENTS, RECONFIG_TOPIC, SERVICE_INPUT_TOPIC
from .messages.update_message_types import *
from .messages.agent_result_message import AgentResultMessage
from .adapter.MsgBusWriter import MessageBusWriter

_logger = init_logger(__name__)


class SimpleService(Service):
    def __init__(self, name, read, is_sync=False, simulations=[]):
        super().__init__(name)
        self.write = MessageBusWriter(self.type, simulations, is_sync=is_sync)
        self.read_hook = read
        self.current_package_id = None
        self.simulations = simulations
        self.__stop_consumer_loop = False

    @abstractmethod
    def proposal(self, params: Optional[dict]) -> Optional[Tuple[dict, int, str]]:
        """[summary]
        Function that will be called when the Agent is triggered.
        :param params: Optional parameter for configuration or setting internal parameter
        :type params: Optional[dict]
        :return: A tuple consisting of a dictionary which is containing the result of the Agent that will be stored,
        an error code and and error message. All parameter are optional and can be set to None if not needed.
        :rtype: Optional[Tuple[dict, int, str]]
        """
        pass

    def read(self, channel, device, _property, **kwargs):
        if self.read_hook is None:
            raise KeyError("read_hook isn't set.")
        return self.read_hook(channel, device, _property, **kwargs)

    def reconfig_event(self, msg):
        """[summary]
        Function that can be overloaded by the concret service to reconfig without restarting
        :param msg: [description]
        :type msg: [type]
        """
        pass

    def _does_local_storage_exists(self):
        # ToDo: Not implemented yet
        return False

    def stop(self):
        self.__stop_consumer_loop = True
        super().stop()
        _logger.debug(f"exit stop on service {self.name}")

    def __consumer_stop_hook(self):
        return self.__stop_consumer_loop

    def post_init(self):
        for msg in consume([SERVICE_INPUT_TOPIC, RECONFIG_TOPIC], stop_hook=self.__consumer_stop_hook, timeout_poll=0.1, group_id=self.type, bootstrap_server=KAFKA_SERVER_URL):
            self.service_input_handler(msg)

        _logger.debug("end consuming")

    def _service_input_event_handler(self, msg):
        data = SimpleServiceMessage.deserialize([msg])
        result = self.proposal(data.params)
        # store message
        agent_result, error_code, error_message = result if result != None else ({}, 0, 'None')
        if self._does_local_storage_exists():
            # TODO: store the agent_result in local db and set agent_result to db url
            pass
        self.producer.async_produce(AGENT_EVENTS, AgentResultMessage(agent_result, error_message, self.write.send_messages, error_code).serialize(),
                                    Headers(package_id=self.current_package_id, source=self.type, msg_type=self.type))
        self.write.reset()

        _logger.debug(f"send result message to topic '{AGENT_EVENTS}'")

    def service_input_handler(self, msg, **kwargs):
        timestamp_type, timestamp = msg.timestamp()
        if timestamp_type == TIMESTAMP_NOT_AVAILABLE:
            _logger.debug(f"[{self.name}] receive a message without a timestamp")
            return
        headers = Headers.from_kafka_headers(msg.headers())
        self.current_package_id = headers.package_id
        #self.machine_adapter.active_package_id = headers.package_id
        _logger.debug(f'[{self.name}] call service_input_handler receive headers: {str(headers)}')
        _logger.debug(f"Received message from topic '{msg.topic()}'")

        if headers.is_message_for(self.type) or headers.is_message_for(self.name):
            if msg.topic() == SERVICE_INPUT_TOPIC:
                self._service_input_event_handler(msg)

            elif msg.topic() == RECONFIG_TOPIC:
                _logger.debug(f"reconfig message received")
                config_data = json.loads(msg.value().decode('utf-8'))
                self.reconfig_event(config_data)
                self.producer.async_produce(AGENT_EVENTS, AgentResultMessage(config_data, "None", [self.current_package_id], 0).serialize(),
                                            Headers(package_id=self.current_package_id, source=self.type, msg_type=self.type))
                return

        _logger.debug(f'[{self.name}] end service_input_handler')
