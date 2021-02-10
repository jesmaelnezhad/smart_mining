from clock.clock import calculate_tick_duration_from_sleep_duration
from configuration import EXECUTION_CONFIGS
from configuration.constants import SLUSHPOOL_NAME, DEFAULT_NUMBER_OF_PAST_BLOCKS_TO_FETCH
from data_bank.database import DatabaseHandler, DatabaseUpdater
from utility.log import logger


class MineDatabaseUpdater(DatabaseUpdater):
    def __init__(self, handler):
        super().__init__(handler)

    def get_db_csv_name_suffix(self):
        return "mine"

    def get_tick_duration(self):
        return calculate_tick_duration_from_sleep_duration(EXECUTION_CONFIGS.mine_db_updater_sleep_duration)

    def update_data(self, up_to_timestamp):
        """
        Updates the data up to the given timestamp. Uses current timestamp if None is passed.
        :return: None
        """
        super().update_data(up_to_timestamp)
        # TODO logic needed to update the simulation database
        logger('mine-database').debug("Updating data up to timestamp {0}.".format(up_to_timestamp))


class MineDatabaseHandler(DatabaseHandler):
    def __init__(self, user, password, database="smart_miner", host="127.0.0.1", port="5432"):
        """
        A singleton class that is the interface of our data bank database
        """
        super().__init__(user, password, database, host, port)

    def get_latest_block_id(self):
        """
        Returns the id of the latest block in the database
        :return: id
        """
        pass

    def get_blocks_between(self, begin_timestamp, end_timestamp, pool_name=SLUSHPOOL_NAME):
        """
        Returns a list of blocks in the given pool in the database whose moment is between the given timestamps
        :param pool_name:
        :param begin_timestamp:
        :param end_timestamp:
        :return: A list of tuples of the form (id, moment) where id is the block id and moment is its timestamp
        """
        pass

    def get_blocks_prior_or_equal_to(self, prior_to_timestamp, count=DEFAULT_NUMBER_OF_PAST_BLOCKS_TO_FETCH,
                                     pool_name=SLUSHPOOL_NAME):
        """
        Returns a list of up to 'count' blocks in the given pool in the database whose moment is prior or equal to
        'prior_to_timestamp'
        :param count:
        :param prior_to_timestamp:
        :param pool_name:
        :return: A list of tuples of the form (id, moment) where id is the block id and moment is its timestamp
        """
        pass

