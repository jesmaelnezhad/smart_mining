import json

from data_bank import get_orders_database_handler


class PersistentObject:
    OWNER_KEY = "owner"
    ID_KEY = "strategy_execution_id"

    def __init__(self, owner, strategy_execution_id):
        self.owner = owner
        self.strategy_execution_id = strategy_execution_id
        self.__setitem__(self.OWNER_KEY, owner)
        self.__setitem__(self.ID_KEY, strategy_execution_id)

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __getitem__(self, key):
        return self.__dict__.get(key)

    def __delitem__(self, key):
        del self.__dict__[key]

    def json(self):
        return json.dumps(self.__dict__)

    def __str__(self):
        return self.json().__str__()

    def save_in_db(self):
        orders_db = get_orders_database_handler()
        orders_db.key_value_put(self[self.OWNER_KEY], self[self.ID_KEY], self.__str__())

    def load_from_db(self):
        orders_db = get_orders_database_handler()
        json_str = orders_db.key_value_get(self.owner, self.strategy_execution_id)
        self.__dict__ = json.loads(json_str)
        self.recast_attr_types_after_load()

    def recast_attr_types_after_load(self):
        pass