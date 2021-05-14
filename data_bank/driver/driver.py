from clock.clock import calculate_tick_duration_from_sleep_duration
from configuration import EXECUTION_CONFIGS
from configuration.constants import SLUSHPOOL_ID_NICEHASH
from data_bank.model import NiceHashActiveOrderAlgorithm, NiceHashActiveOrderMarket, NiceHashActiveOrderType


class DriverOperationException(Exception):
    pass


class NiceHashDriver:
    def __init__(self):
        """
        A singleton class that is the driver of nicehash
        """
        super().__init__()
        self.tick_duration = calculate_tick_duration_from_sleep_duration(EXECUTION_CONFIGS.nice_hash_sleep_duration)

    def create_order(self, creation_timestamp, order_id,
                     price, speed_limit, amount,
                     market=NiceHashActiveOrderMarket.EU,
                     order_type=NiceHashActiveOrderType.STANDARD,
                     algorithm=NiceHashActiveOrderAlgorithm.SHA250,
                     pool_id=SLUSHPOOL_ID_NICEHASH,
                     exists=True):
        """
        Creates a new order with the given initial price and limit and returns the order id
        :param price:
        :param amount:
        :param speed_limit:
        :param exists:
        :param creation_timestamp:
        :param pool_id:
        :param market:
        :param order_type:
        :param algorithm:
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

    def update_order_price_and_limit(self, timestamp, order_id, limit, price, display_market_factor=None, market_factor=None):
        """
        # FIXME: set defailts for market factors
        Applies the given change in limit or price in nicehash for the order with the given order id
        :return: True if any matching order found
        """
        pass

    def refill_order(self, timestamp, order_id, refill_amount):
        """
        Adds `refill_amount` to the order which is determined with the `order_id`.
        :return: None
        """
        pass

    def stats_order(self, timestamp, after_timestamp, order_id):
        """
        Returns the statistics of the order determined with the given order id.
        :return: Dictionary with the following keys:
        Timestamp in milliseconds since 1.1.1970
        is_order_alive
        accepted_speed
        rejected_speed_share_above_target
        rejected_speed_stale_shares
        rejected_speed_duplicate_shares
        rejected_speed_invalid_ntime
        rejected_speed_other_reason
        rejected_speed_unknown_worker
        rejected_speed_response_timeout
        speed_limit
        rewarded_speed
        paying_speed
        rejected_speed
        paid_amount
        price
        """
        pass
