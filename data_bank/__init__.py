from configuration import EXECUTION_CONFIGS
from data_bank.mine_database import MineDatabase
from data_bank.simulation_database import SimulationDatabase

DB = None
SIMULATION_DB = None


def get_database():
    global DB
    """
    :return: the database object
    """
    if DB is None:
        DB = MineDatabase(EXECUTION_CONFIGS.db_user, EXECUTION_CONFIGS.db_password, EXECUTION_CONFIGS.db_database_name,
                          EXECUTION_CONFIGS.db_host, EXECUTION_CONFIGS.db_port)
    return DB


def get_simulation_database():
    global SIMULATION_DB
    """
    :return: the simulation data database object
    """
    if SIMULATION_DB is None:
        SIMULATION_DB = SimulationDatabase(EXECUTION_CONFIGS.db_user, EXECUTION_CONFIGS.db_password,
                                     EXECUTION_CONFIGS.db_simulation_database_name,
                                     EXECUTION_CONFIGS.db_host, EXECUTION_CONFIGS.db_port)
    return SIMULATION_DB
