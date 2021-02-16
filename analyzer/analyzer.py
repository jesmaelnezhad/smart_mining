from statistics import mean
from threading import Lock
from time import sleep

from clock import get_clock
from clock.clock import calculate_tick_duration_from_sleep_duration
from clock.tick_performer import TickPerformer
from configuration import EXECUTION_CONFIGS
from utility.datetime_helpers import size_in_seconds
from utility.log import logger
from data_bank import mine_database as mine_db



class AverageWindowMetric:
    """
    Any metric that is calculated in a short window, and is averaged over
    all instances of such window over a larger time window in the past
    """

    def __init__(self, short_window_length_seconds, large_window_length_seconds):
        self.short_window_length = short_window_length_seconds
        self.large_window_length = large_window_length_seconds
        self.latest_timestamp = None
        self.window_values = None
        self.window_values_mutex = Lock()

    def set_latest_timestamp(self, latest_timestamp):
        """
        Sets the ending point of the large window. Setting this property invalidates the window_values
        :param latest_timestamp:
        :return:
        """
        self.window_values_mutex.acquire()
        try:
            self.latest_timestamp = latest_timestamp
            self.window_values = None
        finally:
            self.window_values_mutex.release()

    def get_short_window_boundaries(self, latest_timestamp=None):
        """
        Calculates the boundaries of the short windows that exist in the larger interval
        :param latest_timestamp: the larger window is defined by its length and its end point which is this argument
        :return: the list of window boundaries from latest to oldest
        """

        # check if input latest timestamp parameter is not null, then add it as latest timestamp variable of the object
        if latest_timestamp is not None:
            self.set_latest_timestamp(latest_timestamp)
        # if object has not latest timestamp value yet, short window boundaries cannot be set
        if self.latest_timestamp is None:
            return None
        # set short window boundaries if object has latest timestamp value
        self.window_values_mutex.acquire()
        try:
            window_boundaries = []
            next_boundary = self.latest_timestamp
            while ((self.latest_timestamp - next_boundary) + self.short_window_length) <= self.large_window_length:
                window_boundaries.append(next_boundary)
                next_boundary -= self.short_window_length
            return window_boundaries
        finally:
            self.window_values_mutex.release()

    def update_window_values(self):
        """
        Updates the window values
        :return: None
        """
        window_boundaries, window_values = self.calculate_new_window_values_and_boundaries()
        new_window_info = []
        new_boundaries = self.get_short_window_boundaries()
        if self.latest_timestamp is None:
            new_window_info = None
        elif window_boundaries != new_boundaries or len(window_values) != len(window_boundaries):
            new_window_info = None
        else:
            for i in range(0, len(window_boundaries)):
                new_window_info.append((window_boundaries[i], window_values[i],))
        self.window_values_mutex.acquire()
        try:
            self.window_values = new_window_info
        finally:
            self.window_values_mutex.release()

    def get_window_values(self):
        """
        Returns a list of all values where, the latest window's info is in the first element
        :return: A list of tuples like (window_ending_boundary, value)
        """
        self.window_values_mutex.acquire()
        try:
            if self.window_values is None:
                return None
            return self.window_values.copy()
        finally:
            self.window_values_mutex.release()

    def get_average_on_all_values(self):
        return mean([v[1] for v in self.get_window_values()])

    def calculate_new_window_values_and_boundaries(self):
        """
        When called, the object should return a tuple of two lists like (new_values, new_boundaries)
        :return:
        """
        pass


class AverageWindowBlockCount(AverageWindowMetric):
    def calculate_new_window_values_and_boundaries(self):
        """
        When called, the object should return a tuple of two lists like (new_values, new_boundaries)
        :return:
        """
        # get boundary values
        boundaries = self.get_short_window_boundaries()
        # get data from database to fill data
        values = []
        mine_db_handler = mine_db.MineDatabaseHandler(EXECUTION_CONFIGS.db_user, EXECUTION_CONFIGS.db_password)
        for i in range(0, len(boundaries)):
            end_timestamp = boundaries[i]
            begin_timestamp = end_timestamp - self.short_window_length
            values.append(len(mine_db_handler.get_blocks_between(begin_timestamp,end_timestamp)))
        return boundaries, values


class RecentHistoryStatistics:
    def __init__(self):
        #
        # Each member is a tuple window average window metric container
        average_window_metric_containers = [
            AverageWindowBlockCount(short_window_length_seconds=size_in_seconds(days=1),
                                    large_window_length_seconds=size_in_seconds(days=10)),
            AverageWindowBlockCount(short_window_length_seconds=size_in_seconds(days=1),
                                    large_window_length_seconds=size_in_seconds(days=50)),
            AverageWindowBlockCount(short_window_length_seconds=size_in_seconds(days=1),
                                    large_window_length_seconds=size_in_seconds(days=250))
        ]


class Analyzer(TickPerformer):
    def __init__(self):
        """
        A singleton class that is the analyzer
        """
        super().__init__()
        self.tick_duration = calculate_tick_duration_from_sleep_duration(EXECUTION_CONFIGS.analyzer_sleep_duration)

    def run(self, should_stop):
        while True:
            if should_stop():
                break
            sleep(self.tick_duration)
            current_timestamp = get_clock().read_timestamp_of_now()
            logger('analyzer').debug("Updating analytics at timestamp {0}.".format(current_timestamp))

    def post_run(self):
        logger('analyzer').info("Analyzer is terminating.")

    def is_a_daemon(self):
        return False
