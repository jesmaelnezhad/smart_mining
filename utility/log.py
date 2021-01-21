import logging

from configuration import configs

# Initialize the logging utility
FORMAT = '%(asctime)s - %(name)s -  %(levelname)s - %(message)s'
logging.basicConfig(level=logging.DEBUG, format=FORMAT)


def logger(name):
    logger_ = logging.getLogger(name)
    logger_.setLevel(configs.EXECUTION_CONFIGS['log_level'])
    return logger_
