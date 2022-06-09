import numpy as np

from src.acss_core.client.kafka_client import KafkaPipeClient
from adapter.petra.PetraMachineAdapter import PetraMachineAdapter


def test_get_and_set_all_correctors():
    with KafkaPipeClient() as pipe:
        is_started = pipe.wait_for_services(names=['SetTableService'], timeout=3)
        assert is_started
        machine_adapter = PetraMachineAdapter.create_for_simulation()
        h_cor_names = machine_adapter.get_hcor_device_names()
        v_cor_names = machine_adapter.get_vcor_device_names()
        h_cor_values = [float(i) for i, _ in enumerate(h_cor_names)]
        v_cor_values = [i*0.1 for i, _ in enumerate(v_cor_names)]
        machine_adapter.set_hcors(h_cor_names, h_cor_values)
        machine_adapter.set_vcors(v_cor_names, v_cor_values)

        h_cors = machine_adapter.get_hcors(h_cor_names)
        v_cors = machine_adapter.get_vcors(v_cor_names)
        for name, truth_val, set_val in zip(v_cor_names, v_cor_values, v_cors):
            if not name.startswith(('PKPDA', 'PKPDD')):
                assert np.isclose(truth_val, set_val)

        for name, truth_val, set_val in zip(h_cor_names, h_cor_values, h_cors):
            if not name.startswith(('PKPDA', 'PKPDD')):
                assert np.isclose(truth_val, set_val)


def test_petra_simulation_adapter_set_twiss():
    with KafkaPipeClient() as pipe:
        is_started = pipe.wait_for_services(names=['SetTableService'], timeout=3)
        assert is_started
        machine_adapter = PetraMachineAdapter.create_for_simulation()
        names = machine_adapter.get_bpm_device_names()
        twiss_mat = [[float(i+j) for i in range(4)] for j in range(len(names))]
        machine_adapter.set_twiss(names, twiss_mat)
        res_twiss_params = machine_adapter.get_twiss(names)

        assert np.all(np.isclose(twiss_mat, res_twiss_params))


def test_petra_simulation_adapter_set_machine_params():
    with KafkaPipeClient() as pipe:
        is_started = pipe.wait_for_services(names=['SetTableService'], timeout=3)
        assert is_started
        machine_adapter = PetraMachineAdapter.create_for_simulation()
        names = ['Q_x', 'Q_y']
        vals = [1.0, 2.0]
        machine_adapter.set_machine_params(names, vals)
        params = machine_adapter.get_machine_params()
        print(params)

        assert np.all(np.isclose(params['Q_x'], vals[0]))
        assert np.all(np.isclose(params['Q_y'], vals[1]))


def test_petra_simulation_adapter_set_get_in_service():
    with KafkaPipeClient() as pipe:
        adapter = PetraMachineAdapter.create_for_simulation()
        is_started = pipe.wait_for_services(names=['SetTableService'], timeout=3)
        assert is_started
        names = ["PKH_NR_86", "PKH_NR_101", "PKH_NR_103"]
        values = [111.1, 222.2, 333.3]

        id = pipe.run_service('SetTableService', params={'data': [{'names': names, 'values': values, 'type': 'hcor'}]})

        pipe.wait_for_simulation(id, 'PetraOrbitSimulation')

        h_cors_names = adapter.get_hcor_device_names()
        h_cors = adapter.get_hcors(adapter.get_hcor_device_names())

        for name, val in zip(names, values):
            assert h_cors[h_cors_names.index(name)] == val
