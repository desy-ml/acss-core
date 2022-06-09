import requests
import pytest

from src.acss_core.client.kafka_client import KafkaPipeClient
from src.acss_core.utils.utils import wait_until_server_is_online
from src.acss_core.client.utils import get_services


def test_service_does_not_exists():
    wait_until_server_is_online("http_proxy:5002", None)
    # start to services
    res = requests.get('http://http_proxy:5002/start/test_1/fake_name/sim')
    assert res.status_code == 400


@pytest.mark.skip()
def test_start_stop_service():
    with KafkaPipeClient() as pipe:
        #is_started = pipe.wait_for_services(names=['PetraOrbitSimulation'])
        #assert is_started

        wait_until_server_is_online("http_proxy:5002", None)

        # start to services
        #res = requests.get('http://http_proxy:5002/start/test_1/set_table_service/sim')
        res = requests.get('http://http_proxy:5002/start/test_1/orb_cor_agent/sim')
        assert res.status_code == 200
        is_started = pipe.wait_for_services(names=['test_1'])
        assert is_started
        res = requests.get('http://http_proxy:5002/start/test_2/orb_cor_agent/sim')
        assert res.status_code == 200
        # check if services are started
        is_started = pipe.wait_for_services(names=['test_2'])
        assert is_started

        agents, _ = get_services()

        # check if services are stopped
        agents['OrbitCorrAgent'].stop(['test_1', 'test_2'])

        is_stopped = pipe.wait_for_services(names=['test_1', 'test_2'], option='shutdown')
        assert is_stopped
