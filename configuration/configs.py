import yaml
import logging
from enum import Enum

from configuration.constants import MINUTE_SECONDS
from utility.datetime_helpers import datetime_string_to_timestamp

config_raw_data = None
with open("files/config.yaml") as config_file:
    config_raw_data = yaml.safe_load(config_file)

config_raw_realtime = config_raw_data['realtime']
config_raw_simulation = config_raw_data['simulation']


class RuntimeMode(Enum):
    SIMULATION = 1
    REALTIME = 2


RUNTIME_MODE = RuntimeMode.SIMULATION if config_raw_data['runtime_mode'] == "simulation" else RuntimeMode.REALTIME


class RealtimeConfigs:
    def __init__(self, entries):
        self.read_entries(entries)

    def read_entries(self, entries):
        for k, v in entries.items():
            if str(v).startswith("|||"):
                self.__dict__[k] = v[3:]
            else:
                self.__dict__[k] = eval(v)


class SimulationConfigs(RealtimeConfigs):
    def __init__(self, realtime_entries, simulation_entries):
        super().__init__(realtime_entries)
        self.read_entries(simulation_entries)


REALTIME_CONFIGS = RealtimeConfigs(config_raw_realtime)
SIMULATION_CONFIGS = SimulationConfigs(config_raw_realtime, config_raw_simulation)
