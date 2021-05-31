from analyzer import get_analyzer
from learner import get_learner
from clock import get_clock
from configuration import EXECUTION_CONFIGS
from controller import get_controller
from data_bank import get_database_handler, get_simulation_database_handler
from data_bank.orders import get_virtual_orders_handler


class BaseMachine:
    """
    The base class of any Machine class provided for a strategy algorithm.
    """
    def __init__(self):
        self.analyzer = get_analyzer()
        self.learner = get_learner()
        self.clock = get_clock()
        self.configs = EXECUTION_CONFIGS
        self.controller = get_controller()
        self.mine_db_handler = get_database_handler()
        self.simulation_db_handler = get_simulation_database_handler()
        self.virtual_orders_handler = get_virtual_orders_handler()

    def start(self, current_timestamp):
        """
        Method that will be called upon algorithm start
        :param current_timestamp:
        :return:
        """
        pass

    def execute(self, current_timestamp):
        """
        Method that will be called at each given trigger
        :param current_timestamp:
        :return:
        """
        pass

    def end(self, current_timestamp):
        """
        Method that will be called upon algorithm end
        :param current_timestamp:
        :return:
        """