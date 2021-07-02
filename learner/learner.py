import random
from time import sleep

from clock import get_clock
from clock.clock import calculate_tick_duration_from_sleep_duration
from clock.tick_performer import TickPerformer
from configuration import EXECUTION_CONFIGS
from learner.model_handler import ModelHandler
from utility.log import logger

should_always_recreate_model = EXECUTION_CONFIGS.learner_always_recreate_model
should_save_model = EXECUTION_CONFIGS.learner_save_model


class Learner(TickPerformer):
    def __init__(self):
        """
        A singleton class that is the machine learning agent (called the learner)
        """
        super().__init__()
        self.tick_duration = calculate_tick_duration_from_sleep_duration(EXECUTION_CONFIGS.learner_sleep_duration)
        self.model_handler = ModelHandler()

    def receive_predictions(self):
        """
        Main prediction API that uses the model handler object to return the wanted predictions
        :return: Anything that the predict API of the model handler returns
        """
        # TODO
        return self.model_handler.predict()

    def run(self, should_stop):
        if should_always_recreate_model:
            # create new model anyways
            current_timestamp = get_clock().read_timestamp_of_now()
            self.model_handler.init_model(current_timestamp)
        else:
            # try to load the model from database
            model_loaded = self.model_handler.load_model()
            if not model_loaded:
                current_timestamp = get_clock().read_timestamp_of_now()
                self.model_handler.init_model(current_timestamp)

        while True:
            if should_stop():
                break
            messages = dict()
            try:
                self.message_box_changed.acquire()
                self.message_box_changed.wait(self.tick_duration)
                messages = self.message_box.snapshot(should_clear=True)
            finally:
                self.message_box_changed.release()
            # messages can be used from here.
            current_timestamp = get_clock().read_timestamp_of_now()
            logger('learner').debug("Updating learner at timestamp {0}.".format(current_timestamp))
            # update the ML model if any unseen data exists
            if not self.model_handler.has_model_seen_all_data(current_timestamp):
                self.model_handler.update_model(current_timestamp)
        # Do house-keeping before termination
        if should_save_model:
            logger('learner').debug("Saving the ML model in the database.")
            self.model_handler.save_model()

    def post_run(self):
        logger('learner').info("Learner is terminating.")

    def is_a_daemon(self):
        return False
