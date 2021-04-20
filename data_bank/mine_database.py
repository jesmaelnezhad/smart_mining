import datetime
import time
import random

import pytz

from clock.clock import calculate_tick_duration_from_sleep_duration
from configuration import EXECUTION_CONFIGS
from configuration.constants import SLUSHPOOL_ID, SLUSHPOOL_DATA_FETCH_START_UTC_TIMESTAMP, SLUSHPOOL_API_BASE_URL, \
    DATA_FETCH_API_INTER_DELAY
from data_bank.database import DatabaseHandler, DatabaseUpdater, DatabaseException
from utility.datetime_helpers import datetime_string_to_timestamp
from utility.log import logger
import requests


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

        # Updating the block table
        self.update_blocks(up_to_timestamp)

        logger('mine-database').debug("Updating data up to timestamp {0}.".format(up_to_timestamp))

    def update_blocks(self, up_to_timestamp, beginning=SLUSHPOOL_DATA_FETCH_START_UTC_TIMESTAMP, pool_id=SLUSHPOOL_ID):
        """
        :param pool_id: The pool whose blocks we want
        :param beginning: If the blocks table is empty and should_fill_empty_db is True in configs, it starts from
        this moment to fill the blocks table
        :param up_to_timestamp: Makes sure the data of the blocks and pools tables are up to date from the beginning
        until up_to_timestamp
        :return: None
        """
        if not EXECUTION_CONFIGS.should_use_api:
            return
        # When is now?
        now_dt = datetime.datetime.fromtimestamp(up_to_timestamp, tz=pytz.UTC)

        # Check where the beginning is
        latest_block = self.handler.get_latest_block_info(pool_id=pool_id)
        if latest_block is None:
            if EXECUTION_CONFIGS.should_fill_empty_db:
                beg_dt = datetime.datetime.fromtimestamp(beginning, tz=pytz.UTC)
            else:
                return
        else:
            block_id, block_moment = latest_block
            beg_dt = block_moment

        # Start day by day from the beginning
        while beg_dt <= now_dt:
            self.update_blocks_at_date(year=beg_dt.year, month=beg_dt.month, day=beg_dt.day)
            beg_dt += datetime.timedelta(days=1)

    def update_blocks_at_date(self, year, month, day, filter_pool_id=SLUSHPOOL_ID):
        base_url = SLUSHPOOL_API_BASE_URL
        url = base_url + "/{0}{1}{2}".format(year, str(month).zfill(2), str(day).zfill(2))
        logger("mine-db/update-blocks").info(url)
        response = requests.get(url)
        time.sleep(5.0)
        factor = 1
        while response.status_code != 200:
            print(response.status_code)
            time.sleep(DATA_FETCH_API_INTER_DELAY * factor)
            response = requests.get(url)
            factor = min(factor * 2, 4)
        data_list = response.json()['data']
        if data_list is None:
            return
        for block in data_list:
            block_id = block['height']
            timestamp = block['timestamp']
            pool_name = block['extras']['pool_name']
            pool_id = self.handler.get_pool_id(str(pool_name).lower())
            if pool_id != filter_pool_id:
                continue
            sql_query = """INSERT INTO blocks(id, moment, pool_id) VALUES ({0},
             to_timestamp({1}), {2}) ON CONFLICT DO NOTHING;""".format(block_id, timestamp, pool_id)
            try:
                self.handler.execute_write(write_sql_query=sql_query)
            except DatabaseException:
                logger('mine-database/updater').error("Error: inserting block with id {0}".format(block_id))


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

    def get_pool_id(self, pool_name):
        """
        Returns the id of the given pool; and inserts one if not exist
        :param pool_name: The name of the pool
        :return: pool_id
        """
        sql_query = "SELECT id FROM pools WHERE name = '{0}';".format(pool_name)
        ids = self.execute_select(sql_query)
        if len(ids) == 0:
            sql_query = "INSERT INTO pools(name) VALUES ('{0}') RETURNING id;".format(pool_name)
            pool_id = self.execute_write(sql_query, return_generated_id=True)
        else:
            pool_id = ids[0][0]
        return pool_id

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

    def get_slushpool_info(self, begin_timestamp=0, end_timestamp=datetime_string_to_timestamp(datetime_string=None),
                           sort_old_to_new=True, fields_name=None):
        """
        Returns a list of pool info with time stamp for slushpool from database
        :param sort_old_to_new: results are sorted by moment in ascending order if True, and descending if False
        :param fields_name: a list of fields name to be retrieved from database, if None all field will return
        :param begin_timestamp:
        :param end_timestamp:
        :return: A list of tuples of the form (moment timestamp, [fields values])
        """
        # check fields names
        valid_names = ['hash_rate', 'scoring_hash_rate',
                       'active_users', 'active_workers']
        if fields_name is None:
            fields_name = valid_names.copy()
        valid_fields = True
        for field in fields_name:
            if field not in valid_names:
                valid_fields = False
                break
        if not valid_fields:
            return None

        # retrieve info from database
        sql_query = """SELECT moment,{1} FROM {2}
        WHERE moment BETWEEN to_timestamp({3}) AND to_timestamp({4})
        ORDER BY moment {5};""".format("%m/%d/%Y-%H:%M:%S", ",".join(fields_name),
                                       self.SLUSHPOOL_TABLE_NAME,
                                       begin_timestamp, end_timestamp,
                                       "ASC" if sort_old_to_new else "DESC")
        pool_info = self.execute_select(select_sql_query=sql_query)
        return [(info[0].timestamp(), info[1:]) for info in pool_info]

    def get_network_info(self, begin_timestamp=0, end_timestamp=datetime_string_to_timestamp(datetime_string=None),
                         sort_old_to_new=True, fields_name=None):
        """
        Returns a list of pool info with time stamp for slushpool from database
        :param sort_old_to_new: results are sorted by moment in ascending order if True, and descending if False
        :param fields_name: a list of fields name to be retrieved from database, if None all field will return
        :param begin_timestamp:
        :param end_timestamp:
        :return: A list of tuples of the form (moment timestamp, [fields values])
        """
        # check fields names
        valid_names = ['hash_rate', 'scoring_hash_rate',
                       'active_users', 'active_workers']
        if fields_name is None:
            fields_name = valid_names.copy()
        valid_fields = True
        for field in fields_name:
            if field not in valid_names:
                valid_fields = False
                break
        if not valid_fields:
            return None

        # retrieve info from database
        sql_query = """SELECT moment,{1} FROM {2}
        WHERE moment BETWEEN to_timestamp({3}) AND to_timestamp({4})
        ORDER BY moment {5};""".format("%m/%d/%Y-%H:%M:%S", ",".join(fields_name),
                                       self.SLUSHPOOL_TABLE_NAME,
                                       begin_timestamp, end_timestamp,
                                       "ASC" if sort_old_to_new else "DESC")
        pool_info = self.execute_select(select_sql_query=sql_query)
        return [(info[0].timestamp(), info[1:]) for info in pool_info]
