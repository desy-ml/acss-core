from typing import List, Dict


from ..service import Service
from ..logger import init_logger
from ..topics import SIMULATION_EVENTS
from ..messages.message import Headers
from ..messages.update_message_types import UpdateMessage
from src.acss_core.event_utls.consumer import consume
from ..utils.TimerThread import TimerThread

_logger = init_logger(__name__)


class TimedSimService(Service):
    def __init__(self, name, write, read, time: int):
        super().__init__(name)
        self.category = 'Simulation'
        self.read = read

        self._write = write
        self._updated_channels = []

        self.updated_devices: Dict[int, List[List[str]]] = {}
        self._thread = TimerThread(time, self.simulate)

    def write(self, channel: str, device: str, _property, **kwargs):
        self._updated_channels.append(channel)
        self._write(channel, device, _property, **kwargs)

    def stop(self):
        super().stop()
        self._thread.stop()
        self._thread.join()

    def _simulate(self):
        self.simulate()
        self.sim_updated_event(package_id='None',
                               msg=UpdateMessage(source=self.name, updated=self._updated_channels))

    def simulate(self):
        pass

    def post_init(self):
        self._thread.start()
        self._thread.join()

    def sim_updated_event(self, package_id, msg):
        self.producer.sync_produce(SIMULATION_EVENTS, msg.serialize(), Headers(package_id=package_id, source=self.type))
