from configuration import constants as consts
from configuration import configs as configs
from configuration.configs import SimulationConfigs, RealtimeConfigs, RuntimeMode, RUNTIME_MODE, SIMULATION_CONFIGS, \
    REALTIME_CONFIGS


def is_simulation():
    return RUNTIME_MODE == RuntimeMode.SIMULATION


def is_healthcheck():
    return RUNTIME_MODE == RuntimeMode.HEALTHCHECK


def is_new_simulation_going_to_happen():
    return EXECUTION_CONFIGS.identifier is not None


EXECUTION_CONFIGS = None

if is_simulation():
    EXECUTION_CONFIGS = SIMULATION_CONFIGS
else:
    EXECUTION_CONFIGS = REALTIME_CONFIGS
