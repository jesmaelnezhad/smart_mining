from time import sleep

from clock import get_clock
from clock.clock import calculate_tick_duration_from_sleep_duration
from clock.tick_performer import TickPerformer
from configuration import EXECUTION_CONFIGS
from utility.log import logger


class NiceHashOrder:
    def __init__(self, current_timestamp, order_id):
        self.creation_timestamp = current_timestamp
        self.last_updated_timestamp = self.creation_timestamp
        self.order_id = order_id
        self.price = None
        self.limit = None
        self.last_change_timestamp = None
        self.last_change_requested_limit = None


class NiceHashDriver(TickPerformer):
    def __init__(self):
        """
        A singleton class that is the driver of nicehash
        """
        super().__init__()
        self.tick_duration = calculate_tick_duration_from_sleep_duration(EXECUTION_CONFIGS.nice_hash_sleep_duration)

    def run(self, should_stop):
        while True:
            if should_stop():
                break
            sleep(self.tick_duration)
            current_timestamp = get_clock().read_timestamp_of_now()
            self.perform_tick(current_timestamp)

    def is_a_daemon(self):
        return False

    def perform_tick(self, up_to_timestamp):
        """
        Performs one tick.
        :return: None
        """
        logger('nicehash').warn(
            "Base class of the driver in use! Performing a tick at timestamp {0}.".format(up_to_timestamp))
        pass

    def set_limit(self, up_to_timestamp, order_id, limit):
        """
        Sets the limit in nicehash for the given order
        :return: None
        """
        pass

    def get_limit(self, up_to_timestamp, order_id):
        """
        Gets the limit in nicehash for the given order
        :return: limit
        """
        pass

    def set_price(self, up_to_timestamp, order_id, price):
        """
        Sets the price in nicehash for the given order
        :return: None
        """
        pass

    def get_price(self, up_to_timestamp, order_id):
        """
        Gets the price in nicehash for the given order
        :return: price
        """
        pass
