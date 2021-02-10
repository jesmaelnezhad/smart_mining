from time import sleep
from threading import Lock

from configuration import EXECUTION_CONFIGS
from clock.tick_performer import TickPerformer
from utility.datetime_helpers import datetime_string_to_timestamp

clock_real_tick_time_interval = EXECUTION_CONFIGS.clock_timestamp_increase_per_tick
clock_tick_duration = EXECUTION_CONFIGS.clock_tick_duration


def calculate_tick_duration_from_sleep_duration(sleep_duration):
    if clock_real_tick_time_interval is None:
        return sleep_duration
    return (clock_tick_duration * sleep_duration) / clock_real_tick_time_interval


class Clock(TickPerformer):
    def __init__(self):
        super().__init__()
        self.timestamp_of_now = EXECUTION_CONFIGS.clock_start_timestamp
        self.tick_number = 0
        self.timestamp_of_now_safe_mutex = Lock()

    def read_timestamp_of_now(self):
        if clock_real_tick_time_interval is None:
            return int(datetime_string_to_timestamp(datetime_string=None))
        self.timestamp_of_now_safe_mutex.acquire()
        try:
            return int(self.timestamp_of_now)
        finally:
            self.timestamp_of_now_safe_mutex.release()

    def write_timestamp_of_now(self, new_value):
        self.timestamp_of_now_safe_mutex.acquire()
        try:
            self.timestamp_of_now = new_value
        finally:
            self.timestamp_of_now_safe_mutex.release()

    def run(self, should_stop):
        if clock_real_tick_time_interval is None:
            return
        while True:
            if should_stop():
                break
            sleep(clock_tick_duration)
            next_ts_of_now_value = self.read_timestamp_of_now() + clock_real_tick_time_interval
            self.write_timestamp_of_now(next_ts_of_now_value)

    def is_a_daemon(self):
        return True
