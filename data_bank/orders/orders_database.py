from clock.clock import calculate_tick_duration_from_sleep_duration
from configuration import EXECUTION_CONFIGS
from configuration.constants import SLUSHPOOL_ID, SLUSHPOOL_ID_NICEHASH
from data_bank.database import DatabaseHandler, DatabaseUpdater, DatabaseException
from data_bank.model import NiceHashActiveOrderMarket, NiceHashActiveOrderType, NiceHashActiveOrderAlgorithm
from nicehash import get_nice_hash_driver
from utility.datetime_helpers import timestamp_to_datetime_string
from utility.log import logger


class OrdersDatabaseUpdater(DatabaseUpdater):
    def __init__(self, handler):
        super().__init__(handler)

    def get_db_csv_name_suffix(self):
        return "orders"

    def get_tick_duration(self):
        return calculate_tick_duration_from_sleep_duration(EXECUTION_CONFIGS.order_db_updater_sleep_duration)

    def update_data(self, up_to_timestamp):
        """
        Updates the data up to the given timestamp. Uses current timestamp if None is passed.
        :return: None
        """
        super().update_data(up_to_timestamp)

        # Updating the block table
        self.update_orders(up_to_timestamp)

        logger('order-database').debug("Updating data up to timestamp {0}.".format(up_to_timestamp))

    def update_orders(self, up_to_timestamp):
        """
        Update orders and active_orders tables in the database
        :param up_to_timestamp: the update timestamp or creation timestamp of the orders
        :return: None
        """
        # Update the orders table
        # 0. Unset the exist bit on all order records
        self.handler.unset_exist_on_all_orders()
        # 1. Get the list of current active orders with their details
        nice_hash_driver = get_nice_hash_driver()
        existing_orders = nice_hash_driver.get_orders(order_id=None)
        for o in existing_orders:
            self.handler.insert_or_update_order(creation_timestamp=o.get_creation_timestamp(),
                                                order_id=o.get_order_id(),
                                                pool_id=o.get_pool_id(),
                                                market=o.get_market(),
                                                type=o.get_order_type(),
                                                algorithm=o.get_algorithm(),
                                                exist=True)
            self.handler.insert_active_order_update(update_timestamp=o.get_update_timestamp(),
                                                    order_id=o.get_order_id(),
                                                    price=o.get_price(),
                                                    power_limit=o.get_power_limit(),
                                                    amount=o.get_amount(),
                                                    full_details_json_serialized=o.get_full_json_details)


class OrdersDatabaseHandler(DatabaseHandler):
    ORDERS_TABLE_NAME = 'orders'
    ACTIVE_ORDERS_TABLE_NAME = 'active_orders'
    KEY_VALUES_TABLE_NAME = 'key_values'
    POOLS_TABLE_NAME = 'pools'
    SLUSHPOOL_TABLE_NAME = 'slushpool'

    def __init__(self, user, password, database="smart_miner", host="127.0.0.1", port="5432"):
        """
        A singleton class that is the interface of our data bank database
        """
        super().__init__(user, password, database, host, port)

    def get_orders(self, order_id=None, active_orders_instead=False, existing_orders_only=True):
        """
        Returns all orders.
        :param existing_orders_only: return only those orders whose exist column is 1
        :parameter order_id: if None, all orders are returned, if not None, only that order is fetched.
        :parameter active_orders_instead returns active orders if True. Default to False
        :return: A list of lists. Each tuple consists of (creation_timestamp, update_timestamp, order_id, market,
        type, algorithm, price, power_limit, amount, pool_id). This list contains one tuple if order_id is passed, and
        none if order_id is passed and no such order exists.
        """
        # retrieve info from database
        sql_query = """SELECT * FROM {0} {1};""".format(
            self.ACTIVE_ORDERS_TABLE_NAME if active_orders_instead else self.ORDERS_TABLE_NAME,
            "" if order_id is None else " WHERE order_id = '{0}'".format(order_id))
        if existing_orders_only:
            sql_query += " AND exist = 1;"
        orders = self.execute_select(select_sql_query=sql_query)
        return orders

    def get_orders_price_and_limit_and_amount(self, order_id=None, active_orders_instead=False,
                                              existing_orders_only=True):
        """
        Returns the price, limit, and amount orders.
        :param existing_orders_only: return only those orders whose exist column is 1
        :parameter order_id: if None, all orders are returned, if not None, only that order is fetched.
        :parameter active_orders_instead returns active orders if True. Default to False
        :return: A list of lists. Each tuple consists of (price, power_limit, amount). This list contains one tuple if order_id is passed, and
        none if order_id is passed and no such order exists.
        """
        orders = self.get_orders(order_id=order_id, active_orders_instead=active_orders_instead,
                                 existing_orders_only=existing_orders_only)
        if orders is None or len(orders) == 0:
            return orders
        return [(r[6], r[7], r[8],) for r in orders]

    def delete_all_orders_except(self, order_ids=None, delete_active_orders_instead=False):
        """
        Removes any active order whose id is not found in the given list.
        :parameter order_ids: order ids of the records to keep. No records will survive if None or empty list is passed.
        :parameter delete_active_orders_instead: works on the active_orders table instead.
        :return: None
        """
        order_ids_list_str = ""
        if order_ids is not None and len(order_ids) != 0:
            order_ids_list_str = "WHERE order_id NOT IN ({0})".format(
                ", ".join(["'" + order_id + "'" for order_id in order_ids]))
        # retrieve info from database
        sql_query = """DELETE FROM {0} {1} ;""".format(
            self.ACTIVE_ORDERS_TABLE_NAME if delete_active_orders_instead else self.ORDERS_TABLE_NAME,
            order_ids_list_str)
        try:
            self.execute_write(write_sql_query=sql_query)
        except DatabaseException:
            logger('order-database/delete').error("Error: deleting order(s) with id(s) {0}".format(
                "" if order_ids is None or len(order_ids) == 0 else ", ".join(order_ids)
            ))

    def insert_or_update_order(self, creation_timestamp, order_id, pool_id=SLUSHPOOL_ID_NICEHASH,
                               market=NiceHashActiveOrderMarket.EU, type=NiceHashActiveOrderType.STANDARD,
                               algorithm=NiceHashActiveOrderAlgorithm.SHA250,
                               exist=True):
        """
        If the given order id exists, updates the record, and if not, inserts it.
        :param creation_timestamp:
        :param pool_id:
        :param market:
        :param type:
        :param algorithm:
        :param whether the order is found recently in nicehash:
        :return: Boolean: True if record was inserted and False if it was updated
        """
        order = None
        order_ = self.get_orders(order_id=order_id)
        if order_ is not None and len(order_) > 0:
            order = order_[0]
        if order is None:
            # insert
            sql_query = """INSERT INTO {7} 
            (creation_timestamp, order_id, pool_id, market, type, algorithm) 
            VALUES (to_timestamp({0}), '{1}', {2}, '{3}', '{4}', '{5}', '{6}');""".format(
                creation_timestamp, order_id,
                pool_id,
                market, type, algorithm, 1 if exist else 0,
                self.ORDERS_TABLE_NAME
            )
            try:
                self.execute_write(write_sql_query=sql_query)
            except DatabaseException:
                logger('mine-database/orders').error(
                    "Error: inserting order with id {0}".format(order_id))
        else:
            # update
            sql_query = """UPDATE {7} 
            SET creation_timestamp=to_timestamp({1}), 
            pool_id='{2}',
            market='{3}', 
            type='{4}', 
            algorithm='{5}'
            exist='{6}'
            WHERE order_id = '{0}';""".format(
                order_id,
                creation_timestamp, pool_id, market, type, algorithm, '1' if exist else '0',
                self.ORDERS_TABLE_NAME
            )
            try:
                self.execute_write(write_sql_query=sql_query)
            except DatabaseException:
                logger('mine-database/orders').error(
                    "Error: updating order with id {0}".format(order_id))

    def unset_exist_on_all_orders(self):
        """
        Sets exist to 0 on all order records
        :return: None
        """
        sql_query = """UPDATE {0} SET exist = '0';""".format(self.ORDERS_TABLE_NAME)
        try:
            self.execute_write(write_sql_query=sql_query)
        except DatabaseException:
            logger('orders-database/unset all').error("Error: unsetting orders.")

    def insert_active_order_update(self, update_timestamp, order_id, price, power_limit, amount,
                                   full_details_json_serialized=""):
        """
        If the given order id exists, inserts the new update to the active_orders table.
        :return: None
        """
        order = None
        order_ = self.get_orders(order_id=order_id)
        if order_ is not None and len(order_) > 0:
            order = order_[0]
        if order is None:
            # fail because the order for this active order update does not exist
            return
        # insert
        sql_query = """INSERT INTO {6} 
        (update_timestamp, order_id, price, power_limit, amount, full_details_json_serialized) 
        VALUES (to_timestamp({0}), '{1}', {2}, '{3}', '{4}', '{5}');""".format(
            update_timestamp, order_id,
            price, power_limit, amount,
            full_details_json_serialized,
            self.ACTIVE_ORDERS_TABLE_NAME
        )
        try:
            self.execute_write(write_sql_query=sql_query)
        except DatabaseException:
            logger('mine-database/orders').error(
                "Error: inserting active order with id {0}".format(order_id))

    def get_latest_active_order_update(self, up_to_timestamp):
        """
        Returns the info of the latest active order update prior to up_to_timestamp.
        :param up_to_timestamp:
        :return: tuple (update_timestamp, order_id, price, power_limit, amount, full_details_json_serialized) or None if
         no updates found with the given criterion
        """
        sql_query = """SELECT (update_timestamp, order_id, price, power_limit, amount, full_details_json_serialized) 
        FROM {1} ORDER BY update_timestamp DESC WHERE update_timestamp < to_timestamp({0}) LIMIT 1;""".format(
            up_to_timestamp,
            self.ACTIVE_ORDERS_TABLE_NAME
        )
        try:
            self.execute_write(write_sql_query=sql_query)
            order_results = self.execute_select(select_sql_query=sql_query)
            return None if len(order_results) == 0 else order_results[0]
        except DatabaseException:
            logger('mine-database/orders').error(
                "Error: fetching active order update prior to {0}".format(
                    timestamp_to_datetime_string(up_to_timestamp)))
