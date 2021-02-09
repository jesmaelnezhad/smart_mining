import random

from data_bank import get_database
from utility.log import logger


class Controller:
    def __init__(self):
        """
        A singleton class that is the controller
        """
        pass

    def perform_tick(self, up_to_timestamp):
        """
        Performs one tick.
        :return: None
        """
        # TODO: this method should perform asynchronically
        logger('controller').info("Performing a tick at timestamp {0}.".format(up_to_timestamp))
