from typing import Tuple, Dict
from .kafka_client import KafkaPipeClient
from .service_client import AgentClient, MachineClient


def get_services() -> Tuple[Dict[str, AgentClient], Dict[str, MachineClient]]:
    pipe = KafkaPipeClient()
    agents = {}
    machines = {}

    services_sorted_by_type = {}
    running_services = pipe.get_running_service_info()
    # Sort by service type
    for name, info in running_services.items():
        s_type = info['type']
        found_s_type = services_sorted_by_type.get(s_type)
        if found_s_type is not None:
            found_s_type.append(name)
        else:
            services_sorted_by_type[s_type] = [name]
    for s_type, names in services_sorted_by_type.items():

        first_service = running_services[names[0]]

        if first_service['cat'] == 'Simulation':
            machines[s_type] = MachineClient(pipe_client=pipe, names=names, info=first_service['info'], type=first_service['type'])
        else:
            agents[s_type] = AgentClient(pipe_client=pipe, names=names, info=first_service['info'], type=first_service['type'])
    return agents, machines
