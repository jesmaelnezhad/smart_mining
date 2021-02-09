import sys
import traceback
from time import sleep

from configuration import EXECUTION_CONFIGS
from nicehash import get_nice_hash_driver
from utility import log
from analyzer import get_analyzer
from controller import get_controller
from data_bank import get_database


def tick(current_timestamp):
    """
    Everyting that repeats at each tick
    :param current_timestamp: the timestamp of when the tick is happening
    :return: None
    """
    # logic that should repeat periodically
    # Update any information retrieved from nicehash (or perform any logic needed in nicehash mock)
    get_nice_hash_driver().perform_tick(up_to_timestamp=current_timestamp)
    # Update the data in the data bank
    get_database().update_data(up_to_timestamp=current_timestamp)
    # Update analysis results and/or learning models
    get_analyzer().update_analytics(up_to_timestamp=current_timestamp)
    # Wake up the controller to perform one tick
    get_controller().perform_tick(up_to_timestamp=current_timestamp)
    log.logger('main/tick').info('Periodic logic.')


if __name__ == '__main__':
    try:
        timestamp_of_now = EXECUTION_CONFIGS.execution_start_timestamp
        while True:
            tick(timestamp_of_now)
            sleep(EXECUTION_CONFIGS.tick_execution_interval_seconds)
            timestamp_of_now += EXECUTION_CONFIGS.tick_duration_seconds
    except KeyboardInterrupt:
        log.logger('main').info('Program terminating upon keyboard interrupt.')
    except Exception as e:
        log.logger('main').info("Exception {0}".format(e))
        traceback.print_exc(file=sys.stdout)
        sys.exit(1)
    sys.exit(0)
