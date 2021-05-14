from controller.controller import Controller

CONTROLLER = None


def get_controller(scope_identifier):
    global CONTROLLER
    """
    :return: the controller object
    """
    if CONTROLLER is None:
        CONTROLLER = Controller(scope_identifier)
    return CONTROLLER
