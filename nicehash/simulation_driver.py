from nicehash.driver import NiceHashDriver
from utility.log import logger


class NiceHashSimulationDriver(NiceHashDriver):
    """
    Class that implements the driver of the fake nicehash and is used in simulation
    """
    def __init__(self):
        """
        A singleton class that is the driver of nicehash
        """
        # A map from order_id to its information object
        self.orders = dict()

    def perform_tick(self, up_to_timestamp):
        """
        Performs one tick.
        :return: None
        """
        logger('nicehash').info("Performing a tick at timestamp {0}.".format(up_to_timestamp))
        # TODO: move on all orders and update their limits according to any previously requested limit changes
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