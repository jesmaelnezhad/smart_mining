import logging


# Initialize the logging utility
from configuration import EXECUTION_CONFIGS

FORMAT = '%(asctime)s - %(name)s -  %(levelname)s - %(message)s'
logging.basicConfig(level=logging.DEBUG, format=FORMAT)


def logger(name):
    logger_ = logging.getLogger(name)
    logger_.setLevel(EXECUTION_CONFIGS.log_level)
    return logger_
