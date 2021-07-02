import enum
import json
from configuration.constants import SLUSHPOOL_ID


class NiceHashActiveOrderMarket(enum.Enum):
    EU = 'EU'
    USA = 'USA'
    EU_N = 'EU_N'
    USA_E = 'USA_E'


class NiceHashActiveOrderType(enum.Enum):
    STANDARD = 'standard'
    FIXED = 'fixed'


class NiceHashActiveOrderAlgorithm(enum.Enum):
    SHA250 = 'SHA250'


class ActiveOrderInfo:
    def __init__(self, creation_timestamp, order_id, limit, price, budget_left, pool_id=SLUSHPOOL_ID,
                 market=NiceHashActiveOrderMarket.EU, algorithm=NiceHashActiveOrderAlgorithm.SHA250,
                 order_type=NiceHashActiveOrderType.STANDARD):
        self.creation_timestamp = creation_timestamp
        self.update_timestamp = creation_timestamp
        self.order_id = order_id
        self.limit = limit
        self.price = price
        self.budget_left = budget_left
        self.pool_id = pool_id
        self.market = market
        self.algorithm = algorithm
        self.order_type = order_type

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

    def get_market(self):
        return self.market

    def get_algorithm(self):
        return self.algorithm

    def get_order_type(self):
        return self.order_type

    def get_update_timestamp(self):
        return self.update_timestamp

    def get_full_json_details(self):
        return json.dump(self.__dict__)