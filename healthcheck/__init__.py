import sys

from configuration import is_healthcheck
from healthcheck.watcher import HealthCheckWatcher
from utility.log import logger

HEALTH_CHECK_WATCHER = None


def get_health_check_watcher():
    global HEALTH_CHECK_WATCHER
    """
    :return: the nicehash driver object
    """
    if HEALTH_CHECK_WATCHER is None:
        if not is_healthcheck():
            logger("healthcheck").error("Mode should be healthcheck mode to run healthcheck watcher.")
            sys.exit(-1)
        else:
            HEALTH_CHECK_WATCHER = HealthCheckWatcher()
    return HEALTH_CHECK_WATCHER
