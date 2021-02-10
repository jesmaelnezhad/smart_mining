from configuration import EXECUTION_CONFIGS
from data_bank.mine_database import MineDatabaseHandler, MineDatabaseUpdater
from data_bank.simulation_database import SimulationDatabaseHandler, SimulationDatabaseUpdater

DB_UPDATER = None
SIMULATION_DB_UPDATER = None
DB_HANDLER = None
SIMULATION_DB_HANDLER = None


def get_database_handler():
    global DB_HANDLER
    """
    :return: the database object
    """
    if DB_HANDLER is None:
        DB_HANDLER = MineDatabaseHandler(EXECUTION_CONFIGS.db_user, EXECUTION_CONFIGS.db_password, EXECUTION_CONFIGS.db_database_name,
                                         EXECUTION_CONFIGS.db_host, EXECUTION_CONFIGS.db_port)
    return DB_HANDLER


def get_simulation_database_handler():
    global SIMULATION_DB_HANDLER
    """
    :return: the simulation data database object
    """
    if SIMULATION_DB_HANDLER is None:
        SIMULATION_DB_HANDLER = SimulationDatabaseHandler(EXECUTION_CONFIGS.db_user, EXECUTION_CONFIGS.db_password,
                                                          EXECUTION_CONFIGS.db_simulation_database_name,
                                                          EXECUTION_CONFIGS.db_host, EXECUTION_CONFIGS.db_port)
    return SIMULATION_DB_HANDLER


def get_database_updater():
    global DB_UPDATER
    """
    :return: the database updater object
    """
    if DB_UPDATER is None:
        DB_UPDATER = MineDatabaseUpdater(get_database_handler())
    return DB_UPDATER


def get_simulation_database_updater():
    global SIMULATION_DB_UPDATER
    """
    :return: the simulation data database updater object
    """
    if SIMULATION_DB_UPDATER is None:
        SIMULATION_DB_UPDATER = SimulationDatabaseUpdater(get_simulation_database_handler())
    return SIMULATION_DB_UPDATER
