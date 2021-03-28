import glob, os
import sys
from time import sleep

import psycopg2
from psycopg2 import Error as PGError

from clock import get_clock
from clock.clock import calculate_tick_duration_from_sleep_duration
from clock.tick_performer import TickPerformer
from configuration import EXECUTION_CONFIGS
from configuration.constants import SLUSHPOOL_NAME, DEFAULT_NUMBER_OF_PAST_BLOCKS_TO_FETCH
from utility.log import logger


class DatabaseException(Exception):
    pass


class DatabaseUpdater(TickPerformer):
    KV_OWNER_KEY = 'db'
    LOADED_DATA_FILES_LIST_KEY = 'loaded_data_files_list'

    def __init__(self, handler):
        """
        A singleton class that is the interface of databases updater
        """
        super().__init__()
        self.handler = handler
        self.data_files_loaded = []
        self.init_loaded_data_files_info()
        self.tick_duration = self.get_tick_duration()

    def get_tick_duration(self):
        pass

    def run(self, should_stop):
        while True:
            if should_stop():
                break
            sleep(self.tick_duration)
            current_timestamp = get_clock().read_timestamp_of_now()
            self.update_data(current_timestamp)

    def post_run(self):
        logger('database').info("Database ({0}) is terminating.".format(self.get_db_csv_name_suffix()))

    def is_a_daemon(self):
        return False

    def get_db_csv_name_suffix(self):
        raise DatabaseException("The base database class should not be used.")

    def update_data(self, up_to_timestamp):
        """
        Updates the data up to the given timestamp. Uses current timestamp if None is passed.
        :return: None
        """
        # NOTE: this method should execute asynchronically

        # TODO 1. Check the data directory for any new data files to load into the database
        new_csv_files = self.check_new_data_files_to_load()
        if len(new_csv_files) != 0:
            self.load_new_csv_files(new_csv_files)

        # TODO 2. Check the APIs to see if there is any new data to fetch and insert into the database

        # TODO 3: log some status of the database

    def init_loaded_data_files_info(self):
        stored_value = self.handler.key_value_get(self.KV_OWNER_KEY, self.LOADED_DATA_FILES_LIST_KEY)
        if stored_value is None or stored_value == "":
            self.handler.key_value_put(self.KV_OWNER_KEY, self.LOADED_DATA_FILES_LIST_KEY, "")
            self.data_files_loaded = []
        else:
            self.data_files_loaded = stored_value.split(',')

    def remember_csv_file_was_loaded(self, file_name):
        self.data_files_loaded.append(file_name)
        self.handler.key_value_put(self.KV_OWNER_KEY, self.LOADED_DATA_FILES_LIST_KEY, ",".join(self.data_files_loaded))

    def check_new_data_files_to_load(self):
        new_files_to_load = []

        directory_path = EXECUTION_CONFIGS.db_csv_data_dir
        file_format = "*.*.{0}.csv".format(self.get_db_csv_name_suffix())
        file_search_pattern = os.path.join(directory_path, file_format)
        for file_name in glob.glob(file_search_pattern):
            if file_name not in self.data_files_loaded:
                new_files_to_load.append(file_name)
        return new_files_to_load

    def load_new_csv_files(self, new_files_to_load):
        for file_name in new_files_to_load:
            success = self.load_csv_file(file_name)
            if success:
                self.remember_csv_file_was_loaded(file_name)
                logger('database/updater').info("CSV file {0} was loading into the database successfully.".format(file_name))

    def load_csv_file(self, full_file_path):
        file_name = os.path.basename(full_file_path)
        table_name = file_name[:file_name.find('.')]
        # file_full_path = os.path.join(EXECUTION_CONFIGS.project_root_directory,
        #                               EXECUTION_CONFIGS.db_csv_data_dir,
        #                               file_name)
        return self.handler.load_csv_file(table_name, full_file_path)


class DatabaseHandler:
    def __init__(self, user, password, database, host="127.0.0.1", port="5432"):
        """
        A singleton class that is the interface of databases
        """
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database

    def key_value_get(self, owner, key):
        """
        Returns the key from the record determined with the owner and key
        :param owner:
        :param key:
        :return: value or None if it does not exist
        """
        if owner is None or key is None:
            raise DatabaseException(
                "Key value get failed because owner or key was None: owner: {0}, key: {1}".format(owner, key))

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
        :param persistent_connection: when passed non None, no new connection will be made and it won't be closed
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
            logger('database/handler').error("Write query failed {0}.".format(write_sql_query))
            logger('database/handler').error("Exception {0}.".format(e))
            raise DatabaseException('WRITE QUERY /// {0} /// FAILED.'.format(write_sql_query))
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
            logger('database/handler').error("Select query failed {0}.".format(select_sql_query))
            logger('database/handler').error("Exception {0}.".format(e))
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

    def load_csv_file(self, table_name, file_full_path):
        try:
            with open(file_full_path, 'r') as csv_file:
                header = csv_file.readline()
                columns = header.split(EXECUTION_CONFIGS.db_csv_separator)
                record_line = csv_file.readline()
                while record_line:
                    record_values = record_line.split(EXECUTION_CONFIGS.db_csv_separator)
                    sql_insert_statement = """INSERT INTO {0} ({1}) VALUES ({2});""".format(table_name,
                                                                                            ",".join(columns),
                                                                                            ",".join(record_values))
                    try:
                        self.execute_write(write_sql_query=sql_insert_statement)
                    except DatabaseException:
                        logger('database/handler').error("Error: inserting record from csv file failed.")
                    record_line = csv_file.readline()
            return True
        except (Exception, PGError) as e:
            logger('database/handler').error("Loading CSV file failed {0}.".format(file_full_path))
            logger('database/handler').error("Exception {0}.".format(e))
            return False
