from configuration import EXECUTION_CONFIGS
from data_bank.orders.orders_database import OrdersDatabaseHandler, OrdersDatabaseUpdater
from data_bank.scope import RealtimeScopeIdentifier, SimulationScopeIdentifier

ORDER_DB_UPDATER = None
ORDER_DB_HANDLER = None

REALTIME_SCOPE_IDENTIFIER = None
SIMULATION_SCOPE_IDENTIFIER = None


def get_realtime_scope_identifier():
    global REALTIME_SCOPE_IDENTIFIER
    if REALTIME_SCOPE_IDENTIFIER is None:
        REALTIME_SCOPE_IDENTIFIER = RealtimeScopeIdentifier()
    return REALTIME_SCOPE_IDENTIFIER


def get_simulation_scope_identifier():
    global SIMULATION_SCOPE_IDENTIFIER
    if SIMULATION_SCOPE_IDENTIFIER is None:
        SIMULATION_SCOPE_IDENTIFIER = SimulationScopeIdentifier()
    return SIMULATION_SCOPE_IDENTIFIER


def get_orders_database_handler(scope_identifier):
    global ORDER_DB_HANDLER
    """
    :return: the database object
    """
    if ORDER_DB_HANDLER is None:
        ORDER_DB_HANDLER = OrdersDatabaseHandler(scope_identifier, EXECUTION_CONFIGS.db_user,
                                                 EXECUTION_CONFIGS.db_password,
                                                 EXECUTION_CONFIGS.db_orders_database_name,
                                                 EXECUTION_CONFIGS.db_host, EXECUTION_CONFIGS.db_port)
    return ORDER_DB_HANDLER


def get_orders_database_updater(scope_identifier):
    global ORDER_DB_UPDATER
    """
    :return: the database updater object
    """
    if ORDER_DB_UPDATER is None:
        ORDER_DB_UPDATER = OrdersDatabaseUpdater(get_orders_database_handler(scope_identifier), scope_identifier)
    return ORDER_DB_UPDATER
