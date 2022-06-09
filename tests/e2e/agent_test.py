import time

import numpy as np
import pytest

from src.acss_core.client.kafka_client import KafkaPipeClient
from adapter.petra.PetraMachineAdapter import PetraMachineAdapter
from src.acss_core.client.utils import get_services


def test_trigger_agent():
    with KafkaPipeClient() as pipe:
        adapter = PetraMachineAdapter.create_for_simulation()
        is_started = pipe.wait_for_services(names=['OrbitAgent', 'PetraOrbitSimulation'])
        assert is_started
        # remove this

        agents, _ = get_services()
        agents['OrbitAgent'].run(wait_for_sims=['PetraOrbitSimulation'])

        x, y, _ = adapter.get_bpms()
        before_BPM = 0 - np.append(np.array(x), np.array(y))

        agents['OrbitAgent'].run(wait_for_sims=['PetraOrbitSimulation'])

        after_x, after_y, _ = adapter.get_bpms()
        after_BPM = 0 - np.append(after_x, after_y)

        before_average = np.average(before_BPM)
        after_average = np.average(after_BPM)

        # more than 50% of the measurement points have to be different.
        assert (np.isclose(after_average - before_average, 0) == False).size > after_average.size / 2


def test_read_agent_result():
    with KafkaPipeClient() as pipe:
        is_started = pipe.wait_for_services(names=['SillyMeasureAgent'])
        assert is_started

        agents, _ = get_services()
        agents['SillyMeasureAgent'].run()

        agt_result = agents['SillyMeasureAgent'].get_result()
        agt_result.result['some_data']
        assert np.isclose(agt_result.result['some_data'], np.array([i for i in range(3)])).all()


def test_orbit_correction():
    with KafkaPipeClient() as pipe:
        adapter = PetraMachineAdapter.create_for_simulation()
        is_started = pipe.wait_for_services(names=['OrbitCorrAgent', 'SetTableService', 'PetraOrbitSimulation'])
        assert is_started

        agents, _ = get_services()

        machine_adapter = PetraMachineAdapter.create_for_simulation()

        vcor_names = machine_adapter.get_vcor_device_names()
        hcor_names = machine_adapter.get_hcor_device_names()
        np.random.seed(3)
        vcor_val = [np.random.rand()*1e-4 for _ in range(len(vcor_names))]
        hcor_val = [np.random.rand()*1e-4 for _ in range(len(hcor_names))]

        agents['SetTableService'].run(params={'data': [{'names': vcor_names,  'values': vcor_val, 'type': 'vcor'},
                                                       {'names': hcor_names,  'values': hcor_val, 'type': 'hcor'}]},
                                      wait_for_sims=['PetraOrbitSimulation'])

        before_x, _, _ = adapter.get_bpms()

        print(f'before_x: {np.std(before_x)}')

        agents['OrbitCorrAgent'].run(wait_for_sims=['PetraOrbitSimulation'])

        after_x, _, _ = adapter.get_bpms()

        before_std = np.std(before_x)
        after_std = np.std(after_x)

        assert after_std < before_std


@pytest.mark.skip()
def test_speed_agent():
    with KafkaPipeClient() as pipe:
        adapter = PetraMachineAdapter.create_for_simulation()
        is_started = pipe.wait_for_services(names=['OrbitCorrAgent', 'SetTableService', 'PetraOrbitSimulation'])
        assert is_started

        machine_adapter = PetraMachineAdapter.create_for_simulation()

        vcor_names = machine_adapter.get_vcor_device_names()
        hcor_names = machine_adapter.get_hcor_device_names()

        vcor_val = [np.random.rand()*1e-4 for _ in range(len(vcor_names))]
        hcor_val = [np.random.rand()*1e-4 for _ in range(len(hcor_names))]

        agents, _ = get_services()

        id = agents['SetTableService'].run(params={'data': [{'names': vcor_names,  'values': vcor_val, 'type': 'vcor'},
                                                            {'names': hcor_names,  'values': hcor_val, 'type': 'hcor'}]},
                                           wait_for_sims=['PetraOrbitSimulation'])

        before_x, _, _ = adapter.get_bpms()

        print(f'before_x: {np.std(before_x)}')

        start = time.time()
        agents['OrbitCorrAgent'].run(wait_for_sims=['PetraOrbitSimulation'])
        end = time.time()
        t = end - start
        assert t < 0.200
