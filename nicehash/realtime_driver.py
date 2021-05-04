from configuration import EXECUTION_CONFIGS
from nicehash.simulation_driver import NiceHashSimulationDriver
from utility.log import logger


class NiceHashRealtimeDriver(NiceHashSimulationDriver):
    """
    Class that implements the driver of the real nicehash and is used in real execution
    """

    def __init__(self):
        """
        A singleton class that is the driver of nicehash
        """
        super().__init__()

    def perform_tick(self, up_to_timestamp):
        """
        Performs one tick.
        :return: None
        """
        logger('realtime/driver').debug("Performing a tick at timestamp {0}.".format(up_to_timestamp))

    def pre_exit_house_keeping(self):
        """
        This function is called before the thread stops and is useful for closing orders if the robot is going down
        :return: None
        """
        if EXECUTION_CONFIGS.nice_hash_close_orders_before_shutdown:
            # Not needed in simulation because no more records from these records will be written
            pass
        logger('realtime/driver').info("House keeping before shutdown.")

    def create_order(self, creation_timestamp, initial_limit, initial_price, order_id=None):
        """
        Creates a new order with the given initial price and limit and returns the order id
        :param initial_price:
        :param initial_limit:
        :param creation_timestamp:
        :param order_id: will be used if given (in the simulation mode)
        :return: ActiveOrderInfo object
        """
        new_simulation_order = super().create_order(creation_timestamp, initial_limit, initial_price, order_id=order_id)
        # TODO also create the order in the real nicehash
        pass

    def close_order(self, order_id):
        """
        Closes the order with given order id
        :param order_id:
        :return: True if any matching order was found and False otherwise
        """
        result_of_closing_the_simulation_order = super().close_order(order_id)
        # also close order in real nicehash
        pass

    def get_orders(self, order_id=None):
        """
        Returns all orders or the one with the given order id (or None if not exists)
        :param order_id:
        :return: a dictionary of orders or a single order or None
        """
        simulation_orders_snapshot = super().get_orders(order_id=order_id)
        # TODO also get a snapshot of the real orders
        pass

    def change_order(self, timestamp, order_id, limit_change=0, price_change=0):
        """
        Applies the given change in limit or price in nicehash for the order with the given order id
        :return: True if any matching order found
        """
        result_of_changing_the_simulation_order = super().change_order(timestamp, order_id, limit_change, price_change)
        # also change the real order in nicehash
        pass
