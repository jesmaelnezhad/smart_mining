from clock.clock import calculate_tick_duration_from_sleep_duration
from configuration import EXECUTION_CONFIGS
from configuration.constants import SLUSHPOOL_ID
from data_bank.database import DatabaseHandler, DatabaseUpdater
from utility.datetime_helpers import datetime_string_to_timestamp
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
        # TODO logic needed to update the mine database
        logger('mine-database').debug("Updating data up to timestamp {0}.".format(up_to_timestamp))


class MineDatabaseHandler(DatabaseHandler):
    BLOCKS_TABLE_NAME = 'blocks'
    KEY_VALUES_TABLE_NAME = 'key_values'
    NETWORK_DATA_TABLE_NAME = 'network_data'
    POOLS_TABLE_NAME = 'pools'
    SLUSHPOOL_TABLE_NAME = 'slushpool'

    def __init__(self, user, password, database="smart_miner", host="127.0.0.1", port="5432"):
        """
        A singleton class that is the interface of our data bank database
        """
        super().__init__(user, password, database, host, port)

    def get_latest_block_info(self, pool_id=SLUSHPOOL_ID,
                              prior_to_moment=None,
                              return_first_block_info=False):
        """
        Returns the id of the latest block in the database for the given pool_id and prior to the given timestamp
        :param pool_id: identifies the pool
        :param prior_to_moment: latest block earlier than this moment if return_first_block_info is False,
                                or earliest block later than this moment if return_first_block_info is True
                                If None is passed, now is used for latest, and 0 is used for earliest boundary
        :param return_first_block_info:
        :return: (id, moment) or None if no block records exist in the database
        """
        if prior_to_moment is None:
            if return_first_block_info:
                prior_to_moment = 0
            else:
                prior_to_moment = datetime_string_to_timestamp(datetime_string=None)
        sql_query = None
        if return_first_block_info:
            sql_query = """SELECT id, moment FROM {0} 
            WHERE pool_id = {1} AND moment >= to_timestamp({2}) 
            ORDER BY moment ASC
            LIMIT 1;""".format(self.BLOCKS_TABLE_NAME, pool_id, prior_to_moment)
        else:
            sql_query = """SELECT id, moment FROM {0} 
            WHERE pool_id = {1} AND moment <= to_timestamp({2}) 
            ORDER BY moment DESC
            LIMIT 1;""".format(self.BLOCKS_TABLE_NAME, pool_id, prior_to_moment)
        ids = self.execute_select(select_sql_query=sql_query)
        if len(ids) == 0:
            return None
        return ids[0][0], ids[0][1]

    def get_blocks_between(self, begin_timestamp=0, end_timestamp=datetime_string_to_timestamp(datetime_string=None),
                           pool_id=SLUSHPOOL_ID, sort_old_to_new=True, number_of_blocks=None):
        """
        Returns a list of blocks in the given pool in the database whose moment is between the given timestamps
        :param number_of_blocks: limits the number of records to return
        :param sort_old_to_new: results are sorted by moment in ascending order if True, and descending if False
        :param pool_id:
        :param begin_timestamp:
        :param end_timestamp:
        :return: A list of tuples of the form (id, moment) where id is the block id and moment is its timestamp
        """
        sql_query = """SELECT id,moment FROM {0} 
        WHERE moment BETWEEN to_timestamp({1}) AND to_timestamp({2}) AND pool_id = {3}
        ORDER BY moment {4} {5};""".format(self.BLOCKS_TABLE_NAME,
                                           begin_timestamp, end_timestamp,
                                           pool_id, "ASC" if sort_old_to_new else "DESC",
                                           "" if number_of_blocks is None else "LIMIT {0}".format(number_of_blocks))
        blocks = self.execute_select(select_sql_query=sql_query)
        return [(b[0], b[1],) for b in blocks]
