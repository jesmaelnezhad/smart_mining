import json

from utility import persistent_object


class StrategyStateMachine(persistent_object.PersistentObject):
    CODE_FILE_PATH_KEY = 'code_file_path'
    CODE_MODULE_KEY = 'code_module'
    CORE_KEY = 'core'

    def set_code_file_path(self, code_file_path):
        self[self.CODE_FILE_PATH_KEY] = code_file_path

    def init_strategy_core_object(self):
        self[self.CODE_MODULE_KEY] = __import__(self[self.CODE_FILE_PATH_KEY], fromlist=['object'])
        self[self.CORE_KEY] = self[self.CODE_MODULE_KEY].Machine(self)
        return self[self.CORE_KEY]

    def execute(self):
        self[self.CORE_KEY].execute()
        self.save_in_db()

    def json(self):
        core = self[self.CORE_KEY]
        module = self[self.CODE_MODULE_KEY]
        del self[self.CORE_KEY]
        del self[self.CODE_MODULE_KEY]
        try:
            return json.dumps(self.__dict__)
        finally:
            self[self.CORE_KEY] = core
            self[self.CODE_MODULE_KEY] = module





