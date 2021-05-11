from configuration import EXECUTION_CONFIGS
from data_bank.orders.orders_database import OrdersDatabaseHandler, OrdersDatabaseUpdater
from data_bank.orders.virtual_orders_handler import VirtualOrdersUpdater, VirtualOrderThreadSafePersistentContainer

ORDER_DB_UPDATER = None
ORDER_DB_HANDLER = None

VIRTUAL_ORDERS_UPDATER = None
VIRTUAL_ORDERS_HANDLER = None


def get_orders_database_handler():
    global ORDER_DB_HANDLER
    """
    :return: the database object
    """
    if ORDER_DB_HANDLER is None:
        ORDER_DB_HANDLER = OrdersDatabaseHandler(EXECUTION_CONFIGS.db_user, EXECUTION_CONFIGS.db_password,
                                                 EXECUTION_CONFIGS.db_orders_database_name,
                                                 EXECUTION_CONFIGS.db_host, EXECUTION_CONFIGS.db_port)
    return ORDER_DB_HANDLER


def get_orders_database_updater():
    global ORDER_DB_UPDATER
    """
    :return: the database updater object
    """
    if ORDER_DB_UPDATER is None:
        ORDER_DB_UPDATER = OrdersDatabaseUpdater(get_orders_database_handler())
    return ORDER_DB_UPDATER


def get_virtual_orders_updater():
    global VIRTUAL_ORDERS_UPDATER
    """
    :return: the virtual order updater object
    """
    if VIRTUAL_ORDERS_UPDATER is None:
        VIRTUAL_ORDERS_UPDATER = VirtualOrdersUpdater(get_orders_database_handler())
    return VIRTUAL_ORDERS_UPDATER


def get_virtual_orders_handler():
    updater = get_virtual_orders_updater()
    return updater.virtual_orders
