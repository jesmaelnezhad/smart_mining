import math

from clock import get_clock
from configuration import EXECUTION_CONFIGS
from configuration.constants import NICE_HASH_LIMIT_CHANGE_PER_SECOND, SLUSHPOOL_ID_NICEHASH
from data_bank.orders.driver.driver import NiceHashDriver
from data_bank.orders.order import ActiveOrderInfo, NiceHashActiveOrderMarket, NiceHashActiveOrderType, \
    NiceHashActiveOrderAlgorithm
from utility.containers import ThreadSafeDictionary


class SimulationActiveOrderInfo(ActiveOrderInfo):
    class OrderChange:
        def __init__(self, change_timestamp, limit_change=0, price_change=0):
            self.timestamp = change_timestamp
            self.limit_change = limit_change
            self.price_change = price_change

    def __init__(self, current_timestamp, order_id, initial_limit, initial_price):
        super().__init__(creation_timestamp=current_timestamp, order_id=order_id, limit=initial_limit,
                         price=initial_price, budget_left=0)
        self.changes = []
        initial_change = SimulationActiveOrderInfo.OrderChange(current_timestamp, limit_change=initial_limit,
                                                               price_change=initial_price)
        self.changes.append(initial_change)

    def change(self, change_timestamp, limit_change=0, price_change=0):
        new_change = SimulationActiveOrderInfo.OrderChange(change_timestamp, limit_change=limit_change,
                                                           price_change=price_change)
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

    def calculate_budget_left_at(self, timestamp):
        """
        calculate the budget left in order based on the price up to the given timestamp
        :param timestamp:
        :return: the budget left in the order
        """
        # TODO
        return super().get_budget_left()

    def get_limit(self):
        current_timestamp = get_clock().read_timestamp_of_now()
        return self.calculate_limit_at(current_timestamp)

    def get_price(self):
        current_timestamp = get_clock().read_timestamp_of_now()
        return self.calculate_price_at(current_timestamp)

    def get_budget_left(self):
        current_timestamp = get_clock().read_timestamp_of_now()
        return self.calculate_budget_left_at(current_timestamp)


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
        self.order_container = ThreadSafeDictionary()

    def create_order(self, creation_timestamp, order_id,
                     price, speed_limit, amount,
                     market=NiceHashActiveOrderMarket.EU,
                     order_type=NiceHashActiveOrderType.STANDARD,
                     algorithm=NiceHashActiveOrderAlgorithm.SHA250,
                     pool_id=SLUSHPOOL_ID_NICEHASH,
                     exists=True):
        """
        Creates a new order with the given initial price and limit and returns the order id
        :param exists:
        :param amount:
        :param price:
        :param speed_limit:
        :param creation_timestamp:
        :param pool_id:
        :param market:
        :param order_type:
        :param algorithm:
        :param order_id: will be used if given (in the simulation mode)
        :return: ActiveOrderInfo object
        """
        new_order_id = generate_order_id(creation_timestamp) if order_id is None else order_id
        new_order = SimulationActiveOrderInfo(creation_timestamp, new_order_id, speed_limit, price)
        self.order_container.set(new_order_id, new_order)
        return new_order

    def close_order(self, order_id):
        """
        Closes the order with given order id
        :param order_id:
        :return: True if any matching order was found and False otherwise
        """
        return self.order_container.unset(order_id)

    def get_orders(self, order_id=None):
        """
        Returns all orders or the one with the given order id (or None if not exists)
        :param order_id:
        :return: a dictionary of orders or a single order or None
        """
        if order_id is None:
            return self.order_container.snapshot()
        found, obj = self.order_container.get(order_id)
        if found:
            return obj
        return None

    def update_order_price_and_limit(self, timestamp, order_id, limit, price, display_market_factor=None, market_factor=None):
        """
        Applies the given change in limit or price in nicehash for the order with the given order id
        :return: True if any matching order found
        """
        return self.order_container.call_method_from_object(SimulationActiveOrderInfo.change,
                                                            {
                                                                'change_timestamp': timestamp,
                                                                'limit_change': limit,
                                                                'price_change': price,
                                                            },
                                                            order_id)

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


def generate_order_id(creation_timestamp):
    return "{0}_{1}".format(EXECUTION_CONFIGS.identifier, creation_timestamp)
