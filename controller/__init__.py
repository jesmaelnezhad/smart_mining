from controller.controller import Controller

CONTROLLER = None


def get_controller():
    global CONTROLLER
    """
    :return: the controller object
    """
    if CONTROLLER is None:
        CONTROLLER = Controller()
    return CONTROLLER
