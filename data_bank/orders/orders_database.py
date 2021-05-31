from clock.clock import calculate_tick_duration_from_sleep_duration
from configuration import EXECUTION_CONFIGS
from configuration.constants import SLUSHPOOL_ID_NICEHASH
from data_bank.database import DatabaseHandler, DatabaseUpdater, DatabaseException
from data_bank.driver import NiceHashRealtimeDriver, NiceHashSimulationDriver
from data_bank.driver.driver import NiceHashDriver, DriverOperationException
from data_bank.model import NiceHashActiveOrderMarket, NiceHashActiveOrderType, NiceHashActiveOrderAlgorithm
from utility.log import logger


class RuntimeScopeIdentifier:
    DRIVER = None

    def get_runtime_scope_database_prefix(self):
        pass

    def get_runtime_scope_should_drop_at_first(self):
        pass

    def get_nice_hash_driver(self):
        pass


class RealtimeScopeIdentifier(RuntimeScopeIdentifier):
    def get_runtime_scope_database_prefix(self):
        return ""

    def get_runtime_scope_should_drop_at_first(self):
        return False

    def get_nice_hash_driver(self):
        if self.DRIVER is None:
            self.DRIVER = NiceHashRealtimeDriver()
        return self.DRIVER


class SimulationScopeIdentifier(RuntimeScopeIdentifier):
    def get_runtime_scope_database_prefix(self):
        return "simulation_"

    def get_runtime_scope_should_drop_at_first(self):
        return True

    def get_nice_hash_driver(self):
        if self.DRIVER is None:
            self.DRIVER = NiceHashSimulationDriver()
        return self.DRIVER


class OrdersDatabaseUpdater(DatabaseUpdater):
    def __init__(self, handler, scope_identifier):
        super().__init__(handler)
        self.scope_identifier = scope_identifier

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
        self.handler.unset_exist()
        # 1. Get the list of current active orders with their details
        nice_hash_driver = self.scope_identifier.get_nice_hash_driver()
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


class OrdersDatabaseHandler(DatabaseHandler, NiceHashDriver):
    ENSURE_INIT_SQL_STATEMENTS = [
        """CREATE TYPE nicehash_order_market AS ENUM ('EU','USA','EU_N','USA_E');""",
        """CREATE TYPE nicehash_order_algorithm AS ENUM ('SHA250');""",
        """CREATE TYPE nicehash_order_type AS ENUM ('standard', 'fixed');"""
    ]
    ENSURE_DROP_TABLE_SQL_STATEMENT = """DROP TABLE IF EXISTS {0};"""

    def ensure_key_values_table(self):
        self.execute_write(write_sql_query=self.KEY_VALUES_CREATE_SQL_STATEMENT)

    def ensure_drop_key_values_table(self):
        sql_statement = self.ENSURE_DROP_TABLE_SQL_STATEMENT.format(self.KEY_VALUES_TABLE_NAME)
        self.execute_write(write_sql_query=sql_statement)

    def ensure_init_sql_statements(self):
        for stmt in self.ENSURE_INIT_SQL_STATEMENTS:
            try:
                self.execute_write(write_sql_query=stmt)
            except DatabaseException as e:
                logger("orders database/init sql statements").warning("Failed to run the initialization scripts.")

    ORDERS_TABLE_NAME = 'orders'
    ORDERS_TABLE_SQL_STATEMENT = """CREATE TABLE IF NOT EXISTS """ + ORDERS_TABLE_NAME + """ 
    (creation_timestamp timestamptz NOT NULL, 
    order_id character(40) PRIMARY KEY NOT NULL,
    price DOUBLE PRECISION NOT NULL,
    speed_limit DOUBLE PRECISION NOT NULL, 
    amount DOUBLE PRECISION NOT NULL,
    market nicehash_order_market NOT NULL, 
    order_type nicehash_order_type NOT NULL, 
    algorithm nicehash_order_algorithm NOT NULL, 
    pool_id character(100) NOT NULL, 
    exist BIT NOT NULL,
    full_details_json_serialized TEXT);"""

    def ensure_orders_table(self):
        self.execute_write(write_sql_query=self.ORDERS_TABLE_SQL_STATEMENT)

    def ensure_drop_orders_table(self):
        sql_statement = self.ENSURE_DROP_TABLE_SQL_STATEMENT.format(self.ORDERS_TABLE_NAME)
        self.execute_write(write_sql_query=sql_statement)

    ORDER_STATS_TABLE_NAME = 'order_stats'
    ORDER_STATS_TABLE_SQL_STATEMENT = """CREATE TABLE IF NOT EXISTS """ + ORDER_STATS_TABLE_NAME + """
    (update_timestamp timestamptz NOT NULL,
    order_id character(40) NOT NULL, 
    is_order_alive BIT NOT NULL,
    accepted_speed DOUBLE PRECISION,
    rejected_speed_share_above_target DOUBLE PRECISION,
    rejected_speed_stale_shares DOUBLE PRECISION,
    rejected_speed_duplicate_shares DOUBLE PRECISION,
    rejected_speed_invalid_ntime DOUBLE PRECISION,
    rejected_speed_other_reason DOUBLE PRECISION,
    rejected_speed_unknown_worker DOUBLE PRECISION,
    rejected_speed_response_timeout DOUBLE PRECISION,
    speed_limit DOUBLE PRECISION NOT NULL,
    rewarded_speed DOUBLE PRECISION NOT NULL,
    paying_speed DOUBLE PRECISION NOT NULL,
    rejected_speed DOUBLE PRECISION NOT NULL,
    paid_amount DOUBLE PRECISION NOT NULL,
    price DOUBLE PRECISION NOT NULL);"""

    def ensure_order_stats_table(self):
        self.execute_write(write_sql_query=self.ORDER_STATS_TABLE_SQL_STATEMENT)

    def ensure_drop_order_stats_table(self):
        sql_statement = self.ENSURE_DROP_TABLE_SQL_STATEMENT.format(self.ORDER_STATS_TABLE_NAME)
        self.execute_write(write_sql_query=sql_statement)

    def __init__(self, scope_identifier, user, password, database, host="127.0.0.1", port="5432"):
        """
        A singleton class that is the interface of our data bank database
        """
        self.scope_identifier = scope_identifier
        super().__init__(user, password,
                         self.scope_identifier.get_runtime_scope_database_prefix() + database,
                         host, port)
        # ensure types on database if it is first time execution
        self.ensure_key_values_table()
        self.ensure_init_sql_statements()
        # Drop tables if they should be dropped to begin
        if self.scope_identifier.get_runtime_scope_should_drop_at_first():
            self.ensure_drop_orders_table()
            self.ensure_drop_order_stats_table()
            self.ensure_drop_key_values_table()
        # Ensure the existence of tables
        self.ensure_orders_table()
        self.ensure_order_stats_table()
        self.ensure_key_values_table()

    def get_nice_hash_driver(self):
        return self.scope_identifier.get_nice_hash_driver()

    def create_order(self, creation_timestamp, order_id,
                     price, speed_limit, amount,
                     market=NiceHashActiveOrderMarket.EU,
                     order_type=NiceHashActiveOrderType.STANDARD,
                     algorithm=NiceHashActiveOrderAlgorithm.SHA250,
                     pool_id=SLUSHPOOL_ID_NICEHASH,
                     exists=True):
        # insert into the driver and if successful, insert into the database
        driver = self.get_nice_hash_driver()
        try:
            driver.create_order(creation_timestamp=creation_timestamp,
                                order_id=order_id, price=price, speed_limit=speed_limit,
                                amount=amount, pool_id=pool_id,
                                market=market, order_type=order_type,
                                algorithm=algorithm,
                                exist=True)
            # insert into the database
            self.insert_or_update_order(creation_timestamp=creation_timestamp,
                                        order_id=order_id, price=price, speed_limit=speed_limit,
                                        pool_id=pool_id,
                                        market=market, order_type=order_type,
                                        algorithm=algorithm,
                                        exist=True)
            # TODO rollback the second one if the first one failed
        except DriverOperationException as e:
            logger("orders database/create").error("Error in driver: {0}".format(str(e)))

    def close_order(self, order_id):
        # close using the driver and if successful, unset exist bit in the database
        driver = self.get_nice_hash_driver()
        try:
            driver.close_order(order_id)
            # unsetting the exist bit into the database
            self.unset_exist(order_id)
        except DriverOperationException as e:
            logger("orders database/close").error("Error in driver: {0}".format(str(e)))

    def close_all_orders(self):
        """
        Closes all orders
        :return:
        """
        orders = self.get_orders(order_id=None)
        for o in orders:
            self.close_order(order_id=o.get_order_id())

    def get_orders(self, order_id=None):
        # just returns what is found in the database
        return self.get_orders_filtered(order_id=order_id, existing_orders_only=True)

    def update_order_price_and_limit(self, timestamp, order_id, limit, price, display_market_factor=None, market_factor=None):
        """
        Applies the given change in limit or price in nicehash for the order with the given order id and also applies the change to DB
        :return: True if any matching order found
        """
        # Update using the driver and if successful, unset exist bit in the database
        driver = self.get_nice_hash_driver()
        try:
            driver.update_order_price_and_limit(timestamp=timestamp, order_id=order_id, limit=limit,
                                                price=price, display_market_factor=display_market_factor,
                                                market_factor=market_factor)
            # Update the database context.
            self.insert_or_update_order(timestamp, order_id=order_id, price=price, speed_limit=limit)
        except DriverOperationException as e:
            logger("orders database/close").error("Error in driver: {0}".format(str(e)))

    def refill_order(self, timestamp, order_id, refill_amount):
        # Refill using the driver and if successful, refill in the database
        driver = self.get_nice_hash_driver()
        try:
            driver.refill_order(timestamp=timestamp, order_id=order_id, refill_amount=refill_amount)
            # Refill the database context.
            self.update_amount_and_refill_in_db(order_id=order_id, amount=refill_amount)
        except DriverOperationException as e:
            logger("orders database/close").error("Error in driver: {0}".format(str(e)))

    def stats_order(self, timestamp, after_timestamp, order_id):
        """
        Returns the statistics of the order determined with the given order id.
        :return: Dictionary with the following keys:
        update_timestamp in milliseconds since 1.1.1970
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
        # just returns what is found in the database
        return self.stats_order_filtered(order_id=order_id, after_timestamp=after_timestamp)

    def get_orders_filtered(self, order_id=None, existing_orders_only=True):
        """
        Returns all orders.
        :param existing_orders_only: return only those orders whose exist column is 1
        :parameter order_id: if None, all orders are returned, if not None, only that order is fetched.
        :return: A list of lists. Each tuple consists of (creation_timestamp, update_timestamp, order_id, market,
        order_type, algorithm, price, power_limit, amount, pool_id). This list contains one tuple if order_id is passed, and
        none if order_id is passed and no such order exists.
        """
        # retrieve info from database
        sql_query = """SELECT * FROM {0} {1};""".format(self.ORDERS_TABLE_NAME,
            "" if order_id is None else " WHERE order_id = '{0}'".format(order_id))
        if existing_orders_only:
            sql_query += " AND exist = 1;"
        orders = self.execute_select(select_sql_query=sql_query)
        return orders

    def stats_order_filtered(self, order_id, after_timestamp):
        # retrieve info from database
        sql_query = """SELECT * FROM {0} WHERE order_id = '{1}' AND  update_timestamp >= to_timestamp('{2}');""".format(
            self.ORDERS_TABLE_NAME, order_id, after_timestamp)
        orders = self.execute_select(select_sql_query=sql_query)
        return orders

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
            self.ORDER_STATS_TABLE_NAME if delete_active_orders_instead else self.ORDERS_TABLE_NAME,
            order_ids_list_str)
        try:
            self.execute_write(write_sql_query=sql_query)
        except DatabaseException:
            logger('order-database/delete').error("Error: deleting order(s) with id(s) {0}".format(
                "" if order_ids is None or len(order_ids) == 0 else ", ".join(order_ids)
            ))

    def insert_or_update_order(self, creation_timestamp, order_id,
                               price, speed_limit, amount,
                               pool_id=SLUSHPOOL_ID_NICEHASH,
                               market=NiceHashActiveOrderMarket.EU, order_type=NiceHashActiveOrderType.STANDARD,
                               algorithm=NiceHashActiveOrderAlgorithm.SHA250,
                               exist=True):
        """
        If the given order id exists, updates the record, and if not, inserts it.
        :param speed_limit:
        :param amount:
        :param price:
        :param creation_timestamp:
        :param order_id:
        :param pool_id:
        :param market:
        :param order_type:
        :param algorithm:
        :param exist:
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
            (creation_timestamp, order_id, price, speed_limit, amount, pool_id, market, order_type, algorithm) 
            VALUES (to_timestamp({0}), '{1}', {2}, '{3}', '{4}', '{5}', '{6}', '{7}', '{8}', '{9}');""".format(
                creation_timestamp, order_id,
                price, speed_limit, amount,
                pool_id,
                market, order_type, algorithm, 1 if exist else 0,
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
            price={2}, speed_limit={3}, amount={4}, 
            pool_id='{5}',
            market='{6}', 
            order_type='{7}', 
            algorithm='{8}'
            exist='{9}'
            WHERE order_id = '{0}';""".format(
                order_id,
                creation_timestamp, price, speed_limit, amount, pool_id, market, type, algorithm, '1' if exist else '0',
                self.ORDERS_TABLE_NAME
            )
            try:
                self.execute_write(write_sql_query=sql_query)
            except DatabaseException:
                logger('mine-database/orders').error(
                    "Error: updating order with id {0}".format(order_id))

    def update_price_and_limit_in_db(self, order_id, price, speed_limit):
        """

        :param order_id:
        :param price:
        :param speed_limit:
        :return: None if no such order ID is found
        """
        order = None
        order_ = self.get_orders(order_id=order_id)
        if order_ is not None and len(order_) > 0:
            order = order_[0]
        if order is None:
            return None
        else:
            sql_write_statement = """UPDATE {3} 
            SET price = {1} and speed_limit = {2} 
            WHERE order_id = '{0}';""".format(order_id, price, speed_limit, self.ORDERS_TABLE_NAME)
            self.execute_write(write_sql_query=sql_write_statement)
            return None

    def update_amount_and_refill_in_db(self, order_id, amount):
        """

        :param amount:
        :param order_id:
        :return: None if no such order ID is found
        """
        order = None
        order_ = self.get_orders(order_id=order_id)
        if order_ is not None and len(order_) > 0:
            order = order_[0]
        if order is None:
            return None
        else:
            sql_write_statement = """UPDATE {2} 
            SET amount = {1} 
            WHERE order_id = '{0}';""".format(order_id, amount, self.ORDERS_TABLE_NAME)
            self.execute_write(write_sql_query=sql_write_statement)
            return None
