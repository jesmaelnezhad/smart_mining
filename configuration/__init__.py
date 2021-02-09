from configuration import constants as consts
from configuration import configs as configs
from configuration.configs import SimulationConfigs, RealtimeConfigs, RuntimeMode, RUNTIME_MODE, SIMULATION_CONFIGS, \
    REALTIME_CONFIGS


def is_simulation_run():
    return RUNTIME_MODE == RuntimeMode.SIMULATION


EXECUTION_CONFIGS = None

if is_simulation_run():
    EXECUTION_CONFIGS = SIMULATION_CONFIGS
else:
    EXECUTION_CONFIGS = REALTIME_CONFIGS
