from utility.log import logger


class Analyzer:
    def __init__(self):
        """
        A singleton class that is the analyzer
        """
        pass

    def update_analytics(self, up_to_timestamp):
        """
        Updates the analytics results up to the given timestamp.
        :return: None
        """
        # TODO: this method should perform asynchronically
        logger('analyzer').info("Updating analytics up to timestamp {0}.".format(up_to_timestamp))
