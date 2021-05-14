from threading import Lock
from time import sleep

from clock.clock import calculate_tick_duration_from_sleep_duration
from clock.tick_performer import TickPerformer
from configuration import EXECUTION_CONFIGS
from data_bank.orders import get_realtime_scope_identifier
from utility.log import logger


class HealthCheckWatcher(TickPerformer):
    """
    Closes all orders if no controller declares liveness periodically
    """
    def __init__(self):
        super().__init__()
        self.tick_duration = calculate_tick_duration_from_sleep_duration(
            EXECUTION_CONFIGS.healthcheck_watcher_sleep_duration)
        self.silent_cycles_threshold = calculate_tick_duration_from_sleep_duration(
            EXECUTION_CONFIGS.healthcheck_watcher_silent_cycles_threshold)
        self.nice_hash_driver = get_realtime_scope_identifier()
        self.silent_cycles_count = 0
        self.silent_cycles_count_mutex = Lock()

    def get_silent_cycles_count(self):
        self.silent_cycles_count_mutex.acquire()
        try:
            return self.silent_cycles_count
        finally:
            self.silent_cycles_count_mutex.release()

    def increment_silent_cycles_count(self):
        self.silent_cycles_count_mutex.acquire()
        try:
            self.silent_cycles_count += 1
        finally:
            self.silent_cycles_count_mutex.release()

    def reset_silent_cycles_count(self):
        self.silent_cycles_count_mutex.acquire()
        try:
            self.silent_cycles_count = 0
        finally:
            self.silent_cycles_count_mutex.release()

    def run(self, should_stop):
        while True:
            if should_stop():
                break
            sleep(self.tick_duration)
            silent_cycles_count = self.get_silent_cycles_count()
            logger("healthcheck/watcher").debug("Silent cycles count is {0}".format(silent_cycles_count))
            if silent_cycles_count > self.silent_cycles_threshold:
                logger("healthcheck").info("Controller has been too silent. Going to panic and close all orders.")
                self.panic()
            else:
                self.increment_silent_cycles_count()

    def panic(self):
        """
        The action that must be done by the healthcheck module if controller stays too silent
        :return: None
        """
        self.nice_hash_driver.close_all_orders()

    def post_run(self):
        logger('healthcheck').info("Healthcheck watcher is terminating.")

    def is_a_daemon(self):
        return True

