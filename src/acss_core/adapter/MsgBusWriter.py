import time
import requests
from acss_core.config import OBSERVER_URL
from acss_core.simulation.MachineService import MachineService
from ..messages.update_message_types import WriteCommand, SetMachineMessage
from ..topics import PROPOSAL_TOPIC
from ..messages.message import Headers
from ..logger import init_logger
from ..event_utls.producer import Producer
from ..utils.utils import generate_unique_id

_logger = init_logger(__name__)


class MessageBusWriter:
    def __init__(self, service_type, simulations=[], is_sync=False, producer=None):
        self.producer = Producer() if producer is None else producer
        self.cmd_queue = []
        self.service_type = service_type
        self.simulations = simulations
        self._is_sync = is_sync
        self.send_messages = []

    def reset(self):
        self.send_messages = []

    def commit(self):
        data = SetMachineMessage(is_last_message=False, write_commands=self.cmd_queue)
        package_id = generate_unique_id()
        self.producer.sync_produce(PROPOSAL_TOPIC, data.serialize(), Headers(package_id=package_id, source=self.service_type, msg_type=self.service_type))
        self.cmd_queue = []
        self.send_messages.append(package_id)

        if self._is_sync:
            self.wait_for(package_id)

    def __call__(self, channel, device, _property, commit=True, **kwargs):
        if commit:
            self.cmd_queue.append(WriteCommand(channel=channel, device_name=device, property=_property, params=kwargs))
            return

        data = SetMachineMessage(is_last_message=False, write_commands=[WriteCommand(channel=channel, device_name=device, property=_property, params=kwargs)])
        package_id = generate_unique_id()
        self.producer.sync_produce(PROPOSAL_TOPIC, data.serialize(), Headers(package_id=package_id, source=self.service_type, msg_type=self.service_type))
        self.send_messages.append(package_id)
        if self._is_sync:
            self.wait_for(package_id)
        return package_id

    def wait_for(self, package_id):
        if len(self.simulations) > 0:
            for sim in self.simulations:
                res = self._wait_for_write(package_id, sim)
                if res is None:
                    raise TimeoutError(f"timeout reached for package_id={package_id} and service_type={sim}.")
        else:
            res = self._wait_for_write(package_id, MachineService.__name__)
            if res is None:
                raise TimeoutError(f"timeout reached for package_id={package_id} and service_type={MachineService.__name__}.")

    def _wait_for_write(self, package_id, service_type, timeout=30, poll_time=0.05):
        res = requests.get(f'http://{OBSERVER_URL}/find/{package_id}/{service_type}')
        if res.status_code == 200:
            return res.json()
        time_counter = 0.0
        while(res.status_code == 202):
            time.sleep(poll_time)
            time_counter += poll_time
            res = requests.get(f'http://{OBSERVER_URL}/find/{package_id}/{service_type}')
            if res.status_code == 200:
                _logger.debug(f"service name = {service_type}")
                return res.json()
            if time_counter >= timeout:
                _logger.error(f"timeout reached for package_id={package_id} and service_type={service_type}.")
                return None
            poll_time *= 2.0
