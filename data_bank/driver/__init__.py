from data_bank.driver.realtime_driver import NiceHashRealtimeDriver
from data_bank.driver.simulation_driver import NiceHashSimulationDriver

NICE_HASH_DRIVER = None
NICE_HASH_SIMULATION_DRIVER = None


def get_nice_hash_simulation_driver():
    global NICE_HASH_SIMULATION_DRIVER
    """
    :return: the nicehash simulation driver object
    """
    if NICE_HASH_SIMULATION_DRIVER is None:
        NICE_HASH_SIMULATION_DRIVER = NiceHashSimulationDriver()
    return NICE_HASH_SIMULATION_DRIVER
