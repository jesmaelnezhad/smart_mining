import logging


# Initialize the logging utility
from configuration import EXECUTION_CONFIGS

FORMAT = EXECUTION_CONFIGS.log_format
logging.basicConfig(level=logging.DEBUG, format=FORMAT)


def logger(name):
    logger_ = logging.getLogger(name)
    logger_.setLevel(EXECUTION_CONFIGS.log_level)
    return logger_
