from nicehash.vitual_order_request_applier.request_applier import VirtualOrderRequestApplier

REQUEST_APPLIER = None


def get_request_applier():
    global REQUEST_APPLIER
    """
    :return: the database object
    """
    if REQUEST_APPLIER is None:
        REQUEST_APPLIER = VirtualOrderRequestApplier()
    return REQUEST_APPLIER
