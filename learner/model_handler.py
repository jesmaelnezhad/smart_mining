class ModelHandler:
    """
    This class holds the machine learning model that is created/updated/used by the controller.
    The API provided by this class must be thread-safe.
    """

    def __init__(self):
        """
        Initializes the ModelHandler object
        """
        # TODO
        pass

    def __str__(self):
        """
        :return: The string that represents the model handler
        """
        return self.get_model_identifier()

    def get_model_identifier(self):
        """
        Returns the unique identifier of the ML model kept in this handler
        :return: string that can be used to identify a model uniquely
        """
        # TODO
        pass

    def get_model_info(self):
        """
        Returns the information that describes the current state of the model
        :return: ???? the descriptive information of the current state of the ML model
        """
        # TODO
        pass

    def predict(self):
        """
        Main API used for obtaining predictions from a trained model
        :return: None if no model is fit yet, and otherwise, ????
        """
        # TODO
        pass

    def init_model(self, up_to_timestamp):
        """
        Creates an ML model based on the current state of data up to the given timestamp
        :param up_to_timestamp: Looks for data up to this timestamp
        :return: ?????
        """
        # TODO
        pass

    def fit_model(self, up_to_timestamp):
        """
        Fits the ML model from scratch based on the available data
        :return: ?????
        """
        # TODO
        pass

    def has_model_seen_all_data(self, up_to_timestamp):
        """
        :param up_to_timestamp: The latest timestamp that would be checked in the database to see if there is any
        data not considered in the model yet.
        :return: True if there are any new data points in the database (end.or_event., up to the given timestamp) that is not
        used in training the model and is new to it; and False otherwise.
        """
        # TODO
        pass

    def update_model(self, up_to_timestamp):
        """
        If any new data points exist, this method uses them to update the model.
        :param up_to_timestamp: Looks for new data up to this timestamp
        :return: True if the model was updated; and False otherwise.
        """
        if self.has_model_seen_all_data(up_to_timestamp):
            self.refit_model(up_to_timestamp)
            return True
        return False

    def refit_model(self, up_to_timestamp):
        """
        Calls refit on the ML model to feed new data points (which are considered only up to the given timestamp)
        :return: None
        """
        # TODO
        pass

    def load_model(self):
        """
        This method uses the model identifier to find the latest stored version of this model in the database
        and if it does find this model, it loads it from the database and populates the object.
        :return: True if any stored version is found, and False otherwise.
        """
        # TODO
        pass

    def save_model(self):
        """
        This method stores the ML model held in this handler in the database.
        :return: True if the model was saved in the database successfully, and False otherwise
        """
        # TODO
        pass

