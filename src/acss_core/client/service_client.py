from typing import List
from .kafka_client import KafkaPipeClient, ServiceId
from ..messages.agent_result_message import AgentResultMessage


class ServiceClient():
    def __init__(self, pipe_client: KafkaPipeClient, names: List[str], type: str,  info: str) -> None:
        self.pipe = pipe_client
        self.info = "No info test." if info == None else info
        self.type = type
        self.names = names

    def stop(self, names=None):
        supspending_services = self.names if names is None else names
        for name in supspending_services:
            self.pipe.stop_service(name)


class MachineClient(ServiceClient):
    def __init__(self, names: List[str], pipe_client: KafkaPipeClient, type: str,  info: str) -> None:
        super().__init__(pipe_client, names, type, info)

    def is_processed(self, service_id: ServiceId):
        return False if self.pipe.wait_for_simulation(service_id, self.type) is None else True


class AgentClient(ServiceClient):
    def __init__(self, pipe_client: KafkaPipeClient, names: List[str], type: str,  info: str) -> None:
        super().__init__(pipe_client, names, type, info)
        self._service_id = None

    def reconfig(self, config, sync=False):
        p_id = self.pipe.reconfig(names=[self.type], config_data=config)
        if sync:
            return self.pipe.get_service_results(ServiceId(p_id, self.type))

    def run(self, params=None, wait_for_sims=[]):
        self._service_id = self.pipe.run_service(self.type, params)
        if len(wait_for_sims) > 0:
            agt_res = self.pipe.get_service_results(self._service_id)
            ids = agt_res[0].send_messages
            for sim in wait_for_sims:
                agt_result = self.pipe._get_results_from_observer(ids, sim, timeout=30, poll_time=0.05)
                if agt_result is None:
                    raise TimeoutError()
            return None
        return self._service_id

    def get_result(self):
        return self.pipe.get_service_results(self._service_id)[0]
