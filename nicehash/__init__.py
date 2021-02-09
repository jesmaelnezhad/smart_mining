from configuration import is_simulation_run
from nicehash.realtime_driver import NiceHashRealtimeDriver
from nicehash.simulation_driver import NiceHashSimulationDriver

NICE_HASH_DRIVER = None


def get_nice_hash_driver():
    global NICE_HASH_DRIVER
    """
    :return: the nicehash driver object
    """
    if NICE_HASH_DRIVER is None:
        if is_simulation_run():
            NICE_HASH_DRIVER = NiceHashSimulationDriver()
        else:
            NICE_HASH_DRIVER = NiceHashRealtimeDriver()
    return NICE_HASH_DRIVER
