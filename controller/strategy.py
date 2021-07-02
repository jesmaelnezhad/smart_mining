import json

from analyzer import get_analyzer
from clock import get_clock
from configuration import EXECUTION_CONFIGS
from controller import get_controller
from learner import get_learner
from utility import persistent_object


CODE_FILE_PATH_KEY = 'code_file_path'
CODE_MODULE_KEY = 'code_module'
CORE_KEY = 'core'


"""
An algorithm run-info is determined with the SSR object, the persisted state, and the virtual order id, and the order id
An object of StrategyStateMachine is created given a SSR object.

It loads the core runner Machine object
If the state machine exists in the database, the 'state' is loaded from the orders database
This class has 
"""


class StrategyStateMachine:

    def __init__(self, owner, object_id, db_handler):
        self.persistent_interface = persistent_object.PersistentObject(owner, object_id)
        self.db_handler = db_handler

    def set_code_file_path(self, code_file_path):
        self[CODE_FILE_PATH_KEY] = code_file_path

    def init_strategy_core_object(self):
        self[CODE_MODULE_KEY] = __import__(self[CODE_FILE_PATH_KEY], fromlist=['object'])
        self[CORE_KEY] = self[CODE_MODULE_KEY].Machine(self.persistent_interface)
        return self[CORE_KEY]

    def execute(self):
        self[CORE_KEY].execute()
        self.persistent_interface.save_in_db(self.db_handler)

    def json(self):
        core = self[CORE_KEY]
        module = self[CODE_MODULE_KEY]
        del self[CORE_KEY]
        del self[CODE_MODULE_KEY]
        try:
            return json.dumps(self.__dict__)
        finally:
            self[CORE_KEY] = core
            self[CODE_MODULE_KEY] = module


class BaseCore:
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