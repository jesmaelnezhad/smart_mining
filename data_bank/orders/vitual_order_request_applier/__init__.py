from data_bank.orders.vitual_order_request_applier.request_applier import VirtualOrderRequestApplier

REQUEST_APPLIER = None


def get_request_applier(scope_identifier):
    global REQUEST_APPLIER
    """
    :return: the database object
    """
    if REQUEST_APPLIER is None:
        REQUEST_APPLIER = VirtualOrderRequestApplier(scope_identifier=scope_identifier)
    return REQUEST_APPLIER
