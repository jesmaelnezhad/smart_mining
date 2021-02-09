from data_bank.database import Database
from utility.log import logger


class SimulationDatabase(Database):
    def __init__(self, user, password, database, host="127.0.0.1", port="5432"):
        """
        A singleton class that is the interface of our simulation data database
        """
        super().__init__(user, password, database, host, port)
        # TODO things specific to simulation database

    def get_db_csv_name_suffix(self):
        return "simulation"

    def update_data(self, up_to_timestamp):
        """
        Updates the data up to the given timestamp. Uses current timestamp if None is passed.
        :return: None
        """
        super().update_data(up_to_timestamp)
        # TODO logic needed to update the simulation database
        logger('simulation-database').info("Updating data up to timestamp {0}.".format(up_to_timestamp))

