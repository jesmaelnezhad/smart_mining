from threading import Lock

import math

from configuration import EXECUTION_CONFIGS
from configuration.constants import NICE_HASH_LIMIT_CHANGE_PER_SECOND
from nicehash.driver import NiceHashDriver
from utility.log import logger


class NiceHashOrder:
    class OrderChange:
        def __init__(self, change_timestamp, limit_change=0, price_change=0):
            self.timestamp = change_timestamp
            self.limit_change = limit_change
            self.price_change = price_change

    def __init__(self, current_timestamp, order_id, initial_limit, initial_price):
        self.creation_timestamp = current_timestamp
        self.order_id = order_id
        self.changes = []
        initial_change = NiceHashOrder.OrderChange(current_timestamp, limit_change=initial_limit,
                                                   price_change=initial_price)
        self.changes.append(initial_change)

    def change(self, change_timestamp, limit_change=0, price_change=0):
        new_change = NiceHashOrder.OrderChange(change_timestamp, limit_change=limit_change, price_change=price_change)
        self.changes.append(new_change)

    def calculate_limit_at(self, timestamp):
        limit_change = 0
        for c in self.changes:
            if c.limit_change == 0 or c.timestamp >= timestamp:
                continue
            abs_limit_change = abs(c.limit_change)
            change_in_time_difference = max((timestamp - c.timestamp) * NICE_HASH_LIMIT_CHANGE_PER_SECOND,
                                            abs_limit_change)
            limit_change += math.copysign(change_in_time_difference, c.limit_change)
        return limit_change

    def calculate_price_at(self, timestamp):
        price_change = 0
        for c in self.changes:
            if c.price_change == 0 or c.timestamp >= timestamp:
                continue
            price_change += c.price_change
        return price_change


class NiceHashSimulationDriver(NiceHashDriver):
    """
    Class that implements the driver of the fake nicehash and is used in simulation
    """

    def __init__(self):
        """
        A singleton class that is the driver of nicehash
        """
        # A map from order_id to its information object
        super().__init__()
        self.orders = []
        self.orders_mutex = Lock()

    def perform_tick(self, up_to_timestamp):
        """
        Performs one tick.
        :return: None
        """
        logger('simulation/driver').debug("Performing a tick at timestamp {0}.".format(up_to_timestamp))

    def pre_exit_house_keeping(self):
        """
        This function is called before the thread stops and is useful for closing orders if the robot is going down
        :return: None
        """
        if EXECUTION_CONFIGS.nice_hash_close_orders_before_shutdown:
            # Not needed in simulation because no more records from these records will be written
            pass
        logger('simulation/driver').info("House keeping before shutdown.")

    def create_order(self, creation_timestamp, initial_limit, initial_price):
        """
        Creates a new order with the given initial price and limit and returns the order id
        :param initial_price:
        :param initial_limit:
        :param creation_timestamp:
        :return: order id
        """
        new_order_id = generate_order_id(creation_timestamp)
        new_order = NiceHashOrder(creation_timestamp, new_order_id, initial_limit, initial_price)
        self.orders_mutex.acquire()
        try:
            self.orders.append(new_order)
            return new_order_id
        finally:
            self.orders_mutex.release()

    def close_order(self, order_id):
        """
        Closes the order with given order id
        :param order_id:
        :return: True if any matching order was found and False otherwise
        """
        self.orders_mutex.acquire()
        try:
            found = False
            new_order_list = []
            for o in self.orders:
                if order_id == o.order_id:
                    found = True
                    continue
                new_order_list.append(o)
            self.orders = new_order_list
            return found
        finally:
            self.orders_mutex.release()

    def get_orders(self, order_id=None):
        """
        Returns all orders or the one with the given order id (or None if not exists)
        :param order_id:
        :return: and array of orders or a single order
        """
        self.orders_mutex.acquire()
        try:
            if order_id is None:
                orders = self.orders.copy()
                return orders
            else:
                for o in self.orders:
                    if order_id == o.order_id:
                        return o.copy()
                return None
        finally:
            self.orders_mutex.release()

    def change_order(self, timestamp, order_id, limit_change=0, price_change=0):
        """
        Applies the given change in limit or price in nicehash for the order with the given order id
        :return: True if any matching order found
        """
        self.orders_mutex.acquire()
        try:
            for o in self.orders:
                if order_id == o.order_id:
                    o.change(change_timestamp=timestamp, limit_change=limit_change, price_change=price_change)
                    return True
            return False
        finally:
            self.orders_mutex.release()


def generate_order_id(creation_timestamp):
    return "{0}_{1}".format(EXECUTION_CONFIGS.identifier, creation_timestamp)