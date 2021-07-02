from data_bank.orders import get_orders_database_handler
from data_bank.virtual_orders.virtual_order_applier import VirtualOrderApplier
from data_bank.virtual_orders.virtual_orders import VirtualOrdersUpdater

REQUEST_APPLIER = None
VIRTUAL_ORDERS_UPDATER = None
VIRTUAL_ORDERS_HANDLER = None


def get_request_applier(scope_identifier):
    global REQUEST_APPLIER
    """
    :return: the database object
    """
    if REQUEST_APPLIER is None:
        REQUEST_APPLIER = VirtualOrderApplier(scope_identifier=scope_identifier)
    return REQUEST_APPLIER


def get_virtual_orders_updater(scope_identifier):
    global VIRTUAL_ORDERS_UPDATER
    """
    :return: the virtual order updater object
    """
    if VIRTUAL_ORDERS_UPDATER is None:
        VIRTUAL_ORDERS_UPDATER = VirtualOrdersUpdater(get_orders_database_handler(scope_identifier))
    return VIRTUAL_ORDERS_UPDATER


def get_virtual_orders_handler(scope_identifier):
    updater = get_virtual_orders_updater(scope_identifier)
    return updater.get_virtual_orders_handler()
