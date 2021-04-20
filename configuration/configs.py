import os
import sys

import yaml
import logging
from enum import Enum

from configuration.constants import MINUTE_SECONDS, HOUR_SECONDS, DAY_SECONDS, WEEK_SECONDS
from utility.datetime_helpers import datetime_string_to_timestamp

config_raw_data = None
with open("files/config.yaml") as config_file:
    config_raw_data = yaml.safe_load(config_file)

config_raw_realtime = config_raw_data['realtime']
config_raw_simulation = config_raw_data['simulation']


def evaluate_value(value):
    if value.startswith("|||"):
        return value[3:]
    elif value.startswith("!!"):
        return custom_evaluation(value)
    else:
        return eval(value)


def custom_evaluation(value):
    if value.startswith("!!timestamp!"):
        return datetime_string_to_timestamp(datetime_string=evaluate_value(value[len("!!timestamp!"):]))


class RuntimeMode(Enum):
    SIMULATION = 1
    REALTIME = 2


RUNTIME_MODE = evaluate_value("RuntimeMode." + config_raw_data['runtime_mode'])


class RealtimeConfigs:
    def __init__(self, entries):
        self.read_entries(entries)
        self.project_root_directory = os.path.dirname(sys.modules['__main__'].__file__)
        self.execution_identifier = "realtime-{0}".format(int(datetime_string_to_timestamp(datetime_string=None)))

    def read_entries(self, entries):
        for k, v in entries.items():
            self.__dict__[k] = evaluate_value(v)


class SimulationConfigs(RealtimeConfigs):
    def __init__(self, realtime_entries, simulation_entries):
        super().__init__(realtime_entries)
        self.read_entries(simulation_entries)
        self.execution_identifier = "simulation-{0}".format(int(datetime_string_to_timestamp(datetime_string=None)))


REALTIME_CONFIGS = RealtimeConfigs(config_raw_realtime)
SIMULATION_CONFIGS = SimulationConfigs(config_raw_realtime, config_raw_simulation)
