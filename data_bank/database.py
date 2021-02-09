import random
import random

import psycopg2
from psycopg2 import Error as PGError

from configuration.constants import SLUSHPOOL_NAME, DEFAULT_NUMBER_OF_PAST_BLOCKS_TO_FETCH
from utility.log import logger


class DatabaseException(Exception):
    pass


class Database:
    def __init__(self, user, password, database, host="127.0.0.1", port="5432"):
        """
        A singleton class that is the interface of our data bank database
        """
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database

    def update_data(self, up_to_timestamp):
        """
        Updates the data up to the given timestamp. Uses current timestamp if None is passed.
        :return: None
        """
        # NOTE: this method should execute asynchronically

        # TODO 1. Check the data directory for any new data files to load into the database

        # TODO 2. Check the APIs to see if there is any new data to fetch and insert into the database

        # TODO 3: log some status of the database
        logger('database').info("Updating data up to timestamp {0}.".format(up_to_timestamp))

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

    def key_value_get(self, owner, key):
        """
        Returns the key from the record determined with the owner and key
        :param owner:
        :param key:
        :return: value or None if it does not exist
        """
        if owner is None or key is None:
            raise DatabaseException(
                "Key value put failed because owner or key was None: owner: {0}, key: {1}".format(owner, key))

        sql_query = "SELECT value FROM key_values WHERE owner = '{0}' AND key = '{1}';".format(owner, key)
        results = self.execute_select(sql_query)
        if len(results) == 0:
            return None
        else:
            return results[0][0]

    def key_value_put(self, owner, key, value):
        """
        Upserts the record for owner and key with the given value
        :param owner:
        :param key:
        :param value:
        :return: None
        """
        sql_query = """INSERT INTO key_values (owner, key, value) VALUES ('{0}', '{1}', '{2}') 
         ON CONFLICT ON CONSTRAINT owner_key_unique DO 
         UPDATE SET value = '{2}';""".format(
            owner, key,
            value)
        self.execute_write(sql_query)

    def execute_write(self, write_sql_query, return_generated_id=False):
        """
        Executes the given update/insert/delete query
        :param return_generated_id: The function returns the generated id if True is passed which means it's an insert
        :param write_sql_query: the sql query to execute
        :return: None or the generated ID
        """
        conn = None
        generated_id = None
        try:
            conn = self.create_connection()
            cursor = conn.cursor()
            cursor.execute(write_sql_query)
            if return_generated_id:
                generated_id = cursor.fetchone()[0]
            conn.commit()
            return generated_id
        except (Exception, PGError) as e:
            logger('database').error("Write query failed {0}.".format(write_sql_query))
            logger('database').error("Exception {0}.".format(e))
            raise DatabaseException('SELECT QUERY /// {0} /// FAILED.'.format(write_sql_query))
        finally:
            if conn is not None:
                cursor.close()
                conn.close()

    def execute_select(self, select_sql_query):
        """
        Executes the given select query and returns a list of tuples
        :param select_sql_query: the sql query to execute
        :return: a list of tuples
        """
        conn = None
        try:
            conn = self.create_connection()
            cursor = conn.cursor()
            cursor.execute(select_sql_query)
            resultsList = []
            rows = cursor.fetchall()
            for row in rows:
                resultsList.append([r for r in row])
            return resultsList
        except (Exception, PGError) as e:
            logger('database').error("Select query failed {0}.".format(select_sql_query))
            logger('database').error("Exception {0}.".format(e))
            raise DatabaseException('SELECT QUERY /// {0} /// FAILED.'.format(select_sql_query))
        finally:
            if conn is not None:
                cursor.close()
                conn.close()

    def create_connection(self):
        return psycopg2.connect(user=self.user,
                                password=self.password,
                                host=self.host,
                                port=self.port,
                                database=self.database)
