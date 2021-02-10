import random

from data_bank import get_database_handler
from utility.log import logger


class SimulationEvaluator:
    def __init__(self):
        """
        A singleton class that is the simulation evaluator
        """
        pass

    def perform_tick(self, up_to_timestamp):
        """
        Performs one tick.
        :return: None
        """
        # TODO: this method should perform asynchronically
        logger('simulation-evaluator').info("Performing a tick at timestamp {0}.".format(up_to_timestamp))
