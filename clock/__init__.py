from clock.clock import Clock

CLOCK = None


def get_clock():
    global CLOCK
    """
    :return: the clock object
    """
    if CLOCK is None:
        CLOCK = Clock()
    return CLOCK
