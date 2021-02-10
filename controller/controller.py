import random
from time import sleep

from clock import get_clock
from clock.clock import calculate_tick_duration_from_sleep_duration
from clock.tick_performer import TickPerformer
from configuration import EXECUTION_CONFIGS
from utility.log import logger


class Controller(TickPerformer):
    def __init__(self):
        """
        A singleton class that is the controller
        """
        super().__init__()
        self.tick_duration = calculate_tick_duration_from_sleep_duration(EXECUTION_CONFIGS.controller_sleep_duration)

    def run(self, should_stop):
        while True:
            if should_stop():
                break
            sleep(self.tick_duration)
            current_timestamp = get_clock().read_timestamp_of_now()
            logger('controller').debug("Updating analytics at timestamp {0}.".format(current_timestamp))
            pass

    def is_a_daemon(self):
        return False
