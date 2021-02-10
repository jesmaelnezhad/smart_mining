from clock.clock import calculate_tick_duration_from_sleep_duration
from configuration import EXECUTION_CONFIGS, is_new_simulation_going_to_happen
from data_bank.database import DatabaseHandler, DatabaseUpdater
from utility.log import logger


class SimulationDatabaseUpdater(DatabaseUpdater):
    def __init__(self, handler):
        super().__init__(handler)

    def get_db_csv_name_suffix(self):
        return "simulation"

    def get_tick_duration(self):
        return calculate_tick_duration_from_sleep_duration(EXECUTION_CONFIGS.simulation_db_updater_sleep_duration)

    def update_data(self, up_to_timestamp):
        """
        Updates the data up to the given timestamp. Uses current timestamp if None is passed.
        :return: None
        """
        super().update_data(up_to_timestamp)
        # TODO logic needed to update the simulation database
        logger('simulation/db/updater').debug("Updating data up to timestamp {0}.".format(up_to_timestamp))


class SimulationDatabaseHandler(DatabaseHandler):
    SIMULATION_DATA_TABLE_NAME_PREFIX = 'simulation_'

    def __init__(self, user, password, database="smart_miner_simulation_data", host="127.0.0.1", port="5432"):
        """
        A singleton class that is the interface of our simulation data database
        """
        super().__init__(user, password, database, host, port)
        self.current_simulation_table_name = None

    def prepare_for_simulation(self, proven_simulation_identifiers=None):
        """
        Prepares the database state to begin a simulation
        :return: None
        """
        # Unless None is passed for the list of proven simulations,
        # clean the simulations whose proof is NOT found by the simulation evaluator
        if proven_simulation_identifiers is not None:
            self.clean_unproven_simulation_data(proven_simulation_identifiers=proven_simulation_identifiers)
        # Unless current simulation identifier is None,
        # create the simulation data table for the current simulation
        if is_new_simulation_going_to_happen():
            self.set_current_simulation_table_name()
            self.create_simulation_table_for_the_current_simulation()

    def insert_order_info_sample(self, order_id, timestamp, limit, price):
        sql_statement = """INSERT INTO {0} (order_id, moment, power_limit, price)
        VALUES ('{1}', to_timestamp({2}), {3}, {4});""".format(self.current_simulation_table_name, order_id, timestamp,
                                                               limit, price)
        self.execute_write(write_sql_query=sql_statement)
        logger('simulation/db/handler').debug("Inserted new data sample for order id {0}.".format(order_id))

    def clean_unproven_simulation_data(self, proven_simulation_identifiers):
        tables_to_drop = []
        existing_tables = self.get_list_of_simulation_table_names()
        for table_name in existing_tables:
            table_simulation_identifier = self.generate_simulation_identifier_from_table_name(table_name=table_name)
            if table_simulation_identifier not in proven_simulation_identifiers:
                tables_to_drop.append(table_name)
        for table_name in tables_to_drop:
            logger('simulation/db/handler').info(
                "Dropping table {0} because its simulation proof was not found.".format(table_name))
            self.execute_write(write_sql_query="""DROP TABLE {0};""".format(table_name))

    def set_current_simulation_table_name(self):
        self.current_simulation_table_name = self.generate_table_name_from_simulation_identifier(
            simulation_identifier=EXECUTION_CONFIGS.identifier)

    def create_simulation_table_for_the_current_simulation(self):
        sql_statement = """CREATE TABLE {0}(
        order_id character(200) NOT NULL, 
        moment timestamptz NOT NULL, 
        power_limit DOUBLE PRECISION DEFAULT 0.0, 
        price DOUBLE PRECISION DEFAULT 0.0, 
        CONSTRAINT order_status UNIQUE(order_id, moment));""".format(self.current_simulation_table_name)
        self.execute_write(write_sql_query=sql_statement)
        logger('simulation/db/handler').info(
            "Created table {0} for the simulation that is starting.".format(self.current_simulation_table_name))

    def get_list_of_simulation_table_names(self):
        """
        Returns the list of all existing tables that keep simulation data
        :return: A list of table names
        """
        sql_query = """SELECT table_name FROM information_schema.tables 
        WHERE 
        table_schema = 'public' 
        AND table_catalog = '{0}' 
        AND table_name LIKE '{1}%';""".format(self.database, self.SIMULATION_DATA_TABLE_NAME_PREFIX)
        existing_tables = self.execute_select(select_sql_query=sql_query)
        return [t[0] for t in existing_tables]

    def generate_table_name_from_simulation_identifier(self, simulation_identifier):
        return "{0}{1}".format(self.SIMULATION_DATA_TABLE_NAME_PREFIX, simulation_identifier)

    def generate_simulation_identifier_from_table_name(self, table_name):
        return table_name[len(self.SIMULATION_DATA_TABLE_NAME_PREFIX):]
