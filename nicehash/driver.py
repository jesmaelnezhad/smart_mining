import math
from time import sleep

from clock import get_clock
from clock.clock import calculate_tick_duration_from_sleep_duration
from clock.tick_performer import TickPerformer
from configuration import EXECUTION_CONFIGS
from configuration.constants import SLUSHPOOL_ID
from utility.log import logger


class ActiveOrderInfo:
    def __init__(self, creation_timestamp, order_id, limit, price, budget_left, pool_id=SLUSHPOOL_ID):
        self.creation_timestamp = creation_timestamp
        self.order_id = order_id
        self.limit = limit
        self.price = price
        self.budget_left = budget_left
        self.pool_id = pool_id

    def get_creation_timestamp(self):
        return self.creation_timestamp

    def get_order_id(self):
        return self.order_id

    def get_limit(self):
        return self.limit

    def get_price(self):
        return self.price

    def get_budget_left(self):
        return self.budget_left


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
        self.pre_exit_house_keeping()

    def post_run(self):
        logger('driver').info("Driver is terminating.")

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

    def pre_exit_house_keeping(self):
        """
        This function is called before the thread stops and is useful for closing orders if the robot is going down
        :return: None
        """
        logger('nicehash').warn("Base class of the driver in use! House keeping before shutdown.")
        pass

    def create_order(self, creation_timestamp, initial_limit, initial_price, order_id=None):
        """
        Creates a new order with the given initial price and limit and returns the order id
        :param initial_price:
        :param initial_limit:
        :param creation_timestamp:
        :param order_id: will be used if given (in the simulation mode), order_id=None
        :return: ActiveOrderInfo object
        """
        pass

    def close_order(self, order_id):
        """
        Closes the order with given order id
        :param order_id:
        :return: True if any matching order was found and False otherwise
        """
        pass

    def close_all_orders(self):
        """
        Closes all orders
        :return:
        """
        orders = self.get_orders(order_id=None)
        for o in orders:
            self.close_order(order_id=o.get_order_id())

    def get_orders(self, order_id=None):
        """
        Returns all orders or the one with the given order id (or None if not exists)
        :param order_id:
        :return: and array of orders or a single order
        """
        pass

    def change_order(self, timestamp, order_id, limit_change=0, price_change=0):
        """
        Applies the given change in limit or price in nicehash for the order with the given order id
        :return: True if any matching order found
        """
        pass
