import time

import numpy as np

from src.acss_core.client.kafka_client import KafkaPipeClient
from adapter.petra.PetraMachineAdapter import PetraMachineAdapter
from src.acss_core.client.utils import get_services


def test_startup():
    with KafkaPipeClient() as pipe:
        is_started = pipe.wait_for_services(names=['OrbitAgent', 'PetraOrbitSimulation'])
        assert is_started


def test_class_interface():
    with KafkaPipeClient() as pipe:
        is_started = pipe.wait_for_services(names=['OrbitCorrAgent', 'PetraOrbitSimulation'])
    assert is_started

    agents, simulations = get_services()

    agents['OrbitCorrAgent'].reconfig({'n_sv_x': 200, 'n_sv_y': 200, 'x_factor': 1.0, 'y_factor': 0.0})

    agents['OrbitCorrAgent'].run(wait_for_sims=list(simulations.keys()))

    assert simulations.keys() != 0
