from configuration import constants as consts
from configuration import configs as configs

if configs.RUNTIME_CONFIGS['mode'] == configs.RuntimeMode.SIMULATION:
    configs.EXECUTION_CONFIGS = configs.SIMULATION_CONFIGS
elif configs.RUNTIME_CONFIGS['mode'] == configs.RuntimeMode.REALTIME:
    configs.EXECUTION_CONFIGS = configs.REALTIME_CONFIGS
