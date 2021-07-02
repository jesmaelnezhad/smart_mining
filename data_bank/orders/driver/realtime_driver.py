from configuration.constants import SLUSHPOOL_ID_NICEHASH
from data_bank.orders.driver.driver import NiceHashDriver
from data_bank.orders.order import ActiveOrderInfo, NiceHashActiveOrderMarket, NiceHashActiveOrderType, \
    NiceHashActiveOrderAlgorithm


class RealtimeActiveOrderInfo(ActiveOrderInfo):
    def __init__(self, order_details_json):
        """
        A json such as this: https://www.nicehash.com/docs/rest/post-main-api-v2-hashpower-order
        :param order_details_json: the full json information of the order as Nicehash API returns
        """
        # TODO call super constructor using the data extracted from the given json
        self.order_details_json = order_details_json

    def get_full_json_details(self):
        return self.order_details_json


class NiceHashRealtimeDriver(NiceHashDriver):
    """
    Class that implements the driver of the real nicehash and is used to make changes to actual nicehash orders
    """

    def __init__(self):
        """
        A singleton class that is the driver of nicehash
        """
        super().__init__()

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
        :param exists:
        :param amount:
        :param speed_limit:
        :param creation_timestamp:
        :param order_id: will be used if given (in the simulation mode)
        :param pool_id:
        :param market:
        :param order_type:
        :param algorithm:
        :return: ActiveOrderInfo object
        """
        # TODO create the order in the real nicehash
        pass

    def close_order(self, order_id):
        """
        Closes the order with given order id
        :param order_id:
        :return: True if any matching order was found and False otherwise
        """
        # TODO close order in real nicehash
        pass

    def get_orders(self, order_id=None):
        """
        Returns all orders or the one with the given order id (or None if not exists)
        :param order_id:
        :return: a dictionary of orders or a single order or None
        """
        # TODO get a snapshot of the real orders
        return {}

    def update_order_price_and_limit(self, timestamp, order_id, limit, price, display_market_factor=None,
                                     market_factor=None):
        """
        Applies the given change in limit or price in nicehash for the order with the given order id
        :return: True if any matching order found
        """
        # TODO change the real order in nicehash
        pass

    def refill_order(self, timestamp, order_id, refill_amount):
        """
        Adds `refill_amount` to the order which is determined with the `order_id`.
        :return: None
        """
        # TODO refill the order in nicehash
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
        # TODO get stats from nicehash
        pass
