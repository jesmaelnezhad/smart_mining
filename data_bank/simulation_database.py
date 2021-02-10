from clock.clock import calculate_tick_duration_from_sleep_duration
from configuration import EXECUTION_CONFIGS
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
        logger('simulation-db/updater').debug("Updating data up to timestamp {0}.".format(up_to_timestamp))


class SimulationDatabaseHandler(DatabaseHandler):
    def __init__(self, user, password, database="smart_miner_simulation_data", host="127.0.0.1", port="5432"):
        """
        A singleton class that is the interface of our simulation data database
        """
        super().__init__(user, password, database, host, port)

