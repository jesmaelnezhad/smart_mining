from utility.log import logger


class Database:
    def __init__(self):
        """
        A singleton class that is the interface of our data bank database
        """
        pass

    def update_data(self, up_to_timestamp):
        """
        Updates the data up to the given timestamp. Uses current timestamp if None is passed.
        :return: None
        """
        # TODO: this method should execute asynchronically
        logger('database').info("Updating data up to timestamp {0}.".format(up_to_timestamp))
