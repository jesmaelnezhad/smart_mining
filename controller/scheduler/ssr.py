import enum
import yaml

from configuration.constants import SSR_KEY_SSR, SSR_KEY_BASE_NAME, SSR_KEY_NAME, SSR_KEY_ABSTRACT, SSR_KEY_PACKAGE, \
    SSR_KEY_LIFECYCLE, SSR_KEY_TRIGGERS, SSR_KEY_ORDER_INFO, SSR_KEY_LIFECYCLE_START, SSR_KEY_LIFECYCLE_END, \
    SSR_KEY_LIFECYCLE_EXECUTION, SSR_KEY_ORDER_PHYSICAL_ORDER_ID, SSR_KEY_LIFECYCLE_EXECUTION_PARALLEL, \
    SSR_KEY_LIFECYCLE_EXECUTION_REPEAT
from utility.log import logger


def create_ssr_loader():
    return SSRLoader()


def extends_a_base_request(data_dict):
    if SSR_KEY_BASE_NAME not in data_dict.keys() or data_dict[SSR_KEY_BASE_NAME] == '':
        return False
    return True


class SSR:
    class TriggerType(enum.Enum):
        PERIOD_FIXED = ''

    class Trigger:
        def __init__(self, description_str):
            self.description_str = description_str

        def __str__(self):
            return self.description_str

    def get_dict(self):
        d = dict()
        for k, v in self.__dict__.items():
            if k == SSR_KEY_LIFECYCLE:
                d[k] = v.get_dict()
            elif k == SSR_KEY_ORDER_INFO:
                d[k] = v.get_dict()
            elif k == SSR_KEY_TRIGGERS:
                d[k] = [c.description_str for c in v]
            else:
                d[k] = v
        return d

    def __init__(self):
        self.__dict__[SSR_KEY_ABSTRACT] = False
        self.__dict__[SSR_KEY_NAME] = str()
        self.__dict__[SSR_KEY_BASE_NAME] = str()
        self.__dict__[SSR_KEY_PACKAGE] = str()
        self.__dict__[SSR_KEY_LIFECYCLE] = SSRLifecycle()
        self.__dict__[SSR_KEY_TRIGGERS] = list()
        self.__dict__[SSR_KEY_ORDER_INFO] = SSROrderInfo()

    def load_from_dictionary(self, data_dict):
        for key, value in data_dict.items():
            if key == SSR_KEY_ABSTRACT:
                self.__dict__[SSR_KEY_ABSTRACT] = bool(value)
            elif key in [SSR_KEY_NAME, SSR_KEY_BASE_NAME, SSR_KEY_PACKAGE]:
                self.__dict__[key] = str(value)

            if key in [SSR_KEY_LIFECYCLE, SSR_KEY_ORDER_INFO]:
                parameter_obj = None
                if key == SSR_KEY_LIFECYCLE:
                    parameter_obj = SSRLifecycle()
                elif key == SSR_KEY_ORDER_INFO:
                    parameter_obj = SSROrderInfo()
                # do not override a whole sub-tree
                if key in self.__dict__.keys():
                    parameter_obj = self.__dict__[key]
                parameter_obj.load_from_dictionary(value)
                self.__dict__[key] = parameter_obj

            if key == SSR_KEY_TRIGGERS:
                self.__dict__[key] = list()
                for trigger_str in value:
                    self.__dict__[key].append(SSR.Trigger(trigger_str))

    def is_abstract(self):
        return self.__dict__[SSR_KEY_ABSTRACT]

    def get_name(self):
        return self.__dict__[SSR_KEY_NAME]

    def get_base_name(self):
        return self.__dict__[SSR_KEY_BASE_NAME]

    def get_package(self):
        return self.__dict__[SSR_KEY_PACKAGE]

    def get_lifecycle(self):
        return self.__dict__[SSR_KEY_LIFECYCLE]

    def get_triggers(self):
        return self.__dict__[SSR_KEY_TRIGGERS]

    def get_order_info(self):
        return self.__dict__[SSR_KEY_ORDER_INFO]


class SSRLifecycle:
    class StartConditionType(enum.Enum):
        TS_FIXED = ''

    class StartCondition:
        def __init__(self, description_str):
            self.description_str = description_str

        def __str__(self):
            return self.description_str

    class EndConditionType(enum.Enum):
        TS_FIXED = ''

    class EndCondition:
        def __init__(self, description_str):
            self.description_str = description_str

        def __str__(self):
            return self.description_str

    def get_dict(self):
        d = dict()
        for k, v in self.__dict__.items():
            if k == SSR_KEY_LIFECYCLE_START:
                d[k] = [c.description_str for c in v]
            elif k == SSR_KEY_LIFECYCLE_END:
                d[k] = [c.description_str for c in v]
            else:
                d[k] = v
        return d

    def load_from_dictionary(self, data_dict):
        for key, value in data_dict.items():
            if key == SSR_KEY_LIFECYCLE_START:
                condition_list = value
                conditions = []
                for desc_str in condition_list:
                    new_condition = SSRLifecycle.StartCondition(desc_str)
                    conditions.append(new_condition)
                self.__dict__[key] = conditions
            elif key == SSR_KEY_LIFECYCLE_END:
                condition_list = value
                conditions = []
                for desc_str in condition_list:
                    new_condition = SSRLifecycle.EndCondition(desc_str)
                    conditions.append(new_condition)
                self.__dict__[key] = conditions
            elif key == SSR_KEY_LIFECYCLE_EXECUTION:
                execution_obj = dict()
                if key in self.__dict__.keys():
                    execution_obj = self.__dict__[key]
                for exec_key, exec_value in value.items():
                    execution_obj[exec_key] = bool(exec_value)
                self.__dict__[key] = execution_obj

    def get_start_conditions(self):
        return self.__dict__[SSR_KEY_LIFECYCLE_START]

    def get_end_conditions(self):
        return self.__dict__[SSR_KEY_LIFECYCLE_END]

    def is_execution_in_parallel(self):
        return self.__dict__[SSR_KEY_LIFECYCLE_EXECUTION][SSR_KEY_LIFECYCLE_EXECUTION_PARALLEL]

    def should_execution_repeat(self):
        return self.__dict__[SSR_KEY_LIFECYCLE_EXECUTION][SSR_KEY_LIFECYCLE_EXECUTION_REPEAT]


class SSROrderInfo:

    def get_dict(self):
        return self.__dict__

    def load_from_dictionary(self, data_dict):
        for key, value in data_dict.items():
            if key == SSR_KEY_ORDER_PHYSICAL_ORDER_ID:
                self.__dict__[key] = str(value)




class SSRLoader:
    def __init__(self):
        self.ssr_objects = dict()
        self.ssr_yaml_data = dict()
        self.parse_yaml_files()

    def parse_yaml_files(self):
        file_paths = ['files/strategies/strategy_base.yaml',
                      'files/strategies/strategy_sample.yaml']
        for path in file_paths:
            with open(path, 'r') as yaml_file:
                try:
                    ssr_data = yaml.safe_load(yaml_file)
                    self.ssr_yaml_data[ssr_data[SSR_KEY_SSR][SSR_KEY_NAME]] = ssr_data
                except yaml.YAMLError as err:
                    logger("SSR/parse").error("Had an error while parsing yaml file {0}".format(path))

    def load_ssr_by_name(self, name):
        """

        :param name:
        :return: SSR
        """
        if name in self.ssr_objects.keys():
            return self.ssr_objects[name]
        obj = self.create_ssr_obj_from_dict(self.ssr_yaml_data[name])
        self.ssr_objects[name] = obj
        return obj

    def create_ssr_obj_from_dict(self, data_dict):
        # check that there is only one key and it is 'ssr'
        if len(data_dict.keys()) != 1:
            return False
        if SSR_KEY_SSR not in data_dict.keys():
            return False
        ssr_data = data_dict[SSR_KEY_SSR]
        if extends_a_base_request(ssr_data):
            ssr_base_obj = self.load_ssr_by_name(ssr_data[SSR_KEY_BASE_NAME])
            ssr_base_obj.load_from_dictionary(ssr_data)
            return ssr_base_obj
        else:
            ssr_obj = SSR()
            ssr_obj.load_from_dictionary(ssr_data)
            return ssr_obj
