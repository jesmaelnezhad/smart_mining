from configuration import EXECUTION_CONFIGS
from data_bank.database import Database

DB = None


def get_database():
    global DB
    """
    :return: the database object
    """
    if DB is None:
        DB = Database(EXECUTION_CONFIGS.db_user, EXECUTION_CONFIGS.db_password, EXECUTION_CONFIGS.db_database_name,
                      EXECUTION_CONFIGS.db_host, EXECUTION_CONFIGS.db_port)
    return DB
