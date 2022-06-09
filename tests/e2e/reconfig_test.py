from re import S
import time
from pathlib import Path
import json

from src.acss_core.client.kafka_client import KafkaPipeClient
from adapter.petra.PetraMachineAdapter import PetraMachineAdapter
from src.acss_core.client.utils import get_services


def read_json(path: str):
    for _ in range(3):  # retry 3 times
        try:
            with open(path) as f:
                return json.load(f)
        except json.decoder.JSONDecodeError:  # assuming service is writing json
            time.sleep(0.5)


def test_reconfig_multiple_times():
    with KafkaPipeClient() as pipe:
        adapter = PetraMachineAdapter.create_for_simulation()
        is_started = pipe.wait_for_services(names=['SillyAgent', 'SetTableService', 'PetraOrbitSimulation'], status='RUNNING')
        if not is_started:
            print(pipe.get_running_service_info())

        assert is_started

        # 1. set horizontal correctors to 1.0
        machine_adapter = PetraMachineAdapter.create_for_simulation()

        hcor_names = machine_adapter.get_hcor_device_names()
        hcor_val = [1.0 for _ in range(len(hcor_names))]

        agents, _ = get_services()

        agents['SetTableService'].run(params={'data': [{'names': hcor_names,  'values': hcor_val, 'type': 'hcor'}]},
                                      wait_for_sims=['PetraOrbitSimulation'])

        for val in adapter.get_hcors(hcor_names):
            assert val == 1.0

        # 2. set correctors to 2.0 via agent trigger
        agents['SillyAgent'].reconfig({'factor': 2}, sync=True)
        agents['SillyAgent'].run(wait_for_sims=['PetraOrbitSimulation'])

        for val, name in zip(adapter.get_hcors(hcor_names), hcor_names):
            if not name.startswith(('PKPDA', 'PKPDD')):
                assert val == 2.0
            else:
                assert val == 1.0

        # 3. set correctors to 8.0 via agent trigger
        agents['SillyAgent'].reconfig({'factor': 4}, sync=True)
        agents['SillyAgent'].run(wait_for_sims=['PetraOrbitSimulation'])

        for val, name in zip(adapter.get_hcors(hcor_names), hcor_names):
            if not name.startswith('PKPDA') and not name.startswith('PKPDD'):
                assert val == 8.0
            else:
                assert val == 1.0


def test_config_two_services_same_type():
    with KafkaPipeClient() as pipe:
        adapter = PetraMachineAdapter.create_for_simulation()
        is_started = pipe.wait_for_services(names=['config_to_file_1', 'config_to_file_2'])
        assert is_started

        agents, _ = get_services()

        agents['ConfigToFileService'].reconfig({'test_data': [1, 2, 3]})

        # wait until files created by services.
        is_timeout = False
        time_count = 0
        while(not Path('/tmp/config_to_file_1.json').exists() or not Path('/tmp/config_to_file_2.json').exists()):
            time.sleep(0.05)
            time_count += 0.05
            if time_count > 1.0:
                is_timeout = True
                break

        assert is_timeout == False

        config_1 = read_json('/tmp/config_to_file_1.json')
        config_2 = read_json('/tmp/config_to_file_2.json')

        assert config_1["test_data"] == [1, 2, 3]
        assert config_2["test_data"] == [1, 2, 3]
