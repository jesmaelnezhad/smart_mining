import random

from controller import base_core, controller, strategy
from analyzer import analyzer
from clock import clock
from configuration import configs, constants
from data_bank import mine_database, simulation_database
from data_bank.orders import virtual_orders
from learner import learner


class Machine(base_core.BaseMachine):
    def __init__(self, persistent_interface):
        super(Machine, self).__init__()
        self.persistent_interface = persistent_interface

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
        print(self.persistent_interface['test'])
        self.persistent_interface['test'] = "test" + str(random.randint(10, 20))
        print("Printing in execute of the machine")

    def end(self, current_timestamp):
        """
        Method that will be called upon algorithm end
        :param current_timestamp:
        :return:
        """

