import logging
from enum import Enum

from configuration.constants import MINUTE_SECONDS
from utility.datetime_helpers import datetime_string_to_timestamp


class RuntimeMode(Enum):
    SIMULATION = 1
    REALTIME = 2


RUNTIME_CONFIGS = {
    "mode": RuntimeMode.SIMULATION,
}

SIMULATION_CONFIGS = {
    "tick_execution_interval_seconds": 0.5,
    "tick_duration_seconds": 10 * MINUTE_SECONDS,
    "execution_start_timestamp": datetime_string_to_timestamp("11/22/2019-23:16:24"),
    "log_level": logging.DEBUG,
}

REALTIME_CONFIGS = {
    "tick_execution_interval_seconds": 10 * MINUTE_SECONDS,
    "tick_duration_seconds": 10 * MINUTE_SECONDS,
    "execution_start_timestamp": datetime_string_to_timestamp(datetime_string=None),
    "log_level": logging.INFO,
}

# Configuration object used for execution
EXECUTION_CONFIGS = None
