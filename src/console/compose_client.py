import os
import subprocess
from enum import Enum
from typing import Optional

from src.acss_core.logger import init_logger
from src.acss_core.config import ACSS_CONFIG_FILEPATH

PROFILE = "pipeline"

ACSS_CONFIG_FILEPATH_HOST = os.environ.get("ACSS_CONFIG_FILEPATH_HOST")

_logger = init_logger(__name__)


class DOCKER_COMPOSE_FILTER_BY_STATUS(Enum):
    RUNNING = 'running'
    RESTARTING = 'restarting'
    PAUSED = 'paused'
    STOPPED = 'stopped'


class DockerComposeClient():
    def __init__(self, max_num_of_container: int = 64) -> None:
        self.max_num_of_container = max_num_of_container
        self.host_config_path = os.environ.get("HOST_CONFIG_PATH")

    def get_services(self, filter: Optional[DOCKER_COMPOSE_FILTER_BY_STATUS] = None):
        filter_option = f"--filter status={filter.value}" if filter != None else ""
        ps_str = subprocess.check_output(f"docker-compose -p {PROFILE} ps {filter_option} --services".split(), timeout=10).decode('utf-8').strip()
        split = ps_str.split('\n')
        return split

    def run_service(self, name: str, service_type: str, mode: str):
        running_container = DockerComposeClient.get_services(DOCKER_COMPOSE_FILTER_BY_STATUS.RUNNING)
        if len(running_container) == self.max_num_of_container:  # no free service where script can run
            _logger.warning(f"Maximum running service containers of {self.max_num_of_services} reached. It is not possible to start more service container.")
            return False
        #subprocess.run(args=f'docker-compose -p {PROFILE} run --rm --no-deps -e SERVICE_NAME={name} -e SERVICE_MODE={mode} {service_type}'.split())
        command = f'docker-compose -p {PROFILE} run --rm --no-deps -e SERVICE_NAME={name} -e SERVICE_MODE={mode} -e ACSS_CONFIG_FILEPATH={ACSS_CONFIG_FILEPATH} -v {ACSS_CONFIG_FILEPATH_HOST}:{ACSS_CONFIG_FILEPATH} {service_type}'
        print(command)
        subprocess.Popen(command.split())
        return True


if __name__ == "__main__":
    compose_client = DockerComposeClient()
    print(DockerComposeClient.get_services(filter=DOCKER_COMPOSE_FILTER_BY_STATUS.RUNNING))
    print(f"active service containers: {compose_client.active_service_container} max num of services: {compose_client.max_num_of_services}")
    compose_client.start_service_container(num=4)
    print(f"active service containers: {compose_client.active_service_container} max num of services: {compose_client.max_num_of_services}")
